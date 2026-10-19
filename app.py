import streamlit as st
import requests

# Define the callback function to reset the state
def reset_all_inputs():
    st.session_state["input_one"] = ""
    st.session_state["input_two"] = ""
    st.session_state["input_three"] = ""



st.markdown(
    'Welcome to the stock market weather forecast'
)

headline_1 = st.text_input('Enter the first headline', key="input_one")
headline_2 = st.text_input('Enter the second headline', key="input_two")
headline_3 = st.text_input('Enter the third headline', key="input_three")


text_input = headline_1 + ' ' + headline_2 + ' ' + headline_3


API_PATH = 'http://localhost:8080'

if st.button('Predict weather on the stock market'):
    url = API_PATH
    params = {
        'headline': text_input
    }

    response = requests.get(f'{url}/predict', params=params)

    if response.status_code == 200:
        prediction = response.json()
        weather = prediction['prediction']
        st.markdown(f'Predicted weather: {weather}')

    else:
        st.error(f'API call failed with status {response.status_code}: {response.text}')



# Create a button that triggers the callback
st.button("Clear All Inputs", on_click=reset_all_inputs)
