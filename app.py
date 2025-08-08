# app.py
#from __future__ import annotations
####
#    NID Dashboard 

#    idenya begini?
#    - (background image, text shadow, sidebar gelap).
#    - Limit preview 100 baris di Upload/Home → mencegah UI berat di file besar.
#    - Toggle Demo Mode (env) → jaminan UI tidak kosong saat parser gagal total.
#    - Terintegrasi dengan auto_parser yang memilih CSV vs PCAP.

#    Halaman:
#   - Upload & Home: unggah file dan pratinjau 100 baris
#    - Analysis Summary: ringkasan metrik
#    - Anomaly Detection: deteksi anomali (butuh df terisi)
#    - PCA Analysis: PCA 2D (sampling otomatis)
#    - Summary: ringkasan akhir/eksport
###

import os
import sys
import base64
import tempfile
from pathlib import Path

import streamlit as st
# === PAGE CONFIG ===
st.set_page_config(page_title="Network Intrusion Detection & Analysis Dashboard", layout="wide")
import pandas as pd

# Pastikan modul lokal terdeteksi
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(".")

# Windows asyncio policy (future-proof jika ada lib yang pakai loop)
try:
    import asyncio
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
except Exception:
    pass



# === IMPORT MODUL PROYEK ===
from core.auto_parser import parse_pcap_auto
from pages.Analysis_Summary import show_analysis_summary
from pages.Anomaly_Detection import show_anomaly_detection
from pages.PCA_Analysis import show_pca_visualization
from pages.Summary import show_summary

# === BACKGROUND & THEME CSS ===
def _inject_background_css(img_path: str) -> None:
    if not os.path.exists(img_path):
        st.warning(f"⚠️ Background image tidak ditemukan di {img_path}")
        return
    with open(img_path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{b64}");
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
    margin: 1rem auto;
    box-shadow: 0 0 15px rgba(0,0,0,0.4);
}}
.center-hero {{
    text-align: center;
    padding-top: 2rem;
}}
.center-hero h1 {{
    font-size: 2.5rem;
    color: white;
    text-shadow: 2px 2px 5px black;
    margin-bottom: 0.25rem;
}}
.center-hero p {{
    font-size: 1.1rem;
    color: #ccc;
    text-shadow: 1px 1px 2px black;
    margin-top: 0rem;
}}
</style>
""", unsafe_allow_html=True)

_inject_background_css("assets/background_NIDS.jpg")

# === SIDEBAR NAV ===
st.sidebar.title("Navigasi Halaman")
page = st.sidebar.radio("Pilih halaman:", (
    "Upload & Home",
    "Analysis Summary",
    "Anomaly Detection",
    "PCA Analysis",
    "Summary",
))

# Demo mode toggle (ENV-based) → untuk presentasi
os.environ.setdefault("NID_DEMO_MODE", "0")
st.sidebar.markdown("---")
demo_checked = st.sidebar.toggle(
    "🧪 Demo Mode (isi dummy saat parsing gagal)",
    value=(os.environ.get("NID_DEMO_MODE") == "1"),
    help="Airbag untuk demo: UI tetap menampilkan data minimal jika parser gagal total."
)
if demo_checked and os.environ.get("NID_DEMO_MODE") != "1":
    os.environ["NID_DEMO_MODE"] = "1"
    st.session_state.pop("df", None)
    st.rerun()
elif (not demo_checked) and os.environ.get("NID_DEMO_MODE") != "0":
    os.environ["NID_DEMO_MODE"] = "0"
    st.session_state.pop("df", None)
    st.rerun()

# === SESSION STATE ===
if "df" not in st.session_state:
    st.session_state["df"] = pd.DataFrame()

# === PAGES ===
if page == "Upload & Home":
    # Hero title
    st.markdown("""
        <div class="center-hero">
            <h1>🛡️ Network Intrusion Detection & Analysis Dashboard</h1>
            <p>Transforming Packet Data into Actionable Security Insights</p>
        </div>
    """, unsafe_allow_html=True)

    if os.environ.get("NID_DEMO_MODE") == "1":
        st.info("🧪 Demo Mode aktif: jika parser gagal, sistem mengisi data minimal untuk demo/screenshot.")

    # Upload box
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload file (.pcap / .pcapng / .csv):",
        type=["pcap", "pcapng", "csv"],
        help="Maks 200MB per file"
    )
    if uploaded is not None:
        # Simpan ke file sementara (Streamlit memberikan file-like object)
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        # Parse otomatis (auto_parser akan memilih parser yang tepat)
        df = parse_pcap_auto(tmp_path)

        # Tampilkan hasil
        if df is not None and not df.empty:
            st.session_state["df"] = df
            st.success(f"✅ File berhasil diproses! Jumlah baris: {len(df)}")
            st.markdown("### Contoh Data (maks. 100 baris):")
            st.dataframe(df.head(100), use_container_width=True, height=360)
        else:
            st.error("❌ Gagal memproses file atau data kosong. Aktifkan Demo Mode jika perlu.")
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Analysis Summary":
    if st.session_state["df"].empty:
        st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
    else:
        show_analysis_summary()

elif page == "Anomaly Detection":
    df = st.session_state.get("df", pd.DataFrame())
    if df.empty:
        st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
    else:
        show_anomaly_detection(df)

elif page == "PCA Analysis":
    df = st.session_state.get("df", pd.DataFrame())
    if df.empty:
        st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
    else:
        show_pca_visualization(df)

elif page == "Summary":
    if st.session_state["df"].empty:
        st.warning("⚠️ Belum ada data. Silakan upload file terlebih dahulu.")
    else:
        show_summary(st.session_state["df"])


st.sidebar.markdown("""
<style>
#sidebar-watermark {
  position: fixed;
  left: 20px;          /* geser sedikit ke kanan */
  bottom: 35px;        /* naik sedikit dari bawah */
  width: 240px;
  font-size: 14px;     /* diperbesar */
  color: rgba(255,255,255,0.85);
  text-shadow: 0 1px 3px rgba(0,0,0,0.7);
  z-index: 1000;
  pointer-events: none;
}
#sidebar-watermark .badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  background: linear-gradient(90deg, #0ea5e9, #22c55e, #f59e0b);
  color: #0b1220;
  font-weight: 600;
  margin-left: 8px;
}
</style>
<div id="sidebar-watermark">
  Created by <b>MIlzon_Ramin_QarirGen</b> <span class="badge">@2025</span>
</div>
""", unsafe_allow_html=True)

