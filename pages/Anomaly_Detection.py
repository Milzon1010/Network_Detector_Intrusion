# anomaly_detection.py
import streamlit as st
import pandas as pd

def show_anomaly_detection(df: pd.DataFrame):
    st.subheader("🚨 Anomaly Detection")

    if df.empty:
        st.warning("Data belum tersedia. Harap upload file PCAP terlebih dahulu.")
        return

    threshold = 1400
    anomalies = df[df['length'] > threshold]

    st.markdown(f"### 🔏 Threshold: Panjang paket > {threshold} bytes")
    st.markdown(f"Jumlah paket anomali: **{len(anomalies)}**")

    if len(anomalies) > 0:
        st.success("✅ Anomali terdeteksi dalam data ini.")
    else:
        st.info("🔍 Tidak ditemukan anomali berdasarkan panjang paket.")

    if not anomalies.empty:
        st.dataframe(anomalies)

    st.markdown("---")
    st.markdown("### 📊 Network Summary")
    st.dataframe(df.describe(include='all'))