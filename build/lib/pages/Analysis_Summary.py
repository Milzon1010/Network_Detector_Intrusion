import streamlit as st
import pandas as pd
import plotly.express as px

def show_analysis_summary():
    st.header("📋 Analysis Summary")

    if 'df' not in st.session_state or st.session_state['df'].empty:
        st.warning("⚠️ Data belum tersedia.")
        st.stop()

    df = st.session_state['df']

    st.markdown(f"""
    ### 🔍 Ringkasan:
    - Total paket: **{len(df)}**
    - IP sumber unik: **{df['src'].nunique()}**
    - IP tujuan unik: **{df['dst'].nunique()}**
    - Protokol terdeteksi: **{df['protocol'].nunique() if 'protocol' in df.columns else 0}**
    """)

    if 'length' in df.columns and 'time' in df.columns:
        st.markdown("### 📦 Distribusi Ukuran Paket (dengan smoothing)")
        df_sorted = df.sort_values(by='time')
        df_sorted['length_smooth'] = df_sorted['length'].rolling(window=10, min_periods=1).mean()
        fig = px.line(df_sorted, x='time', y='length_smooth', title='Smoothed Packet Length Over Time')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("📊 Top IP Pengirim")
    top_src = df['src'].value_counts().head(10).reset_index()
    top_src.columns = ['IP Sumber', 'Jumlah Paket']
    fig2 = px.bar(top_src, x='Jumlah Paket', y='IP Sumber', orientation='h', color='Jumlah Paket', color_continuous_scale='Reds')
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 🛠️ Action Plan:")
    st.markdown("""
    - Identifikasi IP dengan jumlah paket tinggi → potensi scanning atau DDoS
    - Periksa protokol dominan → UDP tinggi? Waspada amplifikasi
    - Banyak paket besar → potensi data exfiltration atau upload file mencurigakan
    """)
