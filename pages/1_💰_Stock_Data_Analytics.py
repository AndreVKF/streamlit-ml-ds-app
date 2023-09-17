import streamlit as st
from common.functions import setPageHeader, adjustValueToString
setPageHeader()

import datetime as dt
import pandas as pd
import plotly.graph_objects as go

from common.states import fullStateReset
from services.Yahoo_Fin import Yahoo_Fin

STOCK_OPTIONS_LIST = [
    {
        'id': 1,
        'company': 'Apple Inc.',
        'ticker': 'AAPL'
    },
    {
        'id': 2,
        'company': 'Microsoft Corporation',
        'ticker': 'MSFT'
    },
    {
        'id': 3,
        'company': 'Alphabet Inc.',
        'ticker': 'GOOG'
    },
    {
        'id': 4,
        'company': 'Amazon.com, Inc',
        'ticker': 'AMZN'
    },
    {
        'id': 5,
        'company': 'Tesla, Inc.',
        'ticker': 'TSLA'
    },
    {
        'id': 6,
        'company': 'Coca-Cola Company',
        'ticker': 'KO'
    },
    {
        'id': 7,
        'company': 'Netflix, Inc.',
        'ticker': 'NFLX'
    }
]

SELECT_STOCK_OPTIONS = [stockOption['company'] for stockOption in STOCK_OPTIONS_LIST]


######## FUNC ########
def getTickerFromCompanyName(company: str):
    for stockOption in STOCK_OPTIONS_LIST:
        if company == stockOption['company']:
            return stockOption['ticker']

    return ''

def adjustStatsValuationDf(statsValuationDf: pd.DataFrame):
    adjStatsValuationDf = statsValuationDf.copy()
    adjStatsValuationDf.columns = ['index', 'value']
    
    return adjStatsValuationDf

def adjustPxDataDf(pxData: pd.DataFrame, iniDateStr: str, endDateStr: str):
    iniDate = dt.datetime.strptime(iniDateStr, '%Y-%m-%d')
    endDate = dt.datetime.strptime(endDateStr, '%Y-%m-%d')
    
    chartDf = pxData.copy()
    chartDf = chartDf.loc[(chartDf.index >= iniDate) & (chartDf.index <= endDate)]
    
    return chartDf

@st.cache_data
def createTimeSeriesChart(pxData: pd.DataFrame, iniDateStr: str, endDateStr: str):
    chartDf = adjustPxDataDf(pxData, iniDateStr, endDateStr)
    
    fig = go.Figure(data=[
        go.Scatter(
            x=chartDf.index,
            y=chartDf['adjclose'],
            name="Stock Price"
        )
    ])
    
    fig.update_xaxes(
        rangeslider_visible = True,
        rangeselector = dict(
        buttons = list([
            dict(count = 7, label = '1W', step = 'day', stepmode = 'backward'),
            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
            dict(step = 'all')])))
    
    fig.update_layout(
        title='Stock Time Series',
        yaxis_title='USD'
    )
    
    
    return fig

@st.cache_data
def createCandleStickChart(pxData: pd.DataFrame, iniDateStr: str, endDateStr: str):
    chartDf = adjustPxDataDf(pxData, iniDateStr, endDateStr)
    
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=chartDf.index,
                open=chartDf['open'],
                high=chartDf['high'],
                low=chartDf['low'],
                close=chartDf['adjclose']
            )
        ]
    )
    
    fig.update_xaxes(
        rangeslider_visible = True,
        rangeselector = dict(
        buttons = list([
            dict(count = 7, label = '1W', step = 'day', stepmode = 'backward'),
            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
            dict(step = 'all')])))
    
    fig.update_layout(
        title='Candlestick Chart',
        yaxis_title='USD'
    )
    
    return fig

@st.cache_data
def createOhlcChart(pxData: pd.DataFrame, iniDateStr: str, endDateStr: str):
    chartDf = adjustPxDataDf(pxData, iniDateStr, endDateStr)
    
    fig = go.Figure(
        data=[
            go.Ohlc(
                x=chartDf.index,
                open=chartDf['open'],
                high=chartDf['high'],
                low=chartDf['low'],
                close=chartDf['adjclose']
            )
        ]
    )
    
    fig.update_xaxes(
        rangeslider_visible = True,
        rangeselector = dict(
        buttons = list([
            dict(count = 7, label = '1W', step = 'day', stepmode = 'backward'),
            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
            dict(step = 'all')])))
    
    fig.update_layout(
        title='OHLC Chart',
        yaxis_title='USD'
    )
    
    return fig


