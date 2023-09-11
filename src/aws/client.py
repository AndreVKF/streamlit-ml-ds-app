import boto3
import streamlit as st


@st.cache_resource
def createSession():
    session = boto3.Session(
        aws_access_key_id=st.secrets['aws']['access_key'],
        aws_secret_access_key=st.secrets['aws']['secret_key'],
        region_name='us-east-1',
    )

    return session
