import streamlit as st

from common.functions import setPageHeader

setPageHeader()

st.header("Machine Learning and Data Science Demo App 🤖")

with st.expander(label='', expanded=True):
    st.markdown(body="""
                # Machine Learning and Data Science App Sample
                
                Present ML and DS applications in a reduced form.
                
                Please select an option on the sidebar.
                """)


