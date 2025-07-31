import streamlit as st
import pandas as pd
import numpy as np
import joblib
import pickle
from pathlib import Path

# Configure page
st.set_page_config(layout="wide", page_title="LIHTC Prediction Model")

# Apply the same styling as your main app
st.markdown("""
    <style>
        /* === Global Defaults === */
        * {
            border-radius: 4px !important;
        }

        /* === Input Styling === */
        .stButton > button,
        .stTextInput > div > div,
        .stSelectbox > div,
        .stSlider > div,
        .stCheckbox > div,
        .stRadio > div,
        .stForm,
        .stDataFrame,
        .stMetric {
            border-radius: 4px !important;
        }

        /* === Label Styling for All Common Form Inputs === */
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stCheckbox"] label,
        div[data-testid="stSlider"] label,
        div[data-testid="stRadio"] label {
            font-size: 16px !important;
            font-weight: 500 !important;
            color: #222 !important;
        }

        /* === Optional: Input text size for consistency === */
        input[type="text"] {
            font-size: 15px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Load model function
@st.cache_resource
def load_model():
    try:
        model_path = Path("pages/models/final_model.pkl")
        if model_path.exists():
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        else:
            st.error(f"Model file not found at {model_path}")
            return None
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

# Page header
st.title("LIHTC Scoring Prediction Model")

# Create main layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Model Inputs")
    st.markdown("*Enter values for each scoring criterion*")
    
    # Prediction form with your specific features
    with st.form("prediction_form"):
        st.markdown("### Scoring Criteria")
        
        # Extended Affordability Commitment (0-6.0)
        extended_affordability = st.number_input(
            "Extended Affordability Commitment",
            min_value=0.0,
            max_value=6.0,
            value=0.0,
            step=1.0,
            help="Range: 0.0 - 6.0"
        )
        if extended_affordability % 1.0 != 0:
            extended_affordability = round(extended_affordability)
            st.info(f"Rounded to: {extended_affordability}")
            st.session_state.prev_extended_affordability = extended_affordability

        # Desirable/Undesirable Activities (0-20.0)
        desirable_undesirable = st.number_input(
            "Desirable/Undesirable Activities",
            min_value=0.0,
            max_value=20.0,
            value=0.0,
            step=1.0,
            help="Range: 0.0 - 20.0"
        )
        if desirable_undesirable % 1.0 != 0:
            desirable_undesirable = round(desirable_undesirable)
            st.info(f"Rounded to: {desirable_undesirable}")
            st.session_state.prev_desirable_undesirable = desirable_undesirable
        
        # Mixed Income Development (0-1.0)
        mixed_income = st.number_input(
            "Mixed Income Development",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=1.0,
            help="Range: 0.0 - 1.0"
        )
        if mixed_income % 1.0 != 0:
            mixed_income = round(mixed_income)
            st.info(f"Rounded to: {mixed_income}")
            st.session_state.prev_mixed_income = mixed_income
        
        # Revitalization/Redevelopment Plans (0-10.0)
        revitalization = st.number_input(
            "Revitalization/Redevelopment Plans",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=1.0,
            help="Range: 0.0 - 10.0"
        )
        if revitalization % 1.0 != 0:
            revitalization = round(revitalization)
            st.info(f"Rounded to: {revitalization}")
            st.session_state.prev_revitalization = revitalization
        
        # Deeper Targeting/Rent/Income Restrictions (0-3.0)
        deeper_targeting = st.number_input(
            "Deeper Targeting/Rent/Income Restrictions",
            min_value=0.0,
            max_value=3.0,
            value=0.0,
            step=1.0,
            help="Range: 0.0 - 3.0"
        )
        if deeper_targeting % 1.0 != 0:
            deeper_targeting = round(deeper_targeting)
            st.info(f"Rounded to: {deeper_targeting}")
            st.session_state.prev_deeper_targeting = deeper_targeting
        
        # Favorable Financing (0-5.0)
        favorable_financing = st.number_input(
            "Favorable Financing",
            min_value=0.0,
            max_value=5.0,
            value=0.0,
            step=0.5,
            help="Range: 0.0 - 5.0"
        )
        if favorable_financing % 0.5 != 0:
            favorable_financing = round(favorable_financing * 2) / 2.0
            st.info(f"Rounded to: {favorable_financing}")
            st.session_state.prev_favorable_financing = favorable_financing
        
        # Community Transportation Options (0-6.0)
        community_transportation = st.number_input(
            "Community Transportation Options",
            min_value=0.0,
            max_value=6.0,
            value=0.0,
            step=0.5,
            help="Range: 0.0 - 6.0"
        )
        if community_transportation % 0.5 != 0:
            community_transportation = round(community_transportation * 2) / 2.0
            st.info(f"Rounded to: {community_transportation}")
            st.session_state.prev_community_transportation = community_transportation
        
        predict_button = st.form_submit_button("Generate Prediction", use_container_width=True)
    
    # Handle prediction
    if predict_button:
        with st.spinner("Running XGBoost prediction..."):
            # Load the model
            model = load_model()
            
            if model is not None:
                try:
                    # Prepare input features
                    features = np.array([[
                        extended_affordability,
                        desirable_undesirable,
                        mixed_income,
                        revitalization,
                        deeper_targeting,
                        favorable_financing,
                        community_transportation
                    ]])
                    
                    # Make prediction
                    prediction = model.predict(features)[0]
                    confidence = model.predict_proba(features)[0]

                    # Store results in session state
                    st.session_state.prediction_result = prediction
                    st.session_state.prediction_confidence = confidence
                    st.session_state.input_features = {
                        "Extended Affordability Commitment": extended_affordability,
                        "Desirable/Undesirable Activities": desirable_undesirable,
                        "Mixed Income Development": mixed_income,
                        "Revitalization/Redevelopment Plans": revitalization,
                        "Deeper Targeting/Rent/Income Restrictions": deeper_targeting,
                        "Favorable Financing": favorable_financing,
                        "Community Transportation Options": community_transportation
                    }
                    st.session_state.prediction_made = True
                    
                except Exception as e:
                    st.error(f"Error making prediction: {str(e)}")
            else:
                st.error("Model could not be loaded. Please check the model file.")

with col2:
    st.subheader("Prediction Results")
    
    if st.session_state.get("prediction_made", False):
        # Display prediction results
        st.markdown("### Model Output")
        
        result = st.session_state.get("prediction_result", 0)
        confidence = st.session_state.get("prediction_confidence", 0)

        # Calculate probability of selection based on prediction result
        if result == 1.0:
            probability_of_selection = float(confidence[prediction])
        elif result == 0.0:
            probability_of_selection = 1-float(confidence[prediction])
        else:
            probability_of_selection = 0.0  # Default for unexpected values

        st.metric("Probability of Selection", f"{probability_of_selection*100:.0f}%", help="Probability that this application will be selected for LIHTC")
        # Display input summary
        st.markdown("### Input Summary")
        input_features = st.session_state.get("input_features", {})
        
        # Create a DataFrame for better display
        input_df = pd.DataFrame([
            {"Criterion": k, "Score": v} 
            for k, v in input_features.items()
        ])
        st.dataframe(input_df, use_container_width=True, hide_index=True)
        
        # Add visualization
        st.markdown("### Score Breakdown")
        st.bar_chart(input_df.set_index('Criterion')['Score'])
        
    else:
        st.info("Enter scoring criteria values and click 'Generate Prediction' to see results.")
        
        # Show example or instructions
        st.markdown("### About the Scoring Criteria")
        
        criteria_info = {
            "Extended Affordability Commitment": "This criterion rewards projects that voluntarily commit to keeping units affordable for longer than the minimum federal requirement, supporting long-term housing stability.",
            "Desirable/Undesirable Activities": "This evaluates the site’s surrounding environment, favoring proximity to beneficial amenities (like schools or grocery stores) and penalizing proximity to harmful or incompatible uses (like industrial sites or prisons).",
            "Mixed Income Development": "Projects are encouraged to include a mix of income-restricted and market-rate units, promoting economic integration and avoiding concentrated poverty.",
            "Revitalization/Redevelopment Plans": "Developments that align with local government plans for revitalizing or redeveloping specific areas receive consideration, especially if the plan is formal, active, and includes housing.",
            "Deeper Targeting/Rent/Income Restrictions": "This criterion encourages projects to serve residents with very low incomes by setting aside units with lower rent or income thresholds than the baseline requirements.",
            "Favorable Financing": "Projects that secure advantageous funding—such as grants, below-market loans, or public subsidies—are recognized for reducing long-term financial burden and enhancing feasibility.",
            "Community Transportation Options": "This assesses whether the site is located near accessible public transportation options, supporting mobility and reducing transportation barriers for residents."
        }
        
        for criterion, description in criteria_info.items():
            with st.expander(criterion):
                st.write(description)

# Add model information section
st.markdown("---")
st.subheader("About the Model")

with st.expander("Model Details"):
    st.write("""
    **Model Type**: XGBoost Regressor
    
    **Input Features**: 7 LIHTC scoring criteria
    
    **Training Data**: Historical LIHTC applications and their scoring outcomes
    """)

with st.expander("How to Use"):
    st.write("""
    1. **Enter Scores**: Input values for each of the 7 scoring criteria using the number inputs on the left
    2. **Generate Prediction**: Click the "Generate Prediction" button to run the model
    """)

with st.expander("Score Ranges Reference"):
    st.write("""
    - **Extended Affordability Commitment**: 0.0 - 6.0
    - **Desirable/Undesirable Activities**: 0.0 - 20.0  
    - **Mixed Income Development**: 0.0 - 1.0
    - **Revitalization/Redevelopment Plans**: 0.0 - 10.0
    - **Deeper Targeting/Rent/Income Restrictions**: 0.0 - 3.0
    - **Favorable Financing**: 0.0 - 5.0
    - **Community Transportation Options**: 0.0 - 6.0
    """)