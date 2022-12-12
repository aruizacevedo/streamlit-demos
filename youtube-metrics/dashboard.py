# Import libs
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

# Define functions


@st.cache
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

# Load dataframes
df_agg, df_agg_sub, df_comments, df_time = load_data()


# Additional data engineering for aggregated data 
df_agg_diff = df_agg.copy()
metric_date_12mo = df_agg_diff['Video publish time'].max() - pd.DateOffset(months = 12)
median_agg = df_agg_diff[df_agg_diff['Video publish time'] >= metric_date_12mo].median(numeric_only=True)

# Create differences from the median for values 
# Just numeric columns 
numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))
df_agg_diff.iloc[:,numeric_cols] = (df_agg_diff.iloc[:,numeric_cols] - median_agg).div(median_agg)


# Merge daily data with publish data to get delta 
df_time_diff = pd.merge(
    df_time, 
    df_agg.loc[:,['Video','Video publish time']], 
    left_on = 'External Video ID', 
    right_on = 'Video'
)
df_time_diff['days_published'] = (df_time_diff['Date'] - df_time_diff['Video publish time']).dt.days

# get last 12 months of data rather than all data 
date_12mo = df_agg['Video publish time'].max() - pd.DateOffset(months = 12)
df_time_diff_yr = df_time_diff[df_time_diff['Video publish time'] >= date_12mo]

# get daily view data (first 30), median & percentiles 
views_days = (
    pd.pivot_table(
        df_time_diff_yr, 
        index = 'days_published', values = 'Views', 
        aggfunc = [np.mean, np.median, lambda x: np.percentile(x, 80), lambda x: np.percentile(x, 20)]
    )
    .reset_index()
)
views_days.columns = ['days_published','mean_views','median_views','80pct_views','20pct_views']
views_days = views_days[views_days['days_published'].between(0,30)]
views_cumulative = views_days.loc[:,['days_published','median_views','80pct_views','20pct_views']] 
views_cumulative.loc[:,['median_views','80pct_views','20pct_views']] = views_cumulative.loc[:,['median_views','80pct_views','20pct_views']].cumsum()




# Engineer data
# - What metrics will be relevant?
# - Difference from baseline
# - Percent change by video

# Build dashboard
###############################################################################
#Start building Streamlit App
###############################################################################

add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video', ('Aggregate Metrics', 'Individual Video Analysis'))

if add_sidebar == 'Aggregate Metrics':
    pass

if add_sidebar == 'Individual Video Analysis':
    pass




# - Total picture
# - Individual video
