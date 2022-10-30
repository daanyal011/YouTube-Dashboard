import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
import plotly.express as px
import country_converter as coco
from wordcloud import WordCloud

def style_negative(v, props=''):
    # Style negative values in dataframe
    try:
        return props if v < 0 else None
    except:
        pass


def style_positive(v, props=''):
    # Style positive values in dataframe
    try:
        return props if v > 0 else None
    except:
        pass

# %matplotlib inline
# streamlit run c:\Users\Admin\Desktop\MINIPROJECTSEM5\Dashboard.py
# RPM is revenue per mile means income generate per 100 views 
# top 10 videos, aggregate videos, future prediction 

# loading data 
@st.cache #this is used so that we can cache the data so that you have to load it once and not every time we reload the page 
def load_data():
    
    df_agg = pd.read_csv('Aggregated_Metrics_By_Video.csv').iloc[1:,:]
    df_agg.columns = ['Video','Video title','Video publish time','Comments added','Shares','Dislikes','Likes','Subscribers lost','Subscribers gained','RPM(USD)','CPM(USD)',
                        'Average % viewed','Average view duration','Views','Watch time (hours)','Subscribers','Your estimated revenue (USD)','Impressions','Impressions ctr(%)']#ctr is click through rate
    df_agg['Video publish time'] = pd.to_datetime(df_agg['Video publish time'])
    df_agg['Average view duration'] = df_agg['Average view duration'].apply(lambda x: datetime.strptime(x,'%H:%M:%S'))
    df_agg['Avg_duration_sec'] = df_agg['Average view duration'].apply(lambda x: x.second + x.minute*60 + x.hour*3600)
    df_agg['Engagement_ratio'] =  (df_agg['Comments added'] + df_agg['Shares'] +df_agg['Dislikes'] + df_agg['Likes']) /df_agg.Views
    df_agg['Views / sub gained'] = df_agg['Views'] / df_agg['Subscribers gained']
    df_agg.sort_values('Video publish time', ascending = False, inplace = True)    
    df_agg_sub = pd.read_csv('Aggregated_Metrics_By_Country_And_Subscriber_Status.csv')
    df_comments = pd.read_csv('Aggregated_Metrics_By_Video.csv')
    df_time = pd.read_csv('Video_Performance_Over_Time.csv')
    df_time['Date'] = pd.to_datetime(df_time['Date'])
    return df_agg, df_agg_sub, df_comments, df_time 


df_agg, df_agg_sub, df_comments, df_time = load_data()

# additional data engineering for aggregated data
df_agg_diff = df_agg.copy()
metric_date_12mo = df_agg_diff['Video publish time'].max() - pd.DateOffset(months=12)
median_agg = df_agg_diff[df_agg_diff['Video publish time']>= metric_date_12mo].median()

# create differences from the median for values
# Just numeric columns
numeric_cols = np.array((df_agg_diff.dtypes == 'float64') | (df_agg_diff.dtypes == 'int64'))
df_agg_diff.iloc[:, numeric_cols] = (df_agg_diff.iloc[:, numeric_cols] - median_agg).div(median_agg)
#merge daily data with publish data to get delta 
df_time_diff = pd.merge(df_time, df_agg.loc[:,['Video','Video publish time']], left_on ='External Video ID', right_on = 'Video')
df_time_diff['days_published'] = (df_time_diff['Date'] - df_time_diff['Video publish time']).dt.days

# get last 12 months of data rather than all data 
date_12mo = df_agg['Video publish time'].max() - pd.DateOffset(months =12)
df_time_diff_yr = df_time_diff[df_time_diff['Video publish time'] >= date_12mo]

# get daily view data (first 30), median & percentiles 
views_days = pd.pivot_table(df_time_diff_yr,index= 'days_published',values ='Views', aggfunc = [np.mean,np.median,lambda x: np.percentile(x, 80),lambda x: np.percentile(x, 20)]).reset_index()
views_days.columns = ['days_published','mean_views','median_views','80pct_views','20pct_views']
views_days = views_days[views_days['days_published'].between(0,30)]
views_cumulative = views_days.loc[:,['days_published','median_views','80pct_views','20pct_views']] 
views_cumulative.loc[:,['median_views','80pct_views','20pct_views']] = views_cumulative.loc[:,['median_views','80pct_views','20pct_views']].cumsum()

# Streamlit app building
add_sidebar = st.sidebar.selectbox('Aggregate or Individual Video, Future Predictions', ('Aggregate Metrics', 'Individual Video Analysis','Growth of channel in future','Top 10 Most Viewed , Liked , Subscribed ,Commented, and Shared videos','Top 25 words which give most attraction'))

# Showing aggregate metrics
if add_sidebar == 'Aggregate Metrics':
    st.write("YouTube Aggregated Data")
    
    df_agg_metrics = df_agg[['Video publish time','Views','Likes','Subscribers','Shares','Comments added','RPM(USD)','Average % viewed','Avg_duration_sec', 'Engagement_ratio','Views / sub gained']]
    metric_date_6mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months =6)
    metric_date_12mo = df_agg_metrics['Video publish time'].max() - pd.DateOffset(months =12)
    metric_medians6mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_6mo].median()
    metric_medians12mo = df_agg_metrics[df_agg_metrics['Video publish time'] >= metric_date_12mo].median()
    
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
    
    # get date information / trim to relevant data
    df_agg_diff['Publish_date'] = df_agg_diff['Video publish time'].apply(lambda x: x.date())
    
    df_agg_diff_final = df_agg_diff.loc[:, ['Video title', 'Publish_date', 'Views', 'Likes', 'Subscribers', 'Shares', 'Comments added', 'RPM(USD)', 'Average % viewed',
                                            'Avg_duration_sec', 'Engagement_ratio', 'Views / sub gained']]

    df_agg_numeric_lst = df_agg_diff_final.median().index.tolist()
    df_to_pct = {}
    for i in df_agg_numeric_lst:
        df_to_pct[i] = '{:.1%}'.format

    st.dataframe(df_agg_diff_final.style.hide().applymap(style_negative, props='color:red;').applymap(style_positive, props='color:green;').format(df_to_pct))
    
    st.write('Views gained over time')
    df_vpo = pd.read_csv('Video_Performance_Over_Time.csv')
    df_cl = df_vpo.dropna()
    df_cl['Date'] = pd.to_datetime(df_cl['Date'])
    df_cl['Month'] = df_cl['Date'].dt.month
    fig = px.line(df_cl, x=df_cl['Date'], y=df_cl['Views'])
    fig.update_layout(height=600,width=1100)
    st.plotly_chart(fig)

if add_sidebar == 'Individual Video Analysis':
    videos = tuple(df_agg['Video title'])
    st.write("Individual Video Performance")
    video_select = st.selectbox('Pick a Video:', videos)
    
    agg_filtered = df_agg[df_agg['Video title'] == video_select]
    agg_sub_filtered = df_agg_sub[df_agg_sub['Video Title'] == video_select] # sort in another variable and pass
    
    agg_sub_filtered['Country'] = coco.convert(names= agg_sub_filtered['Country Code'], to = 'name_short')
    agg_sub_filtered.sort_values('Views',ascending=False, inplace=True)
    fig = px.bar(agg_sub_filtered, x='Views', y='Is Subscribed', color='Country', orientation='h')
    fig.update_layout(height=500,width =1000)
    st.plotly_chart(fig)

    fig_map = go.Figure(data=go.Choropleth(
    locations=agg_sub_filtered['Country'], # Spatial coordinates
    z = agg_sub_filtered['Views'].astype(float), # Data to be color-coded
    locationmode = 'country names', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "Views",))
    fig_map.update_layout(title_text = 'Total Views by Country',height=600,width=1100)
    st.plotly_chart(fig_map)
    

    agg_time_filtered = df_time_diff[df_time_diff['Video Title'] == video_select]
    first_30 = agg_time_filtered[agg_time_filtered['days_published'].between(0,30)]
    first_30 = first_30.sort_values('days_published')
    st.write()
    
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['20pct_views'],mode='lines',name='20th percentile', line=dict(color='purple', dash ='dash')))
    fig1.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['median_views'],mode='lines',name='50th percentile', line=dict(color='black', dash ='dash')))
    fig1.add_trace(go.Scatter(x=views_cumulative['days_published'], y=views_cumulative['80pct_views'],mode='lines', name='80th percentile', line=dict(color='royalblue', dash ='dash')))
    fig1.add_trace(go.Scatter(x=first_30['days_published'], y=first_30['Views'].cumsum(),mode='lines', name='Current Video' ,line=dict(color='firebrick',width=8)))
        
    fig1.update_layout(title='View comparison first 30 days',xaxis_title='Days Since Published',yaxis_title='Cumulative views',height=500,width =1000)
    
    st.plotly_chart(fig1)

if add_sidebar == 'Growth of channel in future':
    
    q = df_agg['Likes'].quantile(0.5)
    data_1 = df_agg[df_agg['Likes']<q]

    q = data_1['Shares'].quantile(0.99)
    data_2 = data_1[data_1['Shares']<q]

    q = data_2['Views'].quantile(0.99)
    data_3 = data_2[data_2['Views']<q]

    data_cleaned = data_3.reset_index(drop=True)

    fig_dp = px.scatter(data_cleaned,x='Likes',y='Shares',trendline='ols',trendline_color_override='red')
    fig_dp.update_layout(title='Growth of Shares with Likes',height=600,width =1100)
    st.plotly_chart(fig_dp)
    
    fig_dp1 = px.scatter(data_cleaned, x='Likes',y='Views',trendline='ols',trendline_color_override='red')
    fig_dp1.update_layout(title='Growth of Views with Likes',height=600,width =1100)
    st.plotly_chart(fig_dp1)
    