@st.cache_data
def createBollingerBandsChart(pxData: pd.DataFrame, iniDateStr: str, endDateStr: str):
    chartDf = adjustPxDataDf(pxData, iniDateStr, endDateStr)
    
    chartDf['avg'] = chartDf['adjclose'].rolling(window=30).mean()
    chartDf['std'] = chartDf['adjclose'].rolling(window=30).std()
    
    chartDf['upperBound'] = chartDf['avg'] + chartDf['std']
    chartDf['lowerBound'] = chartDf['avg'] - chartDf['std']
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=chartDf.index,
            y=chartDf['adjclose'],
            name='Price'
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=chartDf.index,
            y=chartDf['avg'],
            name='30D Avg. Price',
            marker=dict(color="#94a3b8", size=5)
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=chartDf.index,
            y=chartDf['upperBound'],
            name='Bollinger Upper Bound',
            marker=dict(color="#14b8a6", size=5)
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=chartDf.index,
            y=chartDf['lowerBound'],
            name='Bollinger Lower Bound',
            marker=dict(color="#fda4af", size=5)
        )
    )
    
    fig.update_xaxes(
        rangeslider_visible = True,
        rangeselector = dict(
        buttons = list([
            dict(count = 7, label = '1W', step = 'day', stepmode = 'backward'),
            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
            dict(step = 'all')])))
    
    fig.update_layout(
        title='Bollinger Chart',
        yaxis_title='USD'
    )
    
    return fig

@st.cache_data
def createMovingAveragesChart(pxData: pd.DataFrame, iniDateStr: str, endDateStr: str):
    chartDf = adjustPxDataDf(pxData, iniDateStr, endDateStr)
    
    chartDf['sma'] = chartDf['adjclose'].rolling(window=7).mean()
    chartDf['lma'] = chartDf['adjclose'].rolling(window=24).mean()

    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=chartDf.index,
            y=chartDf['adjclose'],
            name='Price'
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=chartDf.index,
            y=chartDf['sma'],
            name='Short Period Moving Avg. (7D)',
            marker=dict(color="#facc15", size=5)
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=chartDf.index,
            y=chartDf['lma'],
            name='Long Period Moving Avg. (24D)',
            marker=dict(color="#a78bfa", size=5)
        )
    )
    
    fig.update_xaxes(
        rangeslider_visible = True,
        rangeselector = dict(
        buttons = list([
            dict(count = 7, label = '1W', step = 'day', stepmode = 'backward'),
            dict(count = 1, label = '1M', step = 'month', stepmode = 'backward'),
            dict(count = 6, label = '6M', step = 'month', stepmode = 'backward'),
            dict(count = 1, label = 'YTD', step = 'year', stepmode = 'todate'),
            dict(count = 1, label = '1Y', step = 'year', stepmode = 'backward'),
            dict(step = 'all')])))
    
    fig.update_layout(
        title='Moving Averages Chart',
        yaxis_title='USD'
    )
    
    return fig
    

@st.cache_resource(show_spinner=False)
def getStockData(ticker: str):

    with st.spinner(text="Downloading data..."):
        yahoo_Fin = Yahoo_Fin(ticker=ticker)
        yahoo_Fin.getData()
    
    st.session_state['stockData'] = {
        'pxData': yahoo_Fin.pxData,
        'quoteData': yahoo_Fin.quoteData,
        'statsValuation': yahoo_Fin.statsValuation.iloc[:, :2],
        'companyInfo': yahoo_Fin.companyInfo
        }

######## APP ########
st.header("Stock Data Analytics 💰")

with st.expander(label='', expanded=True):
    st.header("Please select a company")
    
    stock = st.selectbox(label="Stock", options=SELECT_STOCK_OPTIONS, label_visibility='visible', on_change=fullStateReset)
    
    st.button(
        label="Submit",
        on_click=getStockData,
        kwargs={
            'ticker': getTickerFromCompanyName(company=stock)
        }
    )
    
