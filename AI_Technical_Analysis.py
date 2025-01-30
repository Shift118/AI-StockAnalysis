import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from dotenv import find_dotenv, load_dotenv
import os
import base64
import openai as OpenAI
import requests
import tempfile

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
    st.sidebar.subheader("Technical Indicators")
    indicators = st.sidebar.multiselect(
        "Select Indicators:",
        ["20-Day SMA", "20-Day EMA","20-Day Bollinger Bands", "VWAP"],
        default= ["20-Day SMA"]
    )
    
    def add_indicator(indicator):
        if indicator == "20-Day SMA":
            sma = data['Close'].rolling(window = 20).mean()
            fig.add_trace(go.Scatter(x=data.index, y=sma,mode='lines',name='SMA (20)'))
            
        elif indicator == "20-Day EMA":
            ema = data['Close'].ewm(window = 20).mean()
            fig.add_trace(go.Scatter(x=data.index, y=ema,mode='lines',name='EMA (20)'))
            
        elif indicator == "20-Day Bollinger Bands":
            sma = data['Close'].rolling(window = 20).mean()
            std = data['Close'].rolling(windows = 20).std()
            bb_upper = sma + 2 * std
            bb_lower = sma - 2 * std
            fig.add_trace(go.Scatter(x=data.index, y=bb_upper,mode='lines',name='BB Upper'))
            fig.add_trace(go.Scatter(x=data.index, y=bb_lower,mode='lines',name='BB Lower'))
            
        elif indicator == "VWAP":
            data['VWAP'] = (data['Close'] * data["Volume"]).cumsum() / data['Volume'].cumsum()
            fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'],mode='lines',name='VWAP'))
    #Add Selected Indicator To The Chart
    for indicator in indicators:
        add_indicator(indicator)
    
    fig.update_layout(xaxis_rangeslider_visible = False)
    st.plotly_chart(fig)
    
    #Analyze Chart with LLaMA 3.2 Vision on Hugging Face
    st.subheader("AI-Powered Analysis")
    if st.button("Run AI Analysis"):
        with st.spinner("Analyzing the Chart, Please wait..."):
            #Save Chart as a temporary image
            with tempfile.NamedTemporaryFile(suffix = ".png",delete = False) as tmpfile:
                fig.write_image(tmpfile.name)
                tmpfile_path = tmpfile.name
            
            #Read Image and encode to Base64
            with open(tmpfile_path,"rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
                
            #Prepare AI analysis request
            messages = [{
                'role':'user',
                'content':"""You are a Stock Trader specializing in Technical Analysis at a top financial institution. 
                Analyze the stock chart's technical indicators and provide a buy/hold/sell recommendation.
                Base your recommendation only on the candlestick chart and the displayed technical indicators.
                First, provide the recommendation, then, provide your detailed reasoning.""",
                'images':[image_data]
            }]

            #Hugging Face API Endpoint & Headers
            API_URL = "https://api-inference.huggingface.co/v1/meta-llama/Llama-3.2-11B-Vision"
            headers = {
                "Authorization":f"Bearer {HUGGINGFACE_API_TOKEN}",
                "Content-Type":"application/json"
            }
            #Sending the request
            response = requests.post(API_URL,headers=headers,json={"inputs":messages})
            
            if response.status_code == 200:
                st.write("**AI Analysis Results:**")
                st.write(response["message"]["content"])
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
            
            os.remove(tmpfile_path)

            
            
            
            
            
            
            
            
            
            
            
            
            
                       