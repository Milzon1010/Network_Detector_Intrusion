# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
import pandas as pd
import base64
import tempfile
from pathlib import Path

# === SET PAGE TITLE ===
st.set_page_config(page_title="Network Intrusion Detector Dashboard", layout="wide")

sys.path.append(".")

from core.auto_parser import parse_pcap_auto
from pages.Analysis_Summary import show_analysis_summary
from pages.Anomaly_Detection import show_anomaly_detection
from pages.PCA_Analysis import show_pca_visualization
from pages.Summary import show_summary

# ===== DEBUG STARTUP LOG =====
st.markdown("✅ App started (milzon debug)")
st.markdown("### 📂 File di direktori saat ini:")
try:
    st.code("\n".join(os.listdir(".")))
except Exception as e:
    st.error(f"Gagal list root dir: {e}")

if os.path.exists("assets"):
    st.markdown("### 📁 Isi folder /assets:")
    try:
        st.code("\n".join(os.listdir("assets")))
    except Exception as e:
        st.error(f"Gagal list isi assets/: {e}")
else:
    st.warning("❗ Folder assets tidak ditemukan!")


# === BACKGROUND IMAGE SETUP ===
background_image_path = "assets/background_NIDS.jpg"

if os.path.exists(background_image_path):
    with open(background_image_path, "rb") as img_file:
        img_bytes = img_file.read()
        img_base64 = base64.b64encode(img_bytes).decode()

    # ⬇️ TIDAK BOLEH ADA INDENT DI SINI
    st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{img_base64}");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-position: center;
}}
section[data-testid="stSidebar"] > div:first-child {{
    background-color: rgba(0, 24, 48, 0.85);
}}
section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span {{
    color: #ffeb8a !important;
}}
h1, h2, h3, h4 {{
    color: #ffffff !important;
    text-shadow: 2px 2px 5px black;
}}
p, li, span {{
    color: #f0f0f0 !important;
    text-shadow: 1px 1px 2px black;
}}
.upload-box {{
    background-color: rgba(0,0,0,0.6);
    padding: 2rem;
    border-radius: 12px;
    width: 40%;
    margin-left: 1rem;
    box-shadow: 0 0 15px rgba(0,0,0,0.4);
}}
</style>
""", unsafe_allow_html=True)
else:
    st.warning("⚠️ Background image tidak ditemukan.")

# === SIDEBAR NAVIGASI ===
st.sidebar.title("Navigasi Halaman")
page = st.sidebar.radio("Pilih halaman:", (
    "Upload & Home",
    "Analysis Summary",
    "Anomaly Detection",
    "PCA Analysis",
    "Summary"
))

# === INIT SESSION STATE DF ===
if "df" not in st.session_state:
    st.session_state["df"] = pd.DataFrame()

# === UPLOAD & HOME ===
if page == "Upload & Home":
    st.markdown("<h1 style='text-align: left;'>📁 Network Intrusion Detection<br>Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("Silakan upload file <code>.pcap</code>, <code>.pcapng</code>, atau <code>.csv</code> untuk memulai analisis.", unsafe_allow_html=True)

    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload file:",
        type=["pcap", "pcapng", "csv"],
        help="Limit 200MB per file – PCAP, PCAPNG, CSV"
    )

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        df = parse_pcap_auto(tmp_path)

        if df is not None and not df.empty:
            st.session_state["df"] = df
            st.success(f"✅ File berhasil diproses! Jumlah baris: {len(df)}")
            st.markdown("### Contoh Data:")
            st.dataframe(df.head(10), use_container_width=True)
        else:
            st.error("❌ Gagal memproses file atau data kosong.")
    st.markdown('</div>', unsafe_allow_html=True)

# === ANALYSIS SUMMARY ===
elif page == "Analysis Summary":
    if st.session_state["df"].empty:
        st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
    else:
        show_analysis_summary()

# === ANOMALY DETECTION ===
elif page == "Anomaly Detection":
    df = st.session_state.get("df", pd.DataFrame())
    if df.empty:
        st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
    else:
        show_anomaly_detection(df)

# === PCA ANALYSIS ===
elif page == "PCA Analysis":
    df = st.session_state.get("df", pd.DataFrame())
    if df.empty:
        st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
    else:
        show_pca_visualization(df)

# === SUMMARY ===
elif page == "Summary":
    if st.session_state["df"].empty:
        st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
    else:
        show_summary(st.session_state["df"])

# ✅ NID_ Milzon-QG-Ramin, Aug 2025
