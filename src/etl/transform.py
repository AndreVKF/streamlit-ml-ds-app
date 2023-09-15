import ast
import re

import numpy as np
import pandas as pd
import xgboost as xgb

from etl.extract import getCreditsDb, getMoviesRawDf, getPJMEHourlyRawDf, getDivorceData

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

from nltk.stem.porter import PorterStemmer

def extractAttributeFromStrListObj(obj: str, attrName: str, limit: int = None):
    if not isinstance(obj, str):
        return

    objList = ast.literal_eval(obj)

    returnList = []

    for idx, objItem in enumerate(objList):
        if attrName not in objItem:
            continue

        if isinstance(limit, int) and not limit > idx:
            break

        returnList.append(str(objItem[attrName]).replace(" ", "").lower())

    return returnList


def getMainCrewMembersFromStrListObj(obj: str, jobs: list = ['Writer', 'Director']):
    if not isinstance(obj, str):
        return

    objList = ast.literal_eval(obj)

    returnList = []

    for objItem in objList:
        if len(returnList) == len(jobs):
            break

        job = objItem['job']

        if job not in jobs:
            continue

        returnList.append(objItem['name'].replace(" ", "").lower())

    return returnList


def appendTags(row: pd.Series):
    tagList = []

    for item in row:
        tagList.extend(item)

    return ' '.join(tagList)


def stem(text, stem):
    y = []

    for word in text.split():
        y.append(stem(word))

    return " ".join(y)


def createMoviesDatabase():
    creditsDb = getCreditsDb()
    moviesRawDb = getMoviesRawDf()

    r = re.compile("^[a-zA-Z0-9]")
    movieTitles = moviesRawDb['title'].to_list()
    movieTitles = filter(r.match, movieTitles)

    moviesRawDb = moviesRawDb.loc[moviesRawDb['title'].isin(movieTitles)]
    moviesRawDb = moviesRawDb.loc[moviesRawDb['vote_count'] > 400]
    cleanMovieDb = moviesRawDb.merge(creditsDb, how='left', on='title')

    return cleanMovieDb


def createAnalyticsMoviesDatabase(movieDb: pd.DataFrame):
    pickedColumns = ['title', 'genres', 'keywords', 'cast', 'crew']
    movieDbCp = movieDb.copy()

    movieDbCp = movieDbCp[pickedColumns]

    movieDbCp.loc[:, 'genres'] = movieDbCp['genres'].apply(
        lambda x: extractAttributeFromStrListObj(obj=x, attrName='name')
    )
    movieDbCp.loc[:, 'keywords'] = movieDbCp['keywords'].apply(
        lambda x: extractAttributeFromStrListObj(obj=x, attrName='name')
    )
    movieDbCp.loc[:, 'cast'] = movieDbCp['cast'].apply(
        lambda x: extractAttributeFromStrListObj(obj=x, attrName='name', limit=5)
    )
    movieDbCp.loc[:, 'crew'] = movieDbCp['crew'].apply(lambda x: getMainCrewMembersFromStrListObj(obj=x))

    movieDbCp['tags'] = movieDbCp[['genres', 'keywords', 'cast', 'crew']].apply(lambda row: appendTags(row), axis=1)

    ps = PorterStemmer()
    movieDbCp['tags'] = movieDbCp['tags'].apply(lambda x: stem(x, stem=ps.stem))

    return movieDbCp


def createMovieDbSimilarityVectors(movieDb: pd.DataFrame):
    movieDbDist = movieDb[['title', 'tags']].copy()

    cv = CountVectorizer(max_features=10000, stop_words='english')
    cv.fit_transform(movieDbDist['tags']).toarray().shape

    vectors = cv.fit_transform(movieDbDist['tags']).toarray()

    similarityVectors = cosine_similarity(vectors)

    return similarityVectors