if 'stockData' in st.session_state and bool(st.session_state['stockData']):
    
    pxData = st.session_state['stockData']['pxData']
    lastPxData = pxData.iloc[-1]
    quoteData = st.session_state['stockData']['quoteData']
    
    statsValuationDf = st.session_state['stockData']['statsValuation']
    statsValuationDf = adjustStatsValuationDf(statsValuationDf)
    
    with st.expander(label='', expanded=True):
        st.header("Company KPIs")
        
        companyKpisColumns = st.columns(3)
        
        with companyKpisColumns[0]:
            marketCap = statsValuationDf.loc[statsValuationDf['index']=='Market Cap (intraday)', 'value'].iloc[0]
            st.metric(label='Market Cap', value=marketCap)
            
            trailingPe = statsValuationDf.loc[statsValuationDf['index']=='Trailing P/E', 'value'].iloc[0]
            st.metric(label='Trailing P/E', value=trailingPe)
            
        with companyKpisColumns[1]:
            enterpriseVl = statsValuationDf.loc[statsValuationDf['index']=='Enterprise Value', 'value'].iloc[0]
            st.metric(label='Market Cap', value=enterpriseVl)
            
            forwardPe = statsValuationDf.loc[statsValuationDf['index']=='Forward P/E', 'value'].iloc[0]
            st.metric(label='Forward P/E', value=forwardPe)
            
        with companyKpisColumns[2]:
            pegRatio = statsValuationDf.loc[statsValuationDf['index']=='PEG Ratio (5 yr expected)', 'value'].iloc[0]
            st.metric(label='PEG Ratio', value=pegRatio)
            
            priceBook = statsValuationDf.loc[statsValuationDf['index']=='Price/Book (mrq)', 'value'].iloc[0]
            st.metric(label='Price / Book', value=priceBook)
            
        st.header("Stock Analytics")
        
        stockAnalyticsColumns = st.columns(3)
        
        with stockAnalyticsColumns[0]:
            lastDatePrice = lastPxData.name.date().strftime("%Y-%m-%d")
            st.metric(label='Last Date Pricing', value=str(lastDatePrice))
            
            volume = lastPxData['volume']
            st.metric(label='Volume', value=adjustValueToString(volume))
            
            beta = quoteData['Beta (5Y Monthly)']
            st.metric(label='Beta', value=adjustValueToString(beta))
            
        with stockAnalyticsColumns[1]:
            lastDateOpenPx = lastPxData['open']
            st.metric(label='Open', value=adjustValueToString(lastDateOpenPx))
            
            lastDateHighPx = lastPxData['high']
            st.metric(label='High', value=adjustValueToString(lastDateHighPx))
            
            high30D = pxData['adjclose'].iloc[-30:].max()
            st.metric(label='30D Close Max.', value=adjustValueToString(high30D))
            
        with stockAnalyticsColumns[2]:
            lastDateClosePx = lastPxData['adjclose']
            st.metric(label='Close', value=adjustValueToString(lastDateClosePx))
            
            lastDateLowPx = lastPxData['low']
            st.metric(label='Low', value=adjustValueToString(lastDateLowPx))
            
            min30D = pxData['adjclose'].iloc[-30:].min()
            st.metric(label='30D Close Min.', value=adjustValueToString(min30D))
            
    with st.expander(label='', expanded=True):
        st.header("Charts")
        
        CHARTS_MAP = [
            {
                'name': 'timeSeriesChart',
                'tabName': 'Quote Price Evolution',
                'function': createTimeSeriesChart
            },
            {
                'name': 'candleStickChart',
                'tabName': 'Candlestick Chart',
                'function': createCandleStickChart
            },
            {
                'name': 'ohlcChart',
                'tabName': 'OHLC Chart',
                'function': createOhlcChart
            },
            {
                'name': 'bollingerBandsChart',
                'tabName': 'Bollinger Bands',
                'function': createBollingerBandsChart
            },
            {
                'name': 'movingAveragesChart',
                'tabName': 'Moving Averages',
                'function': createMovingAveragesChart
            }
        ]
        
        sliderDateOptions = [pxDate.date().strftime("%Y-%m-%d") for pxDate in list(pxData.index)]
        
        chartIniDate, chartEndDate = st.select_slider(
            label='Select date range',
            options=sliderDateOptions,
            value=(sliderDateOptions[0], sliderDateOptions[-1]),
            )
        
        tabs = st.tabs([chartObj['tabName'] for chartObj in CHARTS_MAP])
        
        for idx, chartObj in enumerate(CHARTS_MAP):
            with tabs[idx]:
                plot = chartObj['function'](pxData, chartIniDate, chartEndDate)
                st.plotly_chart(figure_or_data=plot, use_container_width=True)
                
    with st.expander(label='', expanded=True):
        st.header("The Company")
        st.markdown(body=st.session_state['stockData']['companyInfo'])
        
with st.expander(label='About', expanded=False):
    st.header("About")
    st.markdown(body="""
                Application uses the open yahoo finance API for data request.
                
                Data manipulation with pandas/numpy and plots with plotly.
                
                Select a stock to get the most recent available data and analytics.
                
                """)