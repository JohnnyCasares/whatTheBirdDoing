import os
import json
import requests
from io import BytesIO
from PIL import Image
import streamlit as st


@st.cache_resource
def save_audio(directory, animal_name, sound_url):
    response = requests.get(sound_url)
    file_path = f'{directory}/{animal_name}.mp3'
    with open(file_path, 'wb') as f:
        f.write(response.content)
    return file_path


# @st.cache_resource
def save_image(directory, animal_name, image_url):
    # Create the directory if it doesn't exist
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Download the image
        response = requests.get(image_url)
        # print(f"RESPONSE\n{response.content}\n")
        image = Image.open(BytesIO(response.content))

        # Save the image to disk
        filename = f"{directory}/{animal_name}.jpg"
        # Return the image
        image.save(filename)
        return image

    except:
        return None


@st.cache_resource
def search_images(query, api_key, search_engine_id) -> list:
    headers = {
        "Accept": "application/json"
    }
    params = {
        "key": api_key,
        "cx": search_engine_id,
        "q": query,
        "searchType": "image",
        "num": 5
    }
    response = requests.get("https://www.googleapis.com/customsearch/v1", headers=headers, params=params)
    results = json.loads(response.content)
    images = [item["link"] for item in results.get("items", [])]
    return images


@st.cache_resource
def search_by_coordinates(latitude, longitude):
    birds_coord = ApiRequest(f"{latitude}{longitude}Birds.json",
                             "birdCoordFiles",
                             f"https://api.ebird.org/v2/data/obs/geo/recent?lat={latitude}&lng={longitude}&&dist=50",
                             "API-KEY-HERE",
                             "Header-HERE")
    bird_data = birds_coord.save_response()
    return bird_data


class ApiRequest:
    def __init__(self, file_name, directory="jsonFiles", url="", api_key="", headers=None):
        self.file_name = file_name
        self.directory = directory
        self.url = url
        self.api_key = api_key
        self.headers = headers

    def save_response(self) -> dict:
        directory = self.directory
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = f"{directory}/{self.file_name}"
        if os.path.exists(file_path):
            # If the file exists, load the data from the file
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            # If the file doesn't exist, make a request to the API and store the data in the file
            if self.headers is None:
                url = f"{self.url}{self.api_key}"
                response = requests.get(url)
                data = response.json()
            else:
                url = self.url
                response = requests.get(url, headers={self.headers: self.api_key})
                data = response.json()
            with open(file_path, 'w') as f:
                json.dump(data, f)
        return data
