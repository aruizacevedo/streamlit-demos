# Import libs
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

# Define functions


# Load data

def load_data():
    """Loads 4 dataframes and does light feature engineering"""

    # Video-level
    df_agg = (
        pd.read_csv(
            "youtube-metrics/data/Aggregated_Metrics_By_Video.csv", 
            header=0,
            names=[
                'Video', 'Video title', 'Video publish time', 'Comments added', 'Shares', 'Dislikes', 'Likes',
                'Subscribers lost', 'Subscribers gained', 'RPM(USD)', 'CPM(USD)', 'Average % viewed', 
                'Average view duration', 'Views', 'Watch time (hours)', 'Subscribers', 'Your estimated revenue (USD)', 
                'Impressions', 'Impressions ctr(%)'],
            skiprows=[0],
            parse_dates=['Video publish time']
        )
    )
    df_agg['Average view duration'] = df_agg['Average view duration'].apply(lambda x: datetime.strptime(x,'%H:%M:%S'))
    df_agg['Avg_duration_sec'] = df_agg['Average view duration'].apply(lambda x: x.second + x.minute*60 + x.hour*3600)
    df_agg['Engagement_ratio'] =  (df_agg['Comments added'] + df_agg['Shares'] +df_agg['Dislikes'] + df_agg['Likes']) /df_agg.Views
    df_agg['Views / sub gained'] = df_agg['Views'] / df_agg['Subscribers gained']
    df_agg.sort_values('Video publish time', ascending = False, inplace = True)    

    # Subscriber-level
    df_agg_sub = pd.read_csv("youtube-metrics/data/Aggregated_Metrics_By_Country_And_Subscriber_Status.csv")

    # Comments
    df_comments = pd.read_csv("youtube-metrics/data/All_Comments_Final.csv")

    # Performance Time Series
    df_time = (
        pd.read_csv("youtube-metrics/data/Video_Performance_Over_Time.csv")
        .assign(Date = lambda x: pd.to_datetime(x['Date']))
    )
    
    return df_agg, df_agg_sub, df_comments, df_time







# Engineer data
# - What metrics will be relevant?
# - Difference from baseline
# - Percent change by video

# Build dashboard
# - Total picture
# - Individual video
