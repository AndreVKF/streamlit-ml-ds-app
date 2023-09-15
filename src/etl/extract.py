import os

import pandas as pd

DATA_PATH = os.path.join(os.getcwd(), "data", "raw")


def getCreditsDb():
    creditsDbFileName = 'credits.csv'
    creditsDbDf = pd.read_csv(os.path.join(DATA_PATH, creditsDbFileName))

    return creditsDbDf


def getMoviesRawDf():
    moviesRawFileName = 'movies_db.csv'
    moviesRawDf = pd.read_csv(os.path.join(DATA_PATH, moviesRawFileName))

    return moviesRawDf


def getPJMEHourlyRawDf():
    pjmeHourlyFileName = 'PJME_hourly.csv'
    pjmeHourlyRawDf = pd.read_csv(os.path.join(DATA_PATH, pjmeHourlyFileName))
    
    return pjmeHourlyRawDf

def getDivorceData():
    divorceDataFileName = 'divorce_data.csv'
    divorceDataRawDf = pd.read_csv(os.path.join(DATA_PATH, divorceDataFileName), sep=';')
    
    return divorceDataRawDf