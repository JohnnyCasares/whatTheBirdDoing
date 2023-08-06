import folium
from streamlit_folium import folium_static


def map_creator(latitude, longitude, tooltip):
    # center on the station
    m = folium.Map(location=[latitude, longitude], zoom_start=10)

    # add marker for the station
    folium.Marker([latitude, longitude], tooltip=tooltip).add_to(m)

    # call to render Folium map in Streamlit
    folium_static(m)



