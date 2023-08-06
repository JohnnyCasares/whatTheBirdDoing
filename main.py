# This is a sample Python script.
import os

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image, UnidentifiedImageError
from streamlit_extras.let_it_rain import rain

from services.api_request import ApiRequest, save_audio, save_image, search_images, search_by_coordinates
from widgets.drop_down import DropDownSelection
from widgets.graphs_and_maps import map_creator


@st.cache_resource
def rainEmoji(emoji):
    rain(
        emoji=emoji,
        font_size=54,
        falling_speed=5,
        animation_length="infinite",
    )


if __name__ == '__main__':

    st.title("🦅 What The Bird Doing? 🦅")

    # Ask user whether to choose by country or by coordinates
    search_method = st.radio("Choose a method of search",
                             ('By country', 'By coordinates'))
    ##SEARCH BY COORDINATES
    if search_method == "By coordinates":

        latitude = st.number_input("Enter a value for latitude", value=0.00, min_value=-90.00, max_value=90.00,
                                   help="Enter a value from -90 to 90")
        longitude = st.number_input("Enter a value for longitude", value=0.00, min_value=-180.00, max_value=180.00,
                                    help="Enter a value from -180 to 180")

        submit = st.button("Submit")
        if submit:
            bird_data = search_by_coordinates(latitude, longitude)

            if len(bird_data) == 0:
                st.error("There is no bird at this coordinate, please re-enter the values.😕")
            else:
                map_creator(latitude, longitude,
                            f"{latitude}, {longitude}")

                df = pd.DataFrame(bird_data)
                st.subheader("Bird Observations")
                st.write("Number of birds observed:")

                chart_data = df.groupby('comName')['howMany'].sum().reset_index()
                fig = px.scatter(chart_data, x='comName', y='howMany', color="comName",
                                 labels={'comName': 'Common Name', 'howMany': 'Number of Sightings'})
                st.plotly_chart(fig)

    ##SEARCH BY COUNTRY
    if search_method == "By country":
        # Countries
        countries_list = ApiRequest("countries.json",
                                    "jsonFiles")
        country_data = countries_list.save_response()

        country = DropDownSelection(country_data)
        country_code = country.get_country_code()
        if len(country_code) != 0:
            # Birds
            birds_country = ApiRequest(f"{country_code}Birds.json",
                                       "recentBirdFiles",
                                       f"https://api.ebird.org/v2/data/obs/{country_code}/recent",
                                       "API-KEY-HERE",
                                       "Header-HERE")

            bird_data = birds_country.save_response()

            bird = DropDownSelection(bird_data)
            bird_selected = bird.get_bird()
            if bird_selected is None:
                pass
            elif bird_selected != -1:
                my_map, pic, bar, all_data = st.tabs(["Map", "Picture & Sound", "Graphs", "All Data"])
                with my_map:
                    # Map
                    st.info(f'Bird seen date: {bird_data[bird_selected]["obsDt"]}')
                    st.info(f"{bird_data[bird_selected]['comName']}/ {bird_data[bird_selected]['sciName']}")
                    map_creator(bird_data[bird_selected]["lat"], bird_data[bird_selected]["lng"],
                                bird_data[bird_selected]["locName"])
                with bar:
                    # Bar Chart
                    df = pd.DataFrame(bird_data)


                    # Create a checkbox to switch between bar and line charts

                    st.subheader("Choose a Graph")
                    bar_chart = st.checkbox("Bar Chart")
                    line_graph = st.checkbox("Line Graph")


                    if bar_chart:

                        st.subheader("Number of birds observed in this country:")
                        chart_data = df.groupby('comName')['howMany'].sum().reset_index()
                        # Allow the user to select a color for the bar chart

                        figBar = px.bar(chart_data, x='comName', y='howMany', color="comName",
                                        labels={'comName': 'Common Name', 'howMany': 'Number of Sightings'})

                        st.plotly_chart(figBar)
                    if line_graph:

                        st.subheader("Number of birds observed over time in this country:")
                        line_chart_data = df.groupby('obsDt')['howMany'].sum().reset_index()
                        # Allow the user to select a color for the line chart
                        line_chart_color = st.color_picker("Choose a color for the line chart", "#00FF00")
                        figLine = px.line(line_chart_data, x='obsDt', y='howMany',
                                          labels={'obsDt': 'Observation Date', 'howMany': 'Number of Sightings'})
                        figLine.update_traces(line_color=line_chart_color)
                        st.plotly_chart(figLine)

                with pic:
                    # Bird Sound
                    species_name = bird_data[bird_selected]["sciName"]
                    sound_bird_URL = "https://www.xeno-canto.org/api/2/recordings?query="
                    bird_list = ApiRequest(f"{species_name}Sound.json",
                                           "soundFiles",
                                           sound_bird_URL + species_name)
                    currentIndex = 0
                    bird_sound_data = bird_list.save_response()
                    # st.write(bird_sound_data)
                    array_of_sounds = bird_sound_data["recordings"]
                    # st.subheader("Common Name/ Scientific Name")
                    st.info(f"{bird_data[bird_selected]['comName']}/ {bird_data[bird_selected]['sciName']}")
                    if len(array_of_sounds) > 0:
                        sound_url = bird_sound_data["recordings"][currentIndex]["file"]
                        # download the sound recording
                        file = save_audio("soundFiles", species_name, sound_url)
                        audio = open(file, 'rb')
                        st.audio(audio)
                    else:
                        st.warning("Sorry, no audio found for this bird")
                    # st.button("Next Audio")
                    # BIRD PICTURE
                    #
                    query = bird_data[bird_selected]["sciName"]
                    api_key = "YOUR-API-KEY-HERE"
                    search_engine_id = "Search-Engine-ID-HERE"

                    filename = f"imageFiles/{query}.jpg"
                    index = 0
                    if os.path.exists(filename):
                        # If the file already exists, return the image from file
                        bird_pic = Image.open(filename)
                    else:
                        bird_pic = None
                        # Otherwise, perform the image search and save the image
                        while index < 5:
                            try:
                                images = search_images(query, api_key, search_engine_id)
                                bird_pic = save_image("imageFiles", query, images[index])
                                break
                            except UnidentifiedImageError:
                                index = index + 1
                                if index >= 5:
                                    print(f"Error image out of bounds. 5 images did not work {NameError}")
                                    bird_pic = None
                                    break

                    if index < 5 and bird_pic is not None:
                        st.image(bird_pic)
                        cute_meter = ["🤢 Ugly",
                                      "😕 Not cute",
                                      "😐 Average",
                                      "😍 Cute",
                                      "🥰 Adorable"]
                        default_value = cute_meter[len(cute_meter) // 2]
                        emoji = st.select_slider("How cute is this bird?", options=cute_meter, value=default_value)
                        submit = st.button("Submit Rating")
                        if submit:
                            rainEmoji(emoji[0])
                            st.success("Your rating has been recorded")
                    else:
                        st.error("We were not able to retrieve an image for you 😞")
                with all_data:
                    st.subheader("All bird data in this country")


                    @st.cache_resource
                    def load_data():
                        return pd.DataFrame(
                            {
                                "Bird Names": [bird['comName'] for bird in bird_data],
                                "Scientific Name": [bird['sciName'] for bird in bird_data],
                                "Date Seen": [bird['obsDt'] for bird in bird_data],
                                # "Observations": [bird['howMany'] for bird in bird_data]

                            }
                        )

                    df = load_data()
                    st.dataframe(df)

            else:
                st.warning("No birds recently reported 😞. Please select another country")
