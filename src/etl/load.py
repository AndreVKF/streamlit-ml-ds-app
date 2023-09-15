import os
import pickle
import boto3

import pandas as pd

from aws.s3 import uploadFile
from etl.transform import createMoviesDatabase, createMovieDbSimilarityVectors, createAnalyticsMoviesDatabase, createXbgRegressionTrainObject, createDivorceDataModel

DATA_PATH = os.path.join(os.getcwd(), "data", "worked")
BUCKET_FOLDER = 'worked'


def loadedInfoPrint(filename: str):
    print(f'Loaded {filename}!!')


def loadWorkedMoviesDatabase(awsSession: boto3.Session):
    movieDb = createMoviesDatabase()
    movieDbAnalytics = createAnalyticsMoviesDatabase(movieDb=movieDb)
    similarityVectors = createMovieDbSimilarityVectors(movieDb=movieDbAnalytics)

    # store data
    movieDbFilename = 'movieDb.csv'
    movieDbPath = os.path.join(DATA_PATH, movieDbFilename)
    movieDb.to_csv(movieDbPath)
    uploadFile(awsSession=awsSession, filePath=movieDbPath, s3Key=f'{BUCKET_FOLDER}/{movieDbFilename}')
    loadedInfoPrint(filename=movieDbFilename)

    movieDbAnalyticsFilename = 'movieDbAnalytics.csv'
    movieDbAnalyticsPath = os.path.join(DATA_PATH, movieDbAnalyticsFilename)
    movieDbAnalytics.to_csv(movieDbAnalyticsPath)
    uploadFile(
        awsSession=awsSession, filePath=movieDbAnalyticsPath, s3Key=f'{BUCKET_FOLDER}/{movieDbAnalyticsFilename}'
    )
    loadedInfoPrint(filename=movieDbAnalyticsFilename)

    similarityVectorsFilename = 'similarityVectors.pkl'
    similarityVectorsPath = os.path.join(DATA_PATH, similarityVectorsFilename)
    with open(similarityVectorsPath, 'wb') as f:
        pickle.dump(similarityVectors, f)
    uploadFile(
        awsSession=awsSession, filePath=similarityVectorsPath, s3Key=f'{BUCKET_FOLDER}/{similarityVectorsFilename}'
    )
    loadedInfoPrint(filename=similarityVectorsFilename)

    return

def loadXbgPJMERegressionObject(awsSession: boto3.Session):
    xbgPJMEObj = createXbgRegressionTrainObject()
    
    xbgPJMEObjFilename = 'xbgPJMEObj.pkl'
    xbgPJMEObjPath = os.path.join(DATA_PATH, xbgPJMEObjFilename)
    with open(xbgPJMEObjPath, 'wb') as f:
        pickle.dump(xbgPJMEObj, f)
        
    uploadFile(
        awsSession=awsSession, filePath=xbgPJMEObjPath, s3Key=f'{BUCKET_FOLDER}/{xbgPJMEObjFilename}'
    )
    loadedInfoPrint(filename=xbgPJMEObjFilename)
    
    return

def loadDiverceMlObject(awsSession: boto3.Session):
    divorceMlObj = createDivorceDataModel()
    
    divorceMlObjFilename = 'divorceMlObj.pkl'
    divorceMlObjPath = os.path.join(DATA_PATH, divorceMlObjFilename)
    with open(divorceMlObjPath, 'wb') as f:
        pickle.dump(divorceMlObj, f)
        
    uploadFile(
        awsSession=awsSession, filePath=divorceMlObjPath, s3Key=f'{BUCKET_FOLDER}/{divorceMlObjFilename}'
    )
    loadedInfoPrint(filename=divorceMlObjFilename)
    
    return