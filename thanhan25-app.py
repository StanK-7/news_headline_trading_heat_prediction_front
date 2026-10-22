import streamlit as st
import requests
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Stock Market Weather Forecaster",
    layout="wide",
    page_icon="🔮"
)

# --- API URLs (Loaded from secrets with fallback) ---
# If secrets.toml exists, it uses those values. Otherwise, it uses the fallback URLs.
SVC_API_URL = st.secrets.get("SVC_API_URL", "https://stockapi3linsvm-241812484319.europe-west1.run.app")
DL_API_URL = st.secrets.get("DL_API_URL", "https://trading-heat-api-398091546603.europe-west1.run.app")

# --- Header ---
st.title("🔮 Stock Market Weather Forecaster")
st.caption("🐂 Enter news headlines below to predict market sentiment 🐻")
st.divider()

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
st.subheader("📰 Enter News Headlines")
st.caption("Combine multiple headlines for a comprehensive market view.")

for i in range(st.session_state.num_inputs):
    is_last = (i == st.session_state.num_inputs - 2)
    st.text_input(
        label=f"Headline {i+1}",
        key=f"input_{i}",
        placeholder=f"e.g., Apple announces record-breaking quarterly profits...",
        on_change=check_last_input if is_last else None,
        label_visibility="collapsed"
    )

st.subheader("📝 Summary (Optional)")
st.caption("Add a brief summary of the news for more context.")
summary_input = st.text_area(
    label="Summary",
    key="summary_input",
    placeholder="e.g., The company reported strong earnings driven by increased consumer demand...",
    height=80,
    label_visibility="collapsed"
)

# Gather inputs
all_inputs_list = [st.session_state.get(f"input_{i}", "") for i in range(st.session_state.num_inputs)]
text_input = ' '.join([x for x in all_inputs_list if x.strip()])

# --- Controls ---
st.divider()
col_select, col_btn, col_reset = st.columns([3, 1.5, 1])

with col_select:
    model_choice_label = st.selectbox(
        '🤖 Select Traditional ML Model (SVC)',
        [
            'LinearSVC, stock price move > 1 STD',
            'LinearSVC, stock price move > 0.5 STD',
            'LinearSVC, stock price move > 0.2 STD'
        ]
    )

# Map labels to the actual values your API expects
model_code_map = {
    'LinearSVC, stock price move > 1 STD': 1,
    'LinearSVC, stock price move > 0.5 STD': 0.5,
    'LinearSVC, stock price move > 0.2 STD': 0.2
}

with col_btn:
    predict_clicked = st.button('🌦️ Predict Weather', type="primary", use_container_width=True)

with col_reset:
    if st.button('🔄 Reset', use_container_width=True):
        reset_all_inputs()
        st.rerun()

st.divider()

# --- Prediction Results ---
if predict_clicked:
    if not text_input.strip():
        st.error("️ Please enter at least one headline.")
    else:
        svc_col, dl_col = st.columns(2)

        # ==================== SVC MODEL ====================
        with svc_col:
            st.subheader("🤖 Traditional ML (SVC)")
            st.caption(f"Model: {model_choice_label}")

            model_code = model_code_map[model_choice_label]

            try:
                with st.spinner("Analyzing with SVC model..."):
                    params = {
                        'headline': text_input,
                        'model_choice': model_code
                    }
                    response = requests.get(f'{SVC_API_URL}/predict', params=params, timeout=15)

                    if response.status_code == 200:
                        prediction = response.json()
                        val = float(prediction.get('prediction', 0))

                        if val >= 1.0:
                            st.success("🔥 **It's going to be HOT** - Market volatility expected")
                        else:
                            st.info("❄️ **It will be COLD** - Market likely stable")
                    else:
                        st.error(f"⚠️ SVC API Error: {response.status_code}")
                        st.code(response.text)

            except requests.exceptions.RequestException as e:
                st.error(f"️ Connection failed: {str(e)}")

        # ==================== DEEP LEARNING MODEL ====================
        with dl_col:
            st.subheader(" Deep Learning (FinBERT-tone)")
            st.caption("Fine-tuned on 200,000 financial samples")

            try:
                with st.spinner("Analyzing with FinBERT..."):
                    payload = {
                        "headline": text_input,
                        "summary": summary_input if summary_input else ""
                    }
                    response = requests.post(f'{DL_API_URL}/dl_predict', json=payload, timeout=15)

                    if response.status_code == 200:
                        data = response.json()
                        label = data.get('label', 'unknown').upper()
                        probs = data.get('probabilities', {})
                        prob_hot = data.get('prob_hot', 0)

                        p_cold = probs.get('cold', 0)
                        p_rising = probs.get('hot_rising', 0)
                        p_falling = probs.get('hot_falling', 0)

                        # Main prediction
                        if label == 'HOT':
                            st.success(f"🔥 **Prediction: {label}** (Confidence: {prob_hot*100:.1f}%)")
                        else:
                            st.info(f"❄️ **Prediction: {label}** (Confidence: {(1-prob_hot)*100:.1f}%)")

                        # 3-Class Probability Breakdown using native Streamlit components
                        st.markdown("#### 📊 3-Class Probability Breakdown")

                        st.markdown("**❄️ Cold**")
                        st.progress(p_cold, text=f"{p_cold*100:.1f}%")

                        st.markdown("**📈 Hot (Rising)**")
                        st.progress(p_rising, text=f"{p_rising*100:.1f}%")

                        st.markdown("** Hot (Falling)**")
                        st.progress(p_falling, text=f"{p_falling*100:.1f}%")

                        # Native 3-class prediction
                        native_class = data.get('native_3class', 'cold')
                        st.markdown(f"**Most likely class:** {native_class.replace('_', ' ').title()}")

                        # Detailed JSON in expander
                        with st.expander("📋 View Raw Probabilities"):
                            st.json({
                                "prediction": label,
                                "confidence": f"{prob_hot*100:.2f}%" if label == "HOT" else f"{(1-prob_hot)*100:.2f}%",
                                "cold": f"{p_cold*100:.2f}%",
                                "hot_rising": f"{p_rising*100:.2f}%",
                                "hot_falling": f"{p_falling*100:.2f}%",
                                "total_hot": f"{prob_hot*100:.2f}%"
                            })

                    else:
                        st.error(f"⚠️ DL API Error: {response.status_code}")
                        st.code(response.text)

            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ Connection failed: {str(e)}")

# --- Footer ---
st.divider()
st.caption("Built with ❤️ for Wagon Bootcamp | Powered by FinBERT & LinearSVC")
