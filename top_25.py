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
    