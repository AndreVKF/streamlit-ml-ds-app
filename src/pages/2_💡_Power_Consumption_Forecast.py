import pickle

import streamlit as st
from common.functions import setPageHeader
setPageHeader()

import datetime as dt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from sklearn.metrics import mean_squared_error
from urllib.request import urlopen
from aws.client import createSession
from aws.s3 import generatePresignedUrl

AWS_BUCKET_PREFIX = 'worked'

AWS_SESSION = createSession()

######## LOAD DATA ########
@st.cache_resource(show_spinner=False)
def getxbgPJMEObj():
    s3Key = f'{AWS_BUCKET_PREFIX}/xbgPJMEObj.pkl'
    url = generatePresignedUrl(awsSession=AWS_SESSION, s3Key=s3Key)

    xbgPJMEObj = pickle.load(urlopen(url))

    return xbgPJMEObj


######## FUNCTIONS ########
@st.cache_data
def createFeatures(rawDf):
    pjmeHourlyRawDf = rawDf.copy()
        
    pjmeHourlyRawDf.rename(columns={'Datetime': 'datetime'}, inplace=True)
    pjmeHourlyRawDf['datetime'] = pd.to_datetime(pjmeHourlyRawDf['datetime'])
    pjmeHourlyRawDf.set_index(keys=['datetime'], inplace=True)
    pjmeHourlyRawDf.sort_index(inplace=True)
    
    pjmeHourlyRawDf['hour'] = pjmeHourlyRawDf.index.hour
    pjmeHourlyRawDf['day'] = pjmeHourlyRawDf.index.day
    pjmeHourlyRawDf['month'] = pjmeHourlyRawDf.index.month
    pjmeHourlyRawDf['year'] = pjmeHourlyRawDf.index.year
    pjmeHourlyRawDf['quarter'] = pjmeHourlyRawDf.index.quarter
    pjmeHourlyRawDf['dayofyear'] = pjmeHourlyRawDf.index.dayofyear
    
    return pjmeHourlyRawDf

@st.cache_data
def getPredictions(_model, X_test):
    predictions = _model.predict(X=X_test)
    return predictions

@st.cache_data
def createPjmeRawDataChart(pjmeRawDf):
    
    fig = go.Figure(data=[
        go.Scatter(
            x=pjmeRawDf.index,
            y=pjmeRawDf['PJME_MW']
        )
    ])
    
    fig.update_layout(title="PJM East Cost Power Consumption", yaxis_title='MW')

    return fig

@st.cache_data
def createPjmeSplitDataChart(y_train: pd.DataFrame, y_test: pd.DataFrame):
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=y_train.index,
            y=y_train['PJME_MW'],
            name='Train Data',
            marker=dict(color="#475569", size=5)
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=y_test.index,
            y=y_test['PJME_MW'],
            name='Test Data',
            marker=dict(color="#0284c7", size=5)
        )
    )
    
    fig.add_vline(x=dt.date(2015, 1, 1), line_dash='dash')

    fig.update_layout(
        title="Train/Test Data Split",
        yaxis_title="MW"
    )

    return fig

@st.cache_data
def createOneWeekData(y_test: pd.DataFrame):

    oneWeekData = y_test.loc[(y_test.index >= '2018-01-01') & (y_test.index <= '2018-01-07')]
    fig = px.scatter(oneWeekData, x=oneWeekData.index, y=['PJME_MW'], title='One Week Data')
    
    fig.update_layout(
        yaxis_title="MW"
    )
    
    return fig

@st.cache_data
def createForecastChart(y_train: pd.DataFrame, y_test: pd.DataFrame):
    
    fig = go.Figure()

    fig.add_trace(
            go.Scatter(
                x=y_train.index,
                y=y_train['PJME_MW'],
                name='Train Data',
                marker=dict(color="#475569", size=5)
            )
    )

    fig.add_trace(
            go.Scatter(
                x=y_test.index,
                y=y_test['PJME_MW'],
                name='Test Data',
                marker=dict(color="#0284c7", size=5)
            )
    )

    fig.add_trace(
            go.Scatter(
                x=y_test.index,
                y=y_test['prediction'],
                name='Prediction',
                marker=dict(color="#fda4af", size=5)
            )
    )

    fig.add_vline(x=dt.date(2015, 1, 1), line_dash='dash')

    fig.update_layout(
        title="Forecast",
        yaxis_title="MW"
    )
    
    return fig

