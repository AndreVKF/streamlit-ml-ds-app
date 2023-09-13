import datetime as dt

from aws.client import createSession
from etl import loadWorkedMoviesDatabase, loadXbgPJMERegressionObject

if __name__ == '__main__':
    startTime = dt.datetime.now()

    awsSession = createSession()

    print(f'init etl!!')
    loadWorkedMoviesDatabase(awsSession=awsSession)
    loadXbgPJMERegressionObject(awsSession=awsSession)
    print(f'finished etl. Process time {dt.datetime.now() - startTime} !!')
