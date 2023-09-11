import ast

import pandas as pd
import re

from etl.extract import getCreditsDb, getMoviesRawDf

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    cleanMovieDb = moviesRawDb.merge(creditsDb, on='title')

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
