import streamlit as st
import base64
import os
import tempfile

# ==== PAGE CONFIG ====
st.set_page_config(
    page_title="Network Intrusion Detector",
    layout="wide",
    page_icon="📡"
)

# ==== BACKGROUND SETUP ====
background_image = "background_nid.jpg"

if os.path.exists(background_image):
    with open(background_image, "rb") as img_file:
        img_bytes = img_file.read()
        img_base64 = base64.b64encode(img_bytes).decode()

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}

        section[data-testid="stSidebar"] > div:first-child {{
            background-color: rgba(173, 216, 230, 0.7); /* light blue-gray */
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

        .stSelectbox div[data-baseweb="select"] > div {{
            background-color: #1f77b4 !important;
            color: white !important;
        }}
        </style>
    """, unsafe_allow_html=True)
else:
    st.warning(f"⚠️ Background image not found: {background_image}")

# ==== MAIN CONTENT ====
st.title("📡 Network Intrusion Detection Dashboard")
st.markdown("""
Selamat datang! Dashboard ini dirancang untuk membantu Anda menganalisis file PCAP dan mendeteksi potensi intrusi jaringan.
""")

# ==== PAGE NAVIGATION ====
page = st.selectbox("📥 Pilih halaman analisis:", (
    "Upload & Home",
    "Analysis Summary",
    "Anomaly Detection",
    "PCA Analysis",
    "Summary"
))

if page == "Upload & Home":
    st.subheader("📤 Upload PCAP File")
    uploaded_file = st.file_uploader("Pilih file PCAP untuk dianalisis", type=["pcap", "pcapng"])

    if uploaded_file is not None:
        from core.auto_parser import parse_pcap_auto

        with st.spinner("⏳ Memproses file..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pcap") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_file_path = tmp_file.name

                st.write(f"📄 File sementara: `{tmp_file_path}`")

                df = parse_pcap_auto(tmp_file_path)
                st.session_state["df"] = df

                st.success("✅ File berhasil diproses! Silakan lanjut ke halaman analisis.")
                st.dataframe(df.head())

                # Hapus file setelah parsing sukses
                os.remove(tmp_file_path)

            except Exception as e:
                st.error(f"❌ Gagal memproses file: {e}")
    else:
        st.warning("📎 Silakan upload file terlebih dahulu.")

elif page == "Analysis Summary":
    from pages import Analysis_Summary
    Analysis_Summary.run()

elif page == "Anomaly Detection":
    from pages import Anomaly_Detection
    Anomaly_Detection.run()

elif page == "PCA Analysis":
    from pages import PCA_Analysis
    PCA_Analysis.run()

elif page == "Summary":
    from pages import Summary
    Summary.run()
