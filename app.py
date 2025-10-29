import streamlit as st
import numpy as np
import joblib
import os
import logging
import pandas as pd
import altair as alt
import re # For Regex Validation
import hashlib # For Model Integrity Check
import json # For Model Metadata
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler # For Log Rotation
from streamlit.web.server.server_util import get_server_address 

# --- Custom Exception for Clarity ---
class SecurityError(Exception):
    """Raised when a security-critical integrity check fails (e.g., hash mismatch)."""
    pass

# --- 0. Configuration and Logging Setup ---
logger = logging.getLogger(__name__) # Use logger name for context
LOG_FILE = 'app_errors.log'

if not logging.getLogger().handlers:
    # Use RotatingFileHandler: 5MB max size, keep 3 backup files
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
    # Includes logger name and line number
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s (L:%(lineno)d)'
    logging.basicConfig(level=logging.INFO, 
                        format=log_format,
                        handlers=[handler])
    logger.info("Rotating file logging initialized.")

load_dotenv() 
MODEL_PATH = 'your_model.pkl'
META_PATH = 'model_meta.json'
REQUIRED_SECRETS = ["EXTERNAL_API_KEY"] 
# Regex to allow positive numbers (float/int)
NUMBER_REGEX = re.compile(r"^[0-9]*\.?[0-9]+$") 

# --- Helper Functions ---
def get_file_hash(path, chunk_size=65536):
    sha256 = hashlib.sha256()
    try:
        with open(path, 'rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()
    except Exception as e:
        raise RuntimeError(f"Could not read file for hashing: {e}")

@st.cache_resource
def load_model_metadata(path):
    """Loads and validates the explicit data contract."""
    try:
        with open(path, 'r') as f:
            meta = json.load(f)
        if not all(k in meta for k in ["features", "feature_count", "model_sha256_hash"]):
            raise ValueError("Metadata file is missing critical keys.")
        if len(meta["features"]) != meta["feature_count"]:
            raise ValueError("Metadata mismatch: features list length != feature_count.")
        return meta
    except Exception as e:
        logger.error(f"FATAL: Failed to load model metadata: {e}", exc_info=True)
        st.error(f"FATAL: Model Data Contract Failed. Ensure {META_PATH} is valid JSON.")
        st.stop()

# --- 1. Top-Tier Model Loading (Cached, Secure, Integrity Checked) ---
@st.cache_resource
def load_and_verify_model(path, meta):
    st.toast("Verifying Model Integrity...", icon='🛡️')
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at: {path}")

        # Integrity Hash Check (RCE Mitigation)
        file_hash = get_file_hash(path)
        known_hash = meta["model_sha256_hash"]

        if file_hash != known_hash:
            if known_hash == "REPLACE_WITH_YOUR_MODEL_SHA256":
                logger.warning("SECURITY WARNING: KNOWN_MODEL_HASH is default placeholder. Integrity check bypassed.")
            else:
                raise SecurityError(f"Model hash mismatch! Expected {known_hash[:8]}... but got {file_hash[:8]}.... File may be tampered.")

        st.toast("Loading ML Model...", icon='⏳')
        model = joblib.load(path)
        st.toast("Model Loaded Successfully.", icon='✅')
        return model
    except SecurityError as se:
        logger.error(f"Security Failure: {se}", exc_info=True)
        st.error(f"FATAL SECURITY FAILURE: {se}")
        st.stop()
    except Exception as e:
        error_msg = f"""
        FATAL: Model loading failed. Details: {e.__class__.__name__}: {e}
        ACTION REQUIRED: If corruption is suspected, run: git lfs pull --force
        """
        logger.error(error_msg, exc_info=True)
        st.error(error_msg)
        st.stop() 

# --- Execution Entry Point ---
# Security Check: Enforce loopback inside the app
server_address = get_server_address()
if server_address and server_address not in ("127.0.0.1", "localhost"):
    st.error(f"FATAL SECURITY VIOLATION: App is exposed on {server_address}. Must be run via 'make run'.")
    st.stop()

# Load Metadata first to drive logic
model_meta = load_model_metadata(META_PATH)
model = load_and_verify_model(MODEL_PATH, model_meta)

# --- Dashboard Header (Aesthetics & UX) ---
st.set_page_config(page_title="DDC Core v2.0 Failure Identifier", layout="wide", initial_sidebar_state="expanded")
st.title("🕵️ DDC Core v2.0 Failure Identifier")
st.markdown("A **Zero-Latency, Local-First** tool for predicting system failure risk based on operational parameters.")

# --- 2. Input Panel (Form Submission Pattern) ---
with st.form(key='risk_prediction_form'):
    st.subheader("⚙️ Input Parameters for Risk Assessment")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        # Input 1: Latency
        param_1_value = st.slider(
            label=model_meta["features"][0], min_value=50, max_value=300, value=120, step=5,
            help="High latency suggests message queue backlog or database strain."
        )

    with col_b:
        # Input 2: Lag Ratio (string input, requires validation)
        param_2_text = st.text_input(
            label=model_meta["features"][1], value="1.5",
            help="Ratio of consumer lag to message production rate (Normal < 1.0)."
        )

    with col_c:
        # Input 3: Health (categorical)
        param_3_value = st.radio(
            label=model_meta["features"][2],
            options=['Healthy', 'Degraded'],
            index=0, horizontal=True,
            help="Status of the primary data ingestion pipeline."
        )
        source_health_int = 1.0 if param_3_value == 'Healthy' else 0.0

    submit_button = st.form_submit_button(label='🎯 Calculate Failure Risk', type="primary")

# --- 3. Prediction and Validation Logic ---
if submit_button:
    try:
        # Regex Validation for Lag Ratio
        param_2_text_clean = param_2_text.strip()
        if not NUMBER_REGEX.match(param_2_text_clean):
            raise ValueError(f"Lag Ratio must be a positive number. Invalid input: '{param_2_text_clean}'")
        
        param_2_value = float(param_2_text_clean)

        if param_2_value < 0:
            raise ValueError("Lag Ratio must be a positive number.")
        
        # Check for NaN/Inf
        if np.isinf(param_2_value) or np.isnan(param_2_value):
            raise ValueError("Input value resulted in 'infinity' or 'NaN'. Please enter a finite number.")

        input_data = [float(param_1_value), param_2_value, source_health_int]
        
        # Runtime Feature Count Assertion using metadata
        if len(input_data) != model_meta["feature_count"]:
            raise RuntimeError(f"Model requires {model_meta['feature_count']} features (from metadata), but {len(input_data)} were provided.")
        
        features = np.array([input_data], dtype=np.float32) 
        prediction_result = model.predict(features)[0]

        # Robust Logic for Categorical, Probabilistic, and Regression
        if hasattr(model, 'predict_proba') or model_meta.get("prediction_mode_hint") == "probabilistic":
            probability_vector = model.predict_proba(features)[0]
            risk_score = probability_vector[1] * 100
            prediction_mode = "Probabilistic"
        elif isinstance(prediction_result, (float, np.floating)) and 0 < prediction_result < 1:
            risk_score = prediction_result * 100 
            prediction_mode = "Regression Score"
        else:
            risk_score = prediction_result * 100
            prediction_mode = "Categorical"
            
        # Store results
        st.session_state['predicted_risk'] = risk_score
        st.session_state['predicted_class'] = prediction_result
        st.session_state['input_vector'] = input_data
        st.session_state['input_names'] = model_meta["features"] # Use names from metadata
        st.session_state['prediction_mode'] = prediction_mode

        logger.info(f"Prediction Success: Mode={prediction_mode}, Risk={risk_score:.2f}%") # Log success
    except ValueError as ve:
        logger.warning(f"Validation Error: {ve}", exc_info=True)
        st.error(f"Validation Error: {ve}")
    except RuntimeError as re:
        logger.error(f"Model Error: {re}", exc_info=True)
        st.error(f"Model Error: {re}")
    except Exception as e:
        logger.error(f"Unhandled Prediction Error: {e}", exc_info=True)
        st.error(f"Unhandled Prediction Error: {e}")

# --- 4. Output Panel and Visualization ---
if 'predicted_risk' in st.session_state:
    try: # Try/Except to prevent partial state corruption crashes
        st.divider()
        st.subheader("📊 Final Risk Assessment & Diagnostics")
        
        risk_score = st.session_state['predicted_risk']
        
        # NaN Metric Failure Fix
        if pd.isna(risk_score):
            st.error("Prediction resulted in 'NaN'. Cannot display results.")
            st.stop()

        # Determine Metric Display
        if st.session_state['prediction_mode'] == "Categorical":
            prediction = st.session_state['predicted_class']
            risk_text = "FAILURE PREDICTED" if prediction == 1 else "STATUS: STABLE"
            st_metric_color = "inverse" if prediction == 1 else "normal"
            st_value = risk_text
            delta_text = "Mode: Hard Classifier"
        elif st.session_state['prediction_mode'] == "Regression Score":
            risk_text = "REGRESSION SCORE"
            st_metric_color = "off"
            st_value = f"{risk_score:.2f} (Raw)"
            delta_text = "Mode: Regression"
        else: # Probabilistic
            risk_text = "CRITICAL FAILURE IMMINENT" if risk_score > 70 else "HIGH RISK WARNING" if risk_score > 30 else "STATUS: STABLE"
            st_metric_color = "inverse" if risk_score > 70 else "off" if risk_score > 30 else "normal"
            st_value = f"{risk_score:.2f}%"
            delta_text = "Mode: Probabilistic"

        col_metric, col_chart = st.columns([1, 2])

        with col_metric:
            st.markdown(f"## {risk_text}")
            st.metric(
                label="Calculated Risk Score", 
                value=st_value, 
                delta_color="normal", # Do not color the delta text itself
                delta=delta_text
            )
            # Add explicit color for visual flair
            if st_metric_color == "inverse":
                st.markdown(f'<p style="color:red; font-weight:bold;">{risk_text}</p>', unsafe_allow_html=True)
            elif st_metric_color == "off":
                 st.markdown(f'<p style="color:orange; font-weight:bold;">{risk_text}</p>', unsafe_allow_html=True)
            
            st.caption("Input Vector (Based on Data Contract):")
            st.json(dict(zip(st.session_state['input_names'], st.session_state['input_vector'])))

        with col_chart:
            # Chart displays only factual data
            chart_data = pd.DataFrame({
                'Feature': st.session_state['input_names'],
                'Value': st.session_state['input_vector'],
            })
            chart = alt.Chart(chart_data).mark_bar().encode(
                y=alt.Y('Feature:N', sort='-x'),
                x='Value:Q',
                color=alt.Color('Value:Q', scale=alt.Scale(range=['#4c78a8', '#ff7f0e', 'red']), legend=None),
                tooltip=['Feature', 'Value']
            ).properties(title='Feature Inputs Profile').interactive()
            st.altair_chart(chart, use_container_width=True)

    except KeyError:
        logger.error("Session state corrupted during output render.", exc_info=True)
        st.error("Session state is corrupted. Please submit the form again.")
    except Exception as e:
        logger.error(f"Unhandled Output Render Error: {e}", exc_info=True)
        st.error(f"An unexpected error occurred while rendering the output: {e}")

# --- 5. Sidebar/Footer (Metadata and Security Status) ---
with st.sidebar:
    st.header("Deployment Status")
    st.text(f"Python Version: {os.environ.get('PYTHON_VERSION', 'UNKNOWN (Run make setup)')}") 
    
    # Enhanced Secrets Status Check
    api_key = os.getenv(REQUIRED_SECRETS[0])
    
    if not api_key:
        st.error(f"Secrets Status: Missing {REQUIRED_SECRETS[0]}")
        st.caption("Run `make setup` to create an `.env` file, then populate it.")
    elif api_key == "replace_with_your_key_for_external_service":
        st.error(f"Secrets Status: {REQUIRED_SECRETS[0]} is not populated.")
        st.caption("Please edit the `.env` file and add your key.")
    else:
        st.success("Secrets Status: ALL Keys Loaded")
        st.caption("Securely loaded from local .env file.")

    st.divider()
    st.info("Local Security: Enforced Loopback Binding (127.0.0.1)")
    hash_display = model_meta["model_sha256_hash"][:8] if model_meta["model_sha256_hash"] != "REPLACE_WITH_YOUR_MODEL_SHA256" else "PLACEHOLDER"
    st.warning(f"Model Integrity Hash: {hash_display}")
    st.warning("Cost: $0.00 (Zero Cost)")