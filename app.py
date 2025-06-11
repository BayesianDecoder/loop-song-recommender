import streamlit as st
from content_based_filtering import content_recommendation
from scipy.sparse import load_npz
import pandas as pd
from numpy import load
from hybrid_recommendations import HybridRecommenderSystem
import re


# load the data
cleaned_data_path = "data/cleaned_data.csv"
songs_data = pd.read_csv(cleaned_data_path)

# load the transformed data
transformed_data_path = "data/transformed_data.npz"
transformed_data = load_npz(transformed_data_path)

# load the track ids
track_ids_path = "data/track_ids.npy"
track_ids = load(track_ids_path,allow_pickle=True)

# load the filtered songs data
filtered_data_path = "data/collab_filtered_data.csv"
filtered_data = pd.read_csv(filtered_data_path)

# load the interaction matrix
interaction_matrix_path = "data/interaction_matrix.npz"
interaction_matrix = load_npz(interaction_matrix_path)

# load the transformed hybrid data
transformed_hybrid_data_path = "data/transformed_hybrid_data.npz"
transformed_hybrid_data = load_npz(transformed_hybrid_data_path)

#logo
# st.image("logo.jpeg", width=250)

# col1, col2, col3 = st.columns([1, 2, 1])
# with col2:
#     st.image("logo.jpeg", width=350)





# Title
# st.title('Feel the rhythm! Find your LOOP 🔁')

# Subheader
# st.write('### Enter the name of a song and the recommender will suggest similar songs 🎵🎧')

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.jpeg", width=400)
    st.markdown("<h1 style='text-align: center;'>Feel the rhythm! Find your LOOP 🔁</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Enter the name of a song and get handpicked recommendations 🎵🎧</h4>", unsafe_allow_html=True)

# Text Input
st.markdown("### 🎶 Song Input")
song_name = st.text_input('Enter a song name:', key="song_input")
#song_name = st.text_input('Enter a song name:')
st.write('You entered:', song_name)
# artist name
#artist_name = st.text_input('Enter the artist name:')
#st.write('You entered:', artist_name)

song_name = song_name.strip()                    # removes leading/trailing spaces
song_name = re.sub(r'\s+', ' ', song_name)       # replaces multiple spaces with single space

# lowercase the input
song_name = song_name.lower()
#artist_name = artist_name.lower()

# k recommndations
# k = st.selectbox('How many recommendations do you want?', [5,10,15,20], index=1)

st.markdown("### 🔢 How many recommendations?")
k = st.selectbox('', [5, 10, 15, 20], index=1)

if (filtered_data["name"] == song_name).any():   
#if ((filtered_data["name"] == song_name) & (filtered_data["artist"] == artist_name)).any(): 
    # type of filtering
    filtering_type = "Hybrid Recommender System"

    # diversity slider
    diversity = st.slider(label="Diversity in Recommendations",
                        min_value=0,
                        max_value=10,
                        value=5,
                        step=1)
    with st.expander("🤔 What does this mean?"):
        st.markdown("""
    - **Personalized**: You’ll get songs that feel *just like* the one you entered — similar mood, energy, and vibe.  
    - **Diverse**: You’ll discover songs that other people with similar taste have liked — perfect if you're open to exploring something new.
    
    🎯 **Tip:** CHOOSE THE RIGHT RATIO:
    - Slide more towards *Personalized* for  similar tracks.  
    - Slide towards *Diverse* to discover new songs .
    """)

    content_based_weight = 1 - (diversity / 10)
    
    # plot a bar graph
    chart_data = pd.DataFrame({
        "type" : ["Personalized", "Diverse"],
        "ratio": [10 - diversity, diversity]
    })
    st.markdown("### ⚖️ Your Mix Ratio")
    st.bar_chart(chart_data,x="type",y="ratio")
    
else:
    # type of filtering
    filtering_type = 'Content-Based Filtering'

# Button
if filtering_type == 'Content-Based Filtering':
    if st.button('Get Recommendations'):
        #if ((songs_data["name"] == song_name) & (songs_data['artist'] == artist_name)).any():
        if (songs_data["name"] == song_name).any():
            st.write('Recommendations for', f"**{song_name}**")
            recommendations = content_recommendation(song_name=song_name,
                                                     
                                                     songs_data=songs_data,
                                                     transformed_data=transformed_data,
                                                     k=k)
            
            # Display Recommendations
            for ind , recommendation in recommendations.iterrows():
                song_name = recommendation['name'].title()
                artist_name = recommendation['artist'].title()
                
                if ind == 0:
                    st.markdown("## Currently Playing")
                    st.markdown(f"#### **{song_name}** by **{artist_name}**")
                    st.audio(recommendation['spotify_preview_url'])
                    st.write('---')
                elif ind == 1:   
                    st.markdown("### Next Up 🎵")
                    st.markdown(f"#### {ind}. **{song_name}** by **{artist_name}**")
                    st.audio(recommendation['spotify_preview_url'])
                    st.write('---')
                else:
                    st.markdown(f"#### {ind}. **{song_name}** by **{artist_name}**")
                    st.audio(recommendation['spotify_preview_url'])
                    st.write('---')
        else:
            st.write(f"Sorry, we couldn't find {song_name} in our database. Please try another song.")
            
elif filtering_type == "Hybrid Recommender System":
    if st.button('Get Recommendations'):
        st.write('Recommendations for', f"**{song_name}**")
        recommender = HybridRecommenderSystem(
                                                number_of_recommendations= k,
                                                weight_content_based= content_based_weight
                                                )
                                
        # get the recommendations
        recommendations = recommender.give_recommendations(song_name= song_name,
                                                       
                                                        songs_data= filtered_data,
                                                        transformed_matrix= transformed_hybrid_data,
                                                        track_ids= track_ids,
                                                        interaction_matrix= interaction_matrix)
        # Display Recommendations
        for ind , recommendation in recommendations.iterrows():
            song_name = recommendation['name'].title()
            artist_name = recommendation['artist'].title()
            
            if ind == 0:
                st.markdown("## Currently Playing")
                st.markdown(f"#### **{song_name}** by **{artist_name}**")
                st.audio(recommendation['spotify_preview_url'])
                st.write('---')
            elif ind == 1:   
                st.markdown("### Next Up 🎵")
                st.markdown(f"#### {ind}. **{song_name}** by **{artist_name}**")
                st.audio(recommendation['spotify_preview_url'])
                st.write('---')
            else:
                st.markdown(f"#### {ind}. **{song_name}** by **{artist_name}**")
                st.audio(recommendation['spotify_preview_url'])
                st.write('---')