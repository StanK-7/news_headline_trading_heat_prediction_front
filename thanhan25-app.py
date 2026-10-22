import streamlit as st
import requests
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Stock Market Weather Forecaster",
    layout="wide",
    page_icon=""
)

# --- API URLs ---
SVC_API_URL = "https://stockapi3linsvm-241812484319.europe-west1.run.app"
DL_API_URL = "https://trading-heat-api-398091546603.europe-west1.run.app"

# --- Custom CSS ---
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    /* Header styling */
    .header-container {
        background: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .header-title {
        color: #2d3748;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        color: #718096;
        font-size: 1.1rem;
        margin-top: 10px;
    }

    /* Result boxes */
    .result-card {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    .hot-prediction {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
    }
    .cold-prediction {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
    }
    .prediction-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .prediction-confidence {
        font-size: 1.2rem;
        opacity: 0.95;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        padding: 12px 24px;
    }

    /* Metric cards */
    .metric-card {
        background: #f7fafc;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2d3748;
    }
    .metric-label {
        color: #718096;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
<div class="header-container">
    <h1 class="header-title"> Stock Market Weather Forecaster</h1>
    <p class="header-subtitle"> Enter news headlines below to predict market sentiment 🐻</p>
</div>
""", unsafe_allow_html=True)

# --- Session State ---
if "num_inputs" not in st.session_state:
    st.session_state.num_inputs = 3

# --- Callbacks ---
def check_last_input():
    last_index = st.session_state.num_inputs - 2
    if st.session_state.get(f"input_{last_index}"):
        st.session_state.num_inputs += 1

def reset_all_inputs():
    for i in range(st.session_state.num_inputs):
        key = f"input_{i}"
        if key in st.session_state:
            st.session_state[key] = ""
    st.session_state.num_inputs = 3

# --- Input Section ---
with st.container():
    st.markdown("### 📰 Enter News Headlines")
    st.markdown("*Combine multiple headlines for a comprehensive market view*")
    st.markdown("")

    for i in range(st.session_state.num_inputs):
        is_last = (i == st.session_state.num_inputs - 2)
        st.text_input(
            label=f"Headline {i+1}",
            key=f"input_{i}",
            placeholder=f"Enter headline {i+1}...",
            on_change=check_last_input if is_last else None,
            label_visibility="collapsed"
        )

# Gather inputs
all_inputs_list = [st.session_state.get(f"input_{i}", "") for i in range(st.session_state.num_inputs)]
text_input = ' '.join([x for x in all_inputs_list if x.strip()])

# --- Controls ---
st.markdown("")
col_select, col_btn, col_reset = st.columns([2, 1, 1])

with col_select:
    model_choice = st.selectbox(
        ' Select Traditional ML Model',
        [
            'LinearSVC, stock price move > 1 STD',
            'LinearSVC, stock price move > 0.5 STD',
            'LinearSVC, stock price move > 0.2 STD'
        ]
    )

with col_btn:
    predict_clicked = st.button('️ Predict Weather', type="primary", use_container_width=True)

with col_reset:
    if st.button('🔄 Reset', use_container_width=True):
        reset_all_inputs()
        st.rerun()

st.markdown("")
st.markdown("---")
st.markdown("")

# --- Prediction Results ---
if predict_clicked:
    if not text_input.strip():
        st.error("⚠️ **Please enter at least one headline**")
    else:
        # Create two columns for side-by-side comparison
        svc_col, dl_col = st.columns(2)

        # ==================== SVC MODEL ====================
        with svc_col:
            st.markdown("### 🤖 Traditional ML (SVC)")
            st.caption(f"Model: {model_choice}")

            model_code_map = {
                'LinearSVC, stock price move > 1 STD': 1,
                'LinearSVC, stock price move > 0.5 STD': 0.5,
                'LinearSVC, stock price move > 0.2 STD': 0.2
            }
            model_code = model_code_map[model_choice]

            try:
                with st.spinner("Analyzing with SVC model..."):
                    params = {
                        'headline': text_input,
                        'model_choice': model_code
                    }
                    response = requests.get(f'{SVC_API_URL}/predict', params=params, timeout=10)

                    if response.status_code == 200:
                        prediction = response.json()
                        val = float(prediction.get('prediction', 0))

                        if val >= 1.0:
                            st.markdown("""
                            <div class="result-card">
                                <div class="hot-prediction">
                                    <div class="prediction-title">🔥 HOT</div>
                                    <div>Market volatility expected</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div class="result-card">
                                <div class="cold-prediction">
                                    <div class="prediction-title">❄️ COLD</div>
                                    <div>Market likely stable</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error(f"⚠️ SVC API Error: {response.status_code}")
                        st.code(response.text)

            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Connection failed: {str(e)}")

        # ==================== DEEP LEARNING MODEL ====================
        with dl_col:
            st.markdown("### 🧠 Deep Learning (FinBERT-tone)")
            st.caption("Fine-tuned on 200k financial samples")

            try:
                with st.spinner("Analyzing with FinBERT..."):
                    payload = {
                        "headline": text_input,
                        "summary": ""
                    }
                    response = requests.post(f'{DL_API_URL}/dl_predict', json=payload, timeout=10)

                    if response.status_code == 200:
                        data = response.json()
                        label = data.get('label', 'unknown').upper()
                        probs = data.get('probabilities', {})
                        prob_hot = data.get('prob_hot', 0)

                        # Display main prediction
                        if label == 'HOT':
                            st.markdown(f"""
                            <div class="result-card">
                                <div class="hot-prediction">
                                    <div class="prediction-title"> {label}</div>
                                    <div class="prediction-confidence">Confidence: {prob_hot*100:.1f}%</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            prob_cold = 1 - prob_hot
                            st.markdown(f"""
                            <div class="result-card">
                                <div class="cold-prediction">
                                    <div class="prediction-title">❄️ {label}</div>
                                    <div class="prediction-confidence">Confidence: {prob_cold*100:.1f}%</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        # Display 3-class probability breakdown
                        st.markdown("#### 📊 3-Class Probability Breakdown")

                        # Create DataFrame for the 3 classes
                        chart_data = pd.DataFrame({
                            'Class': ['Cold', 'Hot (Rising)', 'Hot (Falling)'],
                            'Probability': [
                                probs.get('cold', 0),
                                probs.get('hot_rising', 0),
                                probs.get('hot_falling', 0)
                            ]
                        }).set_index('Class')

                        # Display metrics in columns
                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric(
                                label="❄️ Cold",
                                value=f"{probs.get('cold', 0)*100:.1f}%"
                            )
                        with m2:
                            st.metric(
                                label="📈 Hot Rising",
                                value=f"{probs.get('hot_rising', 0)*100:.1f}%"
                            )
                        with m3:
                            st.metric(
                                label="📉 Hot Falling",
                                value=f"{probs.get('hot_falling', 0)*100:.1f}%"
                            )

                        # Display bar chart
                        st.bar_chart(chart_data, use_container_width=True)

                        # Show detailed probabilities
                        with st.expander("📋 View Detailed Probabilities"):
                            st.json({
                                "Cold": f"{probs.get('cold', 0)*100:.2f}%",
                                "Hot (Rising)": f"{probs.get('hot_rising', 0)*100:.2f}%",
                                "Hot (Falling)": f"{probs.get('hot_falling', 0)*100:.2f}%",
                                "Total Hot": f"{prob_hot*100:.2f}%"
                            })

                    else:
                        st.error(f"⚠️ DL API Error: {response.status_code}")
                        st.code(response.text)

            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Connection failed: {str(e)}")

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: rgba(255,255,255,0.8); padding: 20px;'>
        <p>Built with ❤️ for Wagon Bootcamp | Powered by FinBERT & LinearSVC</p>
    </div>
    """,
    unsafe_allow_html=True
)
