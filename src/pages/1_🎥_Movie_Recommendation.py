import boto3
import os
import pickle
import ast

import pandas as pd
import streamlit as st
import numpy as np

from common.functions import setPageHeader

setPageHeader()

from urllib.request import urlopen
from common.constants import AWS_BUCKET
from common.styles import secondaryBackgroundColor
from aws.client import createSession
from aws.s3 import generatePresignedUrl

AWS_BUCKET_PREFIX = 'worked'

AWS_SESSION = createSession()


######## LOAD DATA ########
@st.cache_resource(show_spinner=False)
def getSimilarityVectors():
    s3Key = f'{AWS_BUCKET_PREFIX}/similarityVectors.pkl'
    url = generatePresignedUrl(awsSession=AWS_SESSION, s3Key=s3Key)

    similarityVectors = pickle.load(urlopen(url))

    return similarityVectors


@st.cache_resource(show_spinner=False)
def getMovieDb():
    s3Key = f'{AWS_BUCKET_PREFIX}/movieDb.csv'
    url = generatePresignedUrl(awsSession=AWS_SESSION, s3Key=s3Key)
    movieDb = pd.read_csv(url)

    return movieDb


@st.cache_resource(show_spinner=False)
def getMovieDbAnalytics():
    s3Key = f'{AWS_BUCKET_PREFIX}/movieDbAnalytics.csv'
    url = generatePresignedUrl(awsSession=AWS_SESSION, s3Key=s3Key)
    movieDbAnalytics = pd.read_csv(url)

    return movieDbAnalytics


######## FUNC ########
@st.cache_resource
def getMovieTitles(movieDb: pd.DataFrame):
    titlesList = movieDb['title'].drop_duplicates().to_list()
    titlesList.sort()

    return titlesList


def getRecommendations(title: str, similarityVectors: np.ndarray, movieDb: pd.DataFrame, nRecommendations: int = 10):
    movieIndex = movieDb.loc[movieDb['title'] == title].index[0]
    distances = similarityVectors[movieIndex]
    similarMoviesDf = (
        pd.DataFrame(distances, columns=['cosin_similarity'])
        .sort_values(by=['cosin_similarity'], ascending=False)
        .iloc[1:nRecommendations, :]
    ).index

    st.session_state['recommendationMoviesIndexes'] = list(similarMoviesDf)


def getMovieDirector(crewListStr: str):
    crewList = ast.literal_eval(crewListStr)

    if not bool(crewList) or len(crewList) == 0:
        return ''

    for item in crewList:
        if item['job'] == 'Director':
            return item['name']


def getMovieCast(castListStr: str):
    fullCastList = ast.literal_eval(castListStr)

    if not bool(fullCastList) or len(fullCastList) == 0:
        return ''

    summarizedCastList = []
    for idx, item in enumerate(fullCastList):
        summarizedCastList.append(item["name"])

        if idx >= 5:
            break

    return summarizedCastList


def getGenresList(genreListStr: str):
    genresFullList = ast.literal_eval(genreListStr)

    if not bool(genresFullList) or len(genresFullList) == 0:
        return ''

    genresList = [genreObj['name'] for genreObj in genresFullList]

    return genresList


def createGenreTags(tags: list):
    if not bool(tags) or len(tags) == 0:
        return ''

    genreTags = f"""<div style="width: 100%; display: flex; align-items: center; gap: 8px;">{''.join([f'<span style="border: 1px solid {secondaryBackgroundColor}; border-radius: 4px; padding: 8px; font-size: 18px;">{tag}</span>' for tag in tags])}</div>"""

    return genreTags


def createMovieCard(title: str, releaseDate: str, director: str, cast: list, overview: str, genres: list):
    st.markdown(
        body=f"""
                <div style="width: 100%; display: flex; flex-direction: column; justify-content: start; gap: 12px; margin-bottom: 12px;">
                <span style="font-size: 40px; font-weight: 600;">{title}<span>
                {f"<p>Released on: {releaseDate}</p>" if bool(releaseDate) else ""}
                {f"<p>Director: {director}</p>" if bool(director) else ""}
                {f"<p>Cast: {', '.join(cast)}</p>" if bool(cast) else ""}
                {f"<p>{overview}</p>" if bool(overview) else ""}
                {createGenreTags(genres)}
                </div>""",
        unsafe_allow_html=True,
    )


######## SESSION CONTROL ########
def fullReset():
    if 'recommendationMoviesIndexes' in st.session_state:
        del st.session_state['recommendationMoviesIndexes']


######## APP ########

st.header("Movie Recommendation 🎥")

with st.spinner('Downloading model and data. Please wait.'):
    similarityVectors = getSimilarityVectors()
    movieDb = getMovieDb()
    movieDbAnalytics = getMovieDbAnalytics()

    movieTitles = getMovieTitles(movieDb=movieDb)

with st.expander(label='', expanded=True):
    st.header("Please select a movie")

    title = st.selectbox(label="Movie Titles", options=movieTitles, label_visibility='visible', on_change=fullReset)

    st.button(
        "Submit",
        on_click=getRecommendations,
        kwargs={
            'title': title,
            'similarityVectors': similarityVectors,
            'movieDb': movieDbAnalytics,
        },
    )


if 'recommendationMoviesIndexes' in st.session_state:
    recommendationMoviesDf = movieDb.iloc[st.session_state['recommendationMoviesIndexes'], :]

    for idx, row in recommendationMoviesDf.iterrows():
        title = row['title']
        genres = getGenresList(row['genres'])
        releaseDate = row['release_date'] if bool(row['release_date']) else ''
        overview = row['overview'] if bool(row['overview']) else ''

        director = getMovieDirector(crewListStr=row['crew'])
        cast = getMovieCast(castListStr=row['cast'])

        with st.expander(label=title, expanded=False):
            createMovieCard(title, releaseDate, director, cast, overview, genres)
