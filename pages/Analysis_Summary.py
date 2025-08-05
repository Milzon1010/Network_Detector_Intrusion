# pages/Analysis_Summary.py

import streamlit as st
import pandas as pd
from fpdf import FPDF
import tempfile


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

    if 'length' in df.columns:
        st.markdown("### 📦 Distribusi Ukuran Paket")
        st.line_chart(df['length'].dropna())

    st.markdown("### 🧠 Insight:")
    st.markdown("""
    - Cek IP yang mendominasi traffic (kemungkinan DDoS/scan)
    - Protokol UDP dominan? Waspadai serangan amplifikasi
    - Banyak paket besar? Periksa exfiltration atau file transfer abnormal
    """)

    # Tombol export ke PDF
    st.subheader("📄 Export Ringkasan ke PDF")

    if st.button("🖨️ Export PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Network Intrusion Detection - Ringkasan Analisa", ln=True, align='C')
        pdf.ln(10)

        summary_text = f"""
        Total paket: {len(df)}
        IP sumber unik: {df['src'].nunique()}
        IP tujuan unik: {df['dst'].nunique()}
        Protokol unik: {df['protocol'].nunique() if 'protocol' in df.columns else 0}

        Insight:
        - Cek IP dominan → indikasi scanning
        - UDP dominan → potensi amplifikasi
        - Panjang paket besar → transfer/exfiltration
        """

        for line in summary_text.strip().split('\n'):
            pdf.cell(0, 10, txt=line.strip(), ln=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            pdf.output(tmp_file.name)
            st.success("✅ PDF berhasil dibuat.")
            with open(tmp_file.name, "rb") as f:
                st.download_button(label="📥 Download PDF", data=f, file_name="NID_Summary_Report.pdf", mime="application/pdf")
