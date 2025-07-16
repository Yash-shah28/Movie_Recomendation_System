import requests
import streamlit as st
import pickle
import pandas as pd
import time
from justwatch import JustWatch


justwatch = JustWatch(country='IN')
def fetch_data(movie_name):
    print(f"Fetching poster for movie ID: {movie_name}")
    url = f"https://www.omdbapi.com/?t= {movie_name}&apikey=11545091&plot=full"
    try:
        time.sleep(2)
        response = requests.get(url)
        data = response.json()

        if data:
            poster_url = data["Poster"]
            plot = data["Plot"]
            year = data["Year"]
            Runtime = data['Runtime']
            imdbRating = data['imdbRating']
            return {
                "poster": poster_url,
                "plot": plot,
                "year": year,
                "runtime": Runtime,
                "imdbRating": imdbRating
            }
        else:
            st.warning(f"No poster path found for movie ID {movie_name}.")
            return ""
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch poster for movie ID {movie_name}: {e}")
        return ""


def recommend(movie):
    movies_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movies_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommend_movies = []
    recommend_movies_detail = {}
    counter = 1
    for i in movies_list:
        movie_name = movies.iloc[i[0]].title
        recommend_movies.append(movies.iloc[i[0]].title)
        recommend_movies_detail.setdefault(counter, []).append(fetch_data(movie_name))
        counter += 1
    return recommend_movies, recommend_movies_detail



st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="centered"
)


movie_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movie_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    "🎬 Select a movie:",
    movies['title'].values
)

if st.button('🚀 Recommend Similar Movies'):

    with st.spinner("Finding similar movies..."):
        movies, result = recommend(selected_movie_name)

        for name, (key,movie_data) in zip(movies, result.items()):
            for movie in movie_data:
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    poster = movie["poster"]
                    plot = movie["plot"]
                    year = movie["year"]
                    runtime = movie["runtime"]
                    imdb_rating  = movie["imdbRating"]

                    streaming_info = []
                    try:
                        results = justwatch.search_for_item(query=name)
                        if results['items']:
                            offers = results['items'][0].get('offers', [])
                            seen = set()
                            for offer in offers:
                                provider_name = offer.get('provider_id')
                                url = offer['urls'].get('standard_web', '')
                                if provider_name and provider_name not in seen:
                                    streaming_info.append(f"[Watch here]({url})")  # You can prettify it
                                    seen.add(provider_name)
                    except Exception as e:
                        streaming_info.append("⚠️ Streaming info not found")
                    with col1:
                        if poster != "N/A":
                            st.image(poster, width=120)
                            if streaming_info:
                                st.markdown("📺 **Available on:**")
                                for link in streaming_info:
                                    st.markdown(f"- {link}")
                            else:
                                st.markdown("📺 Not available on streaming platforms.")
                    with col2:
                        if poster != 'N/A':
                            st.subheader(name)
                            row1_col1, row1_col2 = st.columns(2)
                            with row1_col1:
                                st.text(f"📅 Year: {year}")
                            with row1_col2:
                                st.text(f"⏱ Runtime: {runtime}")
                            st.text(f"⭐ IMDb Rating: {imdb_rating}")
                            st.write(plot)