if add_sidebar == 'Top 10 Most Viewed , Liked , Subscribed ,Commented, and Shared videos':
    
    df_7=df_agg_sub.dropna()
    title=df_7.groupby(["Video Title"])["Views"].sum().sort_values(ascending=False).reset_index().head(10)
    fig_dp2=px.bar(title,x="Video Title",y="Views",title="Top 10 Most Viewed Videos",color='Views',text="Views")
    fig_dp2.update_layout(height=600,width =1100)
    st.plotly_chart(fig_dp2)
    
    video=df_7.groupby(["Video Title"])["Video Likes Added"].sum().sort_values(ascending=False).reset_index().head(10)
    fig_dp3=px.bar(video,x="Video Title",y="Video Likes Added",title="Top 10 Most Liked Videos ",color='Video Likes Added',text='Video Likes Added')
    fig_dp3.update_layout(height=600,width =1100)
    st.plotly_chart(fig_dp3)

    df_15 = df_agg.groupby('Video title')['Subscribers gained'].sum().sort_values(ascending=False).reset_index().head(10)
    fig_dp4 = px.bar(df_15, x='Video title',y = 'Subscribers gained',color='Subscribers gained',text='Subscribers gained')
    fig_dp4.update_layout(title='Top 10 Most Subscribers Gained Videos',height=600,width =1100)
    st.plotly_chart(fig_dp4)

    df_11 = df_agg.groupby('Video title')['Comments added'].sum().sort_values(ascending=False).reset_index().head(10)
    fig_dp7 = px.bar(df_11, x='Video title',y = 'Comments added',color='Comments added',text='Comments added')
    fig_dp7.update_layout(title='Top 10 Most Commented Videos',height=600,width =1100)
    st.plotly_chart(fig_dp7)

    df_12 = df_agg.groupby('Video title')['Shares'].sum().sort_values(ascending=False).reset_index().head(10)
    fig_dp8 = px.bar(df_12, x='Video title',y = 'Shares',color='Shares',text='Shares')
    fig_dp8.update_layout(title='Top 10 Most Shared Videos',height=600,width =1100)
    st.plotly_chart(fig_dp8)

if add_sidebar == 'Top 25 words which give most attraction':
    
    titles_1 = df_agg.loc[df_agg['Subscribers'] > 100].sort_values('Subscribers', ascending=False)['Video title'][1:].tolist()
    words_1 = [word for titles_1 in titles_1 for word in titles_1.split()]
    words_1_joined=(" ").join(words_1)


    titles_2 = df_agg.loc[df_agg['Subscribers'] <= 20].sort_values('Subscribers', ascending=False)['Video title'].tolist()
    words_2 = [word for titles_2 in titles_2 for word in titles_2.split()]
    words_2_joined=(" ").join(words_2)


    word_count1 = pd.DataFrame.from_dict(WordCloud().process_text(words_1_joined), orient='index', columns=['Frequency'])
    word_count2 = pd.DataFrame.from_dict(WordCloud().process_text(words_2_joined), orient='index', columns=['Frequency'])


    df_word = word_count1.sort_values('Frequency', ascending=False)[:25].sort_values('Frequency')
    df_word2 = word_count2.sort_values('Frequency', ascending=False)[:25].sort_values('Frequency')

    ddp = df_word
    ddp.reset_index(inplace=True)
    ddp.columns=['Topic','Frequency']

    fig_ddp = px.bar(ddp,x='Frequency',y='Topic',orientation='h',title='Topics That Gained Most Subscribers')
    fig_ddp.update_layout(height=600,width=1100)
    st.plotly_chart(fig_ddp)

    ddp_7=df_word2
    ddp_7.reset_index(inplace=True)
    ddp_7.columns=['Topic','Frequency']

    fig_ddp7 = px.bar(ddp_7,x='Frequency',y='Topic',orientation='h',title='Topics That Gained Least Subscribers')
    fig_ddp7.update_layout(height=600,width=1100)
    st.plotly_chart(fig_ddp7)
    
    st.write('INSIGHTS')
    st.write('• Both groups are similar due to the subject of the channel (words like "Data Science", "Data" and "Scientist" are popular in both of them) but there are also some differences')
    st.write('• Videos that attract new audience are more frequently focused on learning. The words "Learning" and "Learn" are some of the most frequent in this group. Also there are lots of words related to creating projects - "Project", "Scratch", "Python", "Kaggle", Github", "Portfolio"...')
    st.write('• The second group seems to have more of entertaining videos. Words like "Shorts", "Live", "Stream" and "Funny" are unique to this group.')
    
    
# print("daanyal")
