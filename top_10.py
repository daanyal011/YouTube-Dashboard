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