@st.cache_data
def oneWeekPrediction(y_test: pd.DataFrame):
    
    oneWeekData = y_test.loc[(y_test.index >= '2018-01-01') & (y_test.index <= '2018-01-07')]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=oneWeekData.index,
            y=oneWeekData['PJME_MW'],
            name='Test Data',
            mode='markers',
            marker=dict(color='#0284c7', size=5)
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=oneWeekData.index,
            y=oneWeekData['prediction'],
            name='Forecast',
            mode='markers',
            marker=dict(color='#fda4af', size=5)
        )
    )
    
    
    fig.update_layout(
        title="One Week Forecast",
        yaxis_title="MW"
    )
    
    return fig
    
@st.cache_data
def createFeatureImportanceChart(featureImportance: pd.DataFrame):
    fi = featureImportance.copy()
    fi.sort_index(inplace=True)

    fig = px.bar(fi, x=fi.index, y='importance', color=fi.index)

    return fig
    
######## APP ########
st.header('PJM East Coast Power Consumption Forecast 💡')

with st.spinner('Downloading model and data. Please wait.'):
    xbgPJMEObj = getxbgPJMEObj()

pjmeRawDf = createFeatures(xbgPJMEObj['raw'])

X_train = xbgPJMEObj['X_train'].sort_index()
y_train = xbgPJMEObj['y_train'].sort_index()
X_test = xbgPJMEObj['X_test'].sort_index()
y_test = xbgPJMEObj['y_test'].sort_index()
model = xbgPJMEObj['model']
featureImportance = xbgPJMEObj['featureImportance']

with st.expander(label='', expanded=True):
    st.header("About the Data")
    st.markdown(body="""
                PJM Hourly Energy Consumption Data
                PJM Interconnection LLC (Pennsylvania-New Jersey-Maryland Interconnection) is a regional transmission organization (RTO) in the United States. It is part of the Eastern Interconnection grid operating an electric transmission system serving all or parts of Delaware, Illinois, Indiana, Kentucky, Maryland, Michigan, New Jersey, North Carolina, Ohio, Pennsylvania, Tennessee, Virginia, West Virginia, and the District of Columbia.

                The hourly power consumption data comes from PJM's website and are in megawatts (MW).

                Selected data covers the East Cost regions.
                """)
    
    st.plotly_chart(figure_or_data=createPjmeRawDataChart(pjmeRawDf=pjmeRawDf), use_container_width=True)


with st.expander(label='',expanded=True):
    st.header("Methodology")
    st.markdown(body="""
                eXtreme Gradient Boosting (XGBoost) is a scalable and improved version of the gradient boosting algorithm (terminology alert) designed for efficacy, computational speed and model performance.
                
                In ML, Boosting is a sequential ensemble learning technique to convert a weak hypothesis or weak learners into strong learners to increase the accuracy of the model.
                
                XGBoost uses ensemble learning in order to boost it's learning performance. Ensemble learning is a process in which decisions from multiple machine learning models are combined to reduce errors and improve prediction when compared to a Single ML model. Then the maximum voting technique is used on aggregated decisions to deduce the final prediction. 
                """)
    imageCols = st.columns([0.2, 0.6, 0.2])
    with imageCols[1]:
        st.image(image='assets/images/ensemble.png')
    
with st.expander(label='',expanded=True):
    st.header("Data Handling")
    
    st.markdown(body="### Train/Test")
    st.markdown("All records prior to 2015 were used for model training and the remaining data were used for model testing.")

    st.plotly_chart(figure_or_data=createPjmeSplitDataChart(y_test=y_test, y_train=y_train), use_container_width=True)
    
    st.markdown(body="### Feature Creation")
    st.markdown("Features created by splicing the datetime feature into hour, day, month, year, quarter and dayofyear.")
    
    features = ['hour', 'day', 'month', 'year', 'quarter', 'dayofyear']
    boxPlotTabs = st.tabs([f'Boxplot {feature}' for feature in features])

    for idx, feature in enumerate(features):
        with boxPlotTabs[idx]:
            boxPlot = px.box(pjmeRawDf, x=feature, y='PJME_MW', color=feature)
            st.plotly_chart(figure_or_data=boxPlot, use_container_width=True)

    st.markdown(body="### One Week Data")
    st.plotly_chart(figure_or_data=createOneWeekData(y_test=y_test), use_container_width=True)
    
with st.expander(label='',expanded=True):
    st.header("Forecasting")
    
    y_test['prediction'] = getPredictions(_model=model, X_test=X_test)
    
    st.plotly_chart(figure_or_data=createForecastChart(y_train=y_train, y_test=y_test), use_container_width=True)
    st.plotly_chart(figure_or_data=oneWeekPrediction(y_test=y_test), use_container_width=True)
    
with st.expander(label='',expanded=True):
    st.header("Feature Importance")
    st.markdown("Datetime features most likely overlap themselves. If 'month' was removed most like 'quarter' will gain more importance.")
    
    st.plotly_chart(figure_or_data=createFeatureImportanceChart(featureImportance=featureImportance), use_container_width=True)