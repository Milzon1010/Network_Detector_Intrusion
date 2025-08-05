import streamlit as st
import pandas as pd
import os
import base64
import tempfile
from pathlib import Path

from core.auto_parser import parse_pcap_auto
from pages.Analysis_Summary import run as show_analysis_summary
from pages.Anomaly_Detection import show_anomaly_detection
from pages.PCA_Analysis import show_pca_visualization
from pages.Summary import show_summary

background_image = "background_nid.jpg"

if os.path.exists(background_image):
    with open(background_image, "rb") as img_file:
        img_bytes = img_file.read()
        img_base64 = base64.b64encode(img_bytes).decode()

    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
    }}
    .stApp > div:first-child {{
        background-color: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(4px);
        padding: 2rem;
        border-radius: 12px;
        margin-left: 0 !important;
        text-align: left !important;
    }}
    section[data-testid="stSidebar"] > div:first-child {{
        background-color: rgba(30, 30, 30, 0.8);
        color: white;
    }}
    h1, h2, h3, h4 {{
        color: #fff !important;
        text-shadow: 1px 1px 4px black;
    }}
    p, li {{
        color: #f0f0f0 !important;
        text-shadow: 1px 1px 2px black;
    }}
    .stMarkdown span {{
        text-shadow: 1px 1px 2px black;
    }}
    .stButton > button, .stDownloadButton > button {{
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        background-color: #1666a2;
    }}
    </style>
    """, unsafe_allow_html=True)

st.sidebar.title("📂 Navigasi Halaman")
page = st.sidebar.radio("Pilih halaman:", ("Upload & Home", "Analysis Summary", "Anomaly Detection", "PCA Analysis", "Summary"))

if "df" not in st.session_state:
    st.session_state["df"] = pd.DataFrame()

col1, _ = st.columns([0.65, 0.35])
with col1:
    if page == "Upload & Home":
        st.title("📁 Network Intrusion Detection Dashboard")
        st.markdown("Silakan upload file .pcap atau .csv untuk mulai analisis.")

        uploaded_file = st.file_uploader("Upload file PCAP atau CSV:", type=["pcap", "pcapng", "csv"])

        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            df = parse_pcap_auto(tmp_path)

            if df is not None and not df.empty:
                st.session_state["df"] = df
                st.success(f"✅ File berhasil diproses! Jumlah baris: {len(df)}")
            else:
                st.error("❌ Gagal memproses file atau data kosong.")

    elif page == "Analysis Summary":
        if st.session_state["df"].empty:
            st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
        else:
            show_analysis_summary()

    elif page == "Anomaly Detection":
        if st.session_state["df"].empty:
            st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
        else:
            show_anomaly_detection(st.session_state["df"])

    elif page == "PCA Analysis":
        if st.session_state["df"].empty:
            st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
        else:
            show_pca_visualization(st.session_state["df"])

    elif page == "Summary":
        if st.session_state["df"].empty:
            st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
        else:
            show_summary(st.session_state["df"])