# pages/03_Anomaly_Detection.py

import streamlit as st
import pandas as pd

st.header("🚨 Anomaly Detection")

if 'df' not in st.session_state or st.session_state['df'].empty:
    st.warning("⚠️ Data belum tersedia.")
    st.stop()

df = st.session_state['df']

st.subheader("📏 Threshold: Panjang paket > 1400 bytes")
anomaly_df = df[df['length'] > 1400]

st.write(f"Jumlah paket anomali: {len(anomaly_df)}")
st.dataframe(anomaly_df.head(20))

def run():
    st.header("📊 Network Summary")
    df = st.session_state['df']
    # (isi analisis kamu di sini)