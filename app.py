import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter
import ast

st.set_page_config(page_title="Churn Forecasting", layout="wide")
st.title("📉 AI Forecasting – Subscription Churn")

uploaded_file = st.file_uploader("📤 Upload Preprocessed Churn CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Parse stringified lists
    df['logins_per_month'] = df['logins_per_month'].apply(ast.literal_eval)
    df['session_durations'] = df['session_durations'].apply(ast.literal_eval)
    df['payments'] = df['payments'].apply(ast.literal_eval)

    # Convert types
    df['duration'] = df['duration'].astype(int)
    df['event_observed'] = df['event_observed'].astype(int)

    # Summary metrics
    churn_rate = 100 * df['event_observed'].mean()
    avg_duration = df['duration'].mean()

    st.metric("📉 Churn Rate", f"{churn_rate:.2f}%")
    st.metric("🕒 Avg Subscription Duration", f"{avg_duration:.0f} days")

    st.subheader("📋 Preview of Uploaded Data")
    st.dataframe(df.drop(columns=['payments']).head())


    # Prepare input
    # Drop non-numeric and text fields
    exclude_cols = ['user_id', 'signup_date', 'churn_date', 'logins_per_month', 'session_durations', 'payments']
    survival_df = df.drop(columns=[col for col in exclude_cols if col in df.columns])

    # Encode categorical columns
    survival_df = pd.get_dummies(survival_df, drop_first=True)


    # Fit Cox Model
    cph = CoxPHFitter()
    try:
        cph.fit(survival_df, duration_col='duration', event_col='event_observed')

        st.subheader("📈 Survival Curve (Top 5 Users)")
        surv_fn = cph.predict_survival_function(survival_df.iloc[:5])
        fig, ax = plt.subplots()
        surv_fn.plot(ax=ax)
        plt.title("Survival Curve (Churn Probability Over Time)")
        plt.xlabel("Days Since Signup")
        plt.ylabel("Probability of Staying Subscribed")
        plt.grid(True)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"⚠️ Error fitting survival model: {e}")
