import streamlit as st
import requests

# Inject custom CSS to cleanly change the main app layout background
st.markdown(
    """
    <style>
    .stApp {
        background-color: #F4F3EF; /* Replace with any Hex or HTML color */
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Custom Styled Headline

st.html("""
    <div style="
        background: linear-gradient(135deg, #2ec4b6, #0f4c5c);
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h1 style="color: white; margin: 0; font-family: sans-serif; font-size: 2.0rem;">
            🔮 Smart stock market weather forecaster
        </h1>
        <p style="color: #e0f2f1; margin: 8px 0 0 0; font-family: sans-serif; font-size: 1rem; opacity: 0.9;">
            🐂  Enter news headlines into the text fields below and click Predict to try your luck  🐻


        </p>
    </div>
""")

# 🐂 Enter news headlines into the text area below. Our AI model will classify the market sentiment 🐻

#  st.title(
#     'Welcome to the stock market weather forecast', text_alignment="left"
# )

st.text('')

# 1. Initialize the number of text inputs in session state
if "num_inputs" not in st.session_state:
    st.session_state.num_inputs = 3

if "model_choice" not in st.session_state:
    st.session_state.model_choice = 'LinearSVC, stock price move > 1 STD'

# 2. Callback function to increase the count when the last input is filled
def check_last_input():
    last_index = st.session_state.num_inputs - 2
    if st.session_state.get(f"input_{last_index}"):
        st.session_state.num_inputs += 1

# 3. Callback function to reset all inputs dynamically
def reset_all_inputs():
    # Clear out all the dynamically generated input keys in session state
    for i in range(st.session_state.num_inputs):
        key = f"input_{i}"
        if key in st.session_state:
            st.session_state[key] = ""
    # Reset the starting input field count back to 3
    st.session_state.num_inputs = 3
    st.session_state.model_choice = 'LinearSVC, stock price move > 1 STD'

# 4. Dynamically render the text inputs
for i in range(st.session_state.num_inputs):
    is_last = (i == st.session_state.num_inputs - 2)

    st.text_input(
        label=f"Headline {i+1}",
        key=f"input_{i}",
        on_change=check_last_input if is_last else None
    )


# Gather all text input values into a single Python list
# We use list comprehension to grab the value from session_state for each key
all_inputs_list = [st.session_state.get(f"input_{i}", "") for i in range(st.session_state.num_inputs)]

# Debug display to see your live list (you can remove this in production)
# st.write("### Current Inputs List:", all_inputs_list)

# Concatenate all headlines into one string
text_input = ' '.join(all_inputs_list)


# Create a selector to choose the model
model_selected = st.selectbox('Select model', [
    'LinearSVC, stock price move > 1 STD',
    'LinearSVC, stock price move > 0.5 STD',
    'LinearSVC, stock price move > 0.2 STD',
    'LSTM',
    'FinBERT-tone'])

# Map selected model with the model file
model_mapping = {
    'LinearSVC, stock price move > 1 STD': 1,
    'LinearSVC, stock price move > 0.5 STD': 5,
    'LinearSVC, stock price move > 0.2 STD': 2,
    'LSTM': 7,
    'FinBERT-tone': 9}

model_choice = model_mapping[model_selected]


# Create 3 columns: Predict (width 1), Spacer (width 4), Clear All (width 2)
# You can tweak these numbers to change the sizing of the buttons
col1, col2, col3 = st.columns([4, 2, 2])

lin_svm_model_range = [1, 5, 2]
dl_model_range = [7, 8, 9]

with col1:
    if text_input.strip() == '':
        st.markdown("""
        :red[Please enter at least one headline]
        """)
    else:
        if st.button('Predict weather on the stock market', use_container_width=True, type="primary"):
            response = ''
            weather = ''

            if model_choice == 9:
                url = 'https://trading-heat-api-398091546603.europe-west1.run.app/'
                params = {
                    'headline': text_input
                }
                response = requests.get(f'{url}/dl_predict', params=params)

            elif model_choice in lin_svm_model_range or model_choice == 7:
                url = 'http://localhost:8000' # st.secrets['API_URL']
                params = {
                    'headline': text_input,
                    'model_choice': model_choice
                }

                response = requests.get(f'{url}/predict', params=params)

            if response.status_code == 200:
                prediction = response.json()
                weather = prediction['prediction']
                if weather == 1:
                    st.markdown("""
                        :red[It's likely to get hot ⚡]
                        """)
                else:
                    st.markdown("""
                        :blue[Probably it will be cold ❄️]
                                                """)

                #st.markdown(f'Predicted weather: {weather}')

            else:
                st.error(f'API call failed with status {response.status_code}: {response.text}')
# with col2:
#     st.image("images/bull-bear-fighting-vector-icon-260nw-2501263021.webp")


with col3:
    # Add the reset button using the callback
    st.button("Reset", on_click=reset_all_inputs, use_container_width=True, type='secondary')




st.text('')


# Create 3 columns where the middle one holds the image
# Adjust the weights [1, 2, 1] to make the image column wider or narrower
# left_co, cent_co, right_co = st.columns([4, 1, 2])

# with left_co:
#     st.image("images/bull-bear-fighting-vector-icon-260nw-2501263021.webp")

st.text('')
st.image("images/bull-bear_pr_background_removed.png", width="stretch")
