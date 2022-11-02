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