def createPJMETrainTestDf():
    pjmeHourlyRawDf = getPJMEHourlyRawDf()
    
    #### TRANSFORM ####
    pjmeHourlyRawDf.rename(columns={'Datetime': 'datetime'}, inplace=True)
    pjmeHourlyRawDf['datetime'] = pd.to_datetime(pjmeHourlyRawDf['datetime'])
    pjmeHourlyRawDf.set_index(keys=['datetime'], inplace=True)

    #### FEATURE CREATION ####
    pjmeHourlyRawDf['hour'] = pjmeHourlyRawDf.index.hour
    pjmeHourlyRawDf['day'] = pjmeHourlyRawDf.index.day
    pjmeHourlyRawDf['month'] = pjmeHourlyRawDf.index.month
    pjmeHourlyRawDf['year'] = pjmeHourlyRawDf.index.year
    pjmeHourlyRawDf['quarter'] = pjmeHourlyRawDf.index.quarter
    pjmeHourlyRawDf['dayofyear'] = pjmeHourlyRawDf.index.dayofyear

    pjmeTrain = pjmeHourlyRawDf.loc[pjmeHourlyRawDf.index < '2015-01-01']
    pjmeTest = pjmeHourlyRawDf.loc[pjmeHourlyRawDf.index >= '2015-01-01']

    return pjmeTrain, pjmeTest
    
def createXbgRegressionTrainObject():
    pjmeHourlyRawDf = getPJMEHourlyRawDf()
    pjmeTrain, pjmeTest = createPJMETrainTestDf()
    
    FEATURES = ['hour', 'day', 'month', 'year', 'quarter', 'dayofyear']
    TARGET = ['PJME_MW']

    X_train = pjmeTrain[FEATURES]
    y_train = pjmeTrain[TARGET]

    X_test = pjmeTest[FEATURES]
    y_test = pjmeTest[TARGET]
    
    regressionModel = xgb.XGBRegressor(n_estimators=10000, early_stopping_rounds=50, learning_rate=0.01)
    regressionModel.fit(
        X_train,
        y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        verbose=100)
    
    fi = pd.DataFrame(data=regressionModel.feature_names_in_, index=regressionModel.feature_importances_, columns=['importance'])
    fi.sort_index(inplace=True)
    
    xbgObject = {
        'raw': pjmeHourlyRawDf,
        'X_train': X_train,
        'y_train': y_train,
        'X_test': X_test,
        'y_test': y_test,
        'model': regressionModel,
        'featureImportance': fi
    }
    
    return xbgObject

def createDivorceDataModel():
    
    divorceDataDf = getDivorceData()
    
    X = divorceDataDf.loc[:, ~divorceDataDf.columns.isin(['Divorce'])]
    standardScaler = StandardScaler()
    X_normalized = standardScaler.fit_transform(X)

    y = divorceDataDf.loc[:, divorceDataDf.columns.isin(['Divorce'])]

    X_train, x_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.2, random_state=0)

    logisticRegression = LogisticRegression(random_state=0)
    logisticRegression.fit(X=X_train, y=y_train)

    fi = pd.DataFrame(data={'feature': X.columns, 'value': np.abs(logisticRegression.coef_[0])})
    fi.sort_values(by='value', ascending=False, inplace=True)

    mostImportantFeatures = list(fi['feature'][:11].values)
    mostImportantFeatures.remove('Q52')
    
    ######### REDUCED DATA #########
    reducedData = divorceDataDf[[*mostImportantFeatures, *['Divorce']]]

    X = reducedData.loc[:, ~reducedData.columns.isin(['Divorce'])]
    standardScaler = StandardScaler()
    X_normalized = standardScaler.fit_transform(X)

    y = reducedData.loc[:, reducedData.columns.isin(['Divorce'])]

    logisticRegression = LogisticRegression(random_state=0)
    logisticRegression.fit(X=X_normalized, y=y)
    
    divorceMlObject = {
        'model': logisticRegression,
        'scaler': standardScaler
    }
    
    return divorceMlObject