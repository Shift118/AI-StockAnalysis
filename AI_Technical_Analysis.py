import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from dotenv import find_dotenv, load_dotenv
import os
load_dotenv(find_dotenv())
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Set up Streamlit App
st.set_page_config(
    page_title="StockAI",
    layout="wide",
    page_icon="📈"
    )
st.title("AI-Powered Technical Stock Analysis Dashboard")
st.sidebar.header("Configuration")

#Input For Stock Ticker & Data Range
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g, AAPL):")
start_date = st.sidebar.date_input("Start Date",value = pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End Date", value = pd.to_datetime("today"))

#Fetch Stock Data
if st.sidebar.button("Fetch Data"):
    st.session_state["stock_data"] = yf.download(ticker,start=start_date,end = end_date)
    st.success("Stock Data Loaded Successfully")

#Check if data is available
if "stock_data" in st.session_state:
    data = st.session_state["stock_data"]
    
    #plot candlestick chart
    fig = go.Figure(data=[
        go.Candlestick(
        x = data.index,
        open = data['Open'],
        high = data['High'],
        low = data['Low'],
        close = data['Close'],
        name = 'Candlestick'
    )
    ])
    
#Sidebar: Select Technical Indicator