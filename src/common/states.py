import streamlit as st

def fullStateReset():
    for key in st.session_state:
        del st.session_state[key]