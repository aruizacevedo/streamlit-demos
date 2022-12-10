# Import libs
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

# Define functions


# Load data
df_agg = pd.read_csv("youtube-metrics/data/Aggregated_Metrics_By_Video.csv").iloc[1:,:]
df_agg_sub = pd.read_csv("youtube-metrics/data/Aggregated_Metrics_By_Country_And_Subscriber_Status.csv")
df_comments = pd.read_csv("youtube-metrics/data/All_Comments_Final.csv")
df_time = pd.read_csv("youtube-metrics/data/Video_Performance_Over_Time.csv")



# Engineer data
# - What metrics will be relevant?
# - Difference from baseline
# - Percent change by video

# Build dashboard
# - Total picture
# - Individual video
