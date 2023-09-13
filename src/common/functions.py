from numbers import Number

import streamlit as st


def setPageHeader():
    st.set_page_config(page_title="ML-DS", page_icon="🤖", layout="wide")

def adjustValueToString(value: Number):
    SUFFIX_OPTIONS_LIST = [
        {
            'suffix': '',
            'value': 1
        },
        {
            'suffix': 'K',
            'value': 1000
        },
        {
            'suffix': 'M',
            'value': 1000000
        },
        {
            'suffix': 'B',
            'value': 1000000
        },
        {
            'suffix': 'T',
            'value': 1000000000
        }
    ]
    checkValue = value
    suffix = ''
    
    if value < 999:
        return f'{value:,.2f}'
    
    for suffixOption in SUFFIX_OPTIONS_LIST:
        if checkValue < 1:
            break
        
        suffix = suffixOption['suffix']
        baseValue = suffixOption['value']
        
        checkValue = checkValue / baseValue

    adjValue = f'{value / baseValue:,.2f}{suffix}'
    
    return adjValue