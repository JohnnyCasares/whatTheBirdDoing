import streamlit as st


class DropDownSelection:

    def __init__(self, data):
        self.data = data

    def get_country_code(self) -> str:
        country_options = {"Select a country": ""}

        for country in self.data:
            country_options[country["name"]] = country["code"]

        country = st.selectbox("Choose a country",
                               options=country_options)

        return country_options[country]

    def get_bird(self) -> int:
        bird_options = {"Select a bird": None}
        for i, bird in enumerate(self.data):
            bird_options[bird["comName"]] = i

        bird = st.selectbox("Choose a bird",
                            bird_options)
        # print(bird_options[bird])
        if len(self.data) == 0:
            return -1
        else:
            return bird_options[bird]
