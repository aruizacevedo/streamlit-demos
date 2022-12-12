# Import libs
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from datetime import datetime

# Define functions

def style_negative(v, props=''):
    """ Style negative values in dataframe"""
    try: 
        return props if v < 0 else None
    except:
        pass
    
def style_positive(v, props=''):
    """Style positive values in dataframe"""
    try: 
        return props if v > 0 else None
    except:
        pass    


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
    
    st.write("Ken Jee YouTube Aggregated Data")
    
    df_agg_metrics = df_agg[[
        'Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed',
        'Avg_duration_sec', 'Engagement_ratio','Views / sub gained']]
    metric_date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months = 6)
    metric_date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months = 12)
    metric_medians6mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_6mo].median(numeric_only=True)
    metric_medians12mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_12mo].median(numeric_only=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    columns = [col1, col2, col3, col4, col5]
    
    count = 0
    for i in metric_medians6mo.index:
        with columns[count]:
            delta = (metric_medians6mo[i] - metric_medians12mo[i])/metric_medians12mo[i]
            st.metric(label= i, value = round(metric_medians6mo[i],1), delta = "{:.2%}".format(delta))
            count += 1
            if count >= 5:
                count = 0

    #get date information / trim to relevant data 
    df_agg_diff['Publish_date'] = df_agg_diff['Video publish time'].apply(lambda x: x.date())
    df_agg_diff_final = df_agg_diff.loc[:,['Video title','Publish_date','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed',
                             'Avg_duration_sec', 'Engagement_ratio','Views / sub gained']]
    
    df_agg_numeric_lst = df_agg_diff_final.median().index.tolist()
    df_to_pct = {}
    for i in df_agg_numeric_lst:
        df_to_pct[i] = '{:.1%}'.format
    
    st.dataframe(df_agg_diff_final.style.hide().applymap(style_negative, props='color:red;').applymap(style_positive, props='color:green;').format(df_to_pct))




if add_sidebar == 'Individual Video Analysis':
    pass




# - Total picture
# - Individual video
