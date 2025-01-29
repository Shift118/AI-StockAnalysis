import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from dotenv import find_dotenv, load_dotenv
import os
load_dotenv(find_dotenv())
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")