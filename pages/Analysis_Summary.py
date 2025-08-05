# pages/Analysis_Summary.py

import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile
import plotly.express as px


def run():
    st.header("📋 Analysis Summary")

    if 'df' not in st.session_state or st.session_state['df'].empty:
        st.warning("⚠️ Data belum tersedia.")
        st.stop()

    df = st.session_state['df']

    st.markdown("""
    ### 🔍 Ringkasan:
    - Total paket: **{}**
    - IP sumber unik: **{}**
    - IP tujuan unik: **{}**
    - Protokol terdeteksi: **{}**
    """.format(len(df), df['src'].nunique(), df['dst'].nunique(), df['protocol'].nunique() if 'protocol' in df.columns else 0))

    if 'length' in df.columns and 'time' in df.columns:
        st.markdown("### 📦 Distribusi Ukuran Paket (dengan smoothing)")

        df_sorted = df.sort_values(by='time')
        df_sorted['length_smooth'] = df_sorted['length'].rolling(window=10, min_periods=1).mean()

        fig = px.line(df_sorted, x='time', y='length_smooth', title='Smoothed Packet Length Over Time')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🧠 Insight:")
    st.markdown("""
    - Cek IP yang mendominasi traffic (kemungkinan DDoS/scan)
    - Protokol UDP dominan? Waspadai serangan amplifikasi
    - Banyak paket besar? Periksa exfiltration atau file transfer abnormal
    """)

    # Tombol export ke PDF
    st.subheader("📄 Export Ringkasan ke PDF")
    if "df" not in st.session_state or st.session_state["df"].empty:
        st.warning("⚠️ Data belum tersedia. Silakan upload file terlebih dahulu.")
    st.stop()

    df = st.session_state["df"]

    if st.button("📤 Export PDF"):
        pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", '', 12)
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, "Network Intrusion Detection - Ringkasan Analisa", ln=1, align='C')

    summary_text = (
        f"Total paket: {len(df)}\n"
        f"IP sumber unik: {df['src'].nunique()}\n"
        f"IP tujuan unik: {df['dst'].nunique()}\n"
        f"Protokol unik: {df['protocol'].nunique() if 'protocol' in df.columns else 0}\n\n"
        "Insight:\n"
        "- Cek IP dominan = indikasi scanning\n"
        "- Protokol UDP = potensi amplifikasi\n"
        "- Banyak paket = transfer/exfiltration\n"
    )

    pdf.multi_cell(0, 10, summary_text)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)
        with open(tmp_pdf.name, "rb") as f:
            st.download_button("⬇️ Download PDF", f, file_name="ringkasan_nid.pdf")
