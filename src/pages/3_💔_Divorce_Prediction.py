import pickle
from urllib.request import urlopen
import plotly.graph_objects as go

import streamlit as st

import streamlit as st
from common.functions import setPageHeader
setPageHeader()

from aws.client import createSession
from aws.s3 import generatePresignedUrl

AWS_BUCKET_PREFIX = 'worked'

AWS_SESSION = createSession()

QUESTIONS = [
    "When we need it, we can take our discussions with my spouse from the beginning and correct it",
    "We're just starting a discussion before I know what's going on",
    "Our discussions often occur suddenly",
    "I think that one day in the future, when I look back, I see that my spouse and I have been in harmony with each other",
    "Sometimes I think it's good for me to leave home for a while",
    "When I discuss, I remind my spouse of her/his inadequacy",
    "Most of our goals for people (children, friends, etc.) are the same",
    "I have nothing to do with what I've been accused of",
    "When I talk to my spouse about something, my calm suddenly breaks",
    "I know we can ignore our differences, even if things get hard sometimes",
]

INVERSE_RESPONSE_COLS = [0, 3, 6, 9]
######## LOAD DATA ########
@st.cache_resource(show_spinner=False)
def getDivorceMlObj():
    s3Key = f'{AWS_BUCKET_PREFIX}/divorceMlObj.pkl'
    url = generatePresignedUrl(awsSession=AWS_SESSION, s3Key=s3Key)

    divorceMlObj = pickle.load(urlopen(url))

    return divorceMlObj

DIVORCE_ML_MODEL = getDivorceMlObj()

######## FUNCTIONS ########
@st.cache_data
def createDivorceGaugeChart(divorceProbability: float):

    adjDivorceProb = divorceProbability * 100
    
    if adjDivorceProb <= 30:
        barColor = '#a3e635'
    elif adjDivorceProb > 30 and adjDivorceProb < 50:
        barColor = '#d1d5db'
    else:
        barColor = '#f87171'

    fig = go.Figure(
        data=[
            go.Indicator(
                mode="gauge+number",
                value=adjDivorceProb,
                number = {'suffix': "%"},
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': 'Divorce Prediction Probability'},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': barColor},
                    'threshold': {
                        'line': {'color': '#475569', 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            )
        ]
    )
    
    return fig
    
######## FUNCTIONS ########
def makePredictionState():
    st.session_state['makePrediction'] = True
    pass

def resetPredictionState():
    if 'makePrediction' in st.session_state:
        del st.session_state['makePrediction']

def getDivorceProbability(responseList):
    model = DIVORCE_ML_MODEL['model']
    scaler = DIVORCE_ML_MODEL['scaler']
    
    scaledResponses = scaler.transform([responseList])
    print(scaledResponses)
    predictionsProbability = model.predict_proba(scaledResponses)
    
    return predictionsProbability[0][1]

def getAdjustedResponseList(responseList):
    adjResponseList = responseList.copy()
    
    for questionNumber in INVERSE_RESPONSE_COLS:
        questionVl = responseList[questionNumber]
        
        if questionVl == 0:
            adjValue = 4
        elif questionVl == 1:
            adjValue = 3
        elif questionVl == 2:
            adjValue = 2
        elif questionVl == 3:
            adjValue = 1
        elif questionVl == 4:
            adjValue = 0
            
        adjResponseList[questionNumber] = adjValue

    return adjResponseList

######## APP ########
st.header('Divorce Prediction 💔')

responseList = []
with st.expander(label='', expanded=True):
    st.header('Please respond to all questions (0~4)')

    questionCols = st.columns(2)
    for idx, question in enumerate(QUESTIONS):
        col = 0 if idx % 2 == 0 else 1
        
        with questionCols[col]:
            inputRes = st.number_input(label=question, min_value=0, max_value=4, key=f'Q{idx}', on_change=resetPredictionState)
            responseList.append(inputRes)
            
    submitBtn = st.button(label='Submit', on_click=makePredictionState)
    
if submitBtn and 'makePrediction' in st.session_state and bool(st.session_state['makePrediction']):
    adjResponseList = getAdjustedResponseList(responseList)
    divorceProbability = getDivorceProbability(adjResponseList)
    
    with st.expander(label='', expanded=True):
        st.header('Prediction')
        
        fig = createDivorceGaugeChart(divorceProbability=divorceProbability)
        
        st.plotly_chart(figure_or_data=fig, use_container_width=True)

with st.expander(label='Methodology', expanded=False):
    st.header('Methodology')
    
    st.markdown(body="""
                ### Logistic Regression
                
                Logistic regression is a type of statistic model capable of creating a probability estimate of an event to occur.
                
                It uses a function (most common sigmoid) to create a decision boundary, setting a threshold to predict wheter an event is bound to happen.
                """)
    
    imageCols = st.columns([0.2, 0.6, 0.2])
    with imageCols[1]:
        st.image("assets/images/logistic_regression.png")
    
    st.markdown(body="""
                ### Data 
                
                Divorce Dataset (https://www.kaggle.com/datasets/andrewmvd/divorce-prediction)
                
                """)
    