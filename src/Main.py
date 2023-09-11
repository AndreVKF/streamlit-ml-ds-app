import streamlit as st

from aws.client import createSession

from common.functions import setPageHeader

setPageHeader()

st.header("Machine Learning and Data Science Demo App 🤖")

st.sidebar.info("Select an option above!")

awsSession = createSession()
