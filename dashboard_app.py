# pages/Summary.py

import streamlit as st
import pandas as pd
import plotly.express as px


def run():
    st.header("📈 Network Summary")

    if 'df' not in st.session_state or st.session_state['df'].empty:
        st.warning("⚠️ Data belum tersedia. Silakan upload file terlebih dahulu di halaman utama.")
        st.stop()

    df = st.session_state['df']

    # METRIC HEADER
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total Packets", f"{len(df):,}")
    col2.metric("🔁 Unique Source IPs", df['src'].nunique())
    col3.metric("🎯 Unique Destination IPs", df['dst'].nunique())
    col4.metric("📡 Unique Protocols", df['protocol'].nunique() if 'protocol' in df.columns else "-")

    # CHARTS 2x2
    colA, colB = st.columns(2)

    # 1️⃣ Top Source IPs
    with colA:
        st.subheader("📍 Top Source IPs")
        top_src = df['src'].value_counts().head(10).reset_index()
        top_src.columns = ['Source IP', 'Jumlah Paket']
        if not top_src.empty:
            fig_src = px.bar(
                top_src, x='Jumlah Paket', y='Source IP', orientation='h', color='Jumlah Paket',
                color_continuous_scale='Blues', height=350
            )
            fig_src.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_src, use_container_width=True)
        else:
            st.info("Data source IP tidak tersedia.")

    # 2️⃣ Top Destination Ports
    with colB:
        st.subheader("🎯 Top Destination Ports")
        port_series = pd.concat([
            df['tcp_dstport'].dropna().astype(int) if 'tcp_dstport' in df else pd.Series(dtype=int),
            df['udp_dstport'].dropna().astype(int) if 'udp_dstport' in df else pd.Series(dtype=int)
        ])
        top_ports = port_series.value_counts().head(10).reset_index()
        top_ports.columns = ['Port Tujuan', 'Jumlah Paket']
        if not top_ports.empty:
            fig_ports = px.bar(
                top_ports, x='Jumlah Paket', y='Port Tujuan', orientation='h', color='Jumlah Paket',
                color_continuous_scale='Greens', height=350
            )
            fig_ports.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_ports, use_container_width=True)
        else:
            st.info("Data port tidak tersedia.")

    # 3️⃣ Protocol Distribution
    with colA:
        st.subheader("📡 Protocol Distribution")
        if 'protocol' in df.columns:
            proto_counts = df['protocol'].value_counts().reset_index()
            proto_counts.columns = ['Protokol', 'Jumlah Paket']
            fig_proto = px.bar(
                proto_counts, x='Jumlah Paket', y='Protokol', orientation='h', color='Jumlah Paket',
                color_continuous_scale='Oranges', height=350
            )
            fig_proto.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_proto, use_container_width=True)
        else:
            st.info("Kolom 'protocol' tidak tersedia dalam data.")

    # 4️⃣ Traffic Volume per Minute
    with colB:
        st.subheader("⏱️ Traffic Volume per Minute")
        if 'time' in df.columns:
            df_time = df.copy()
            df_time['time'] = pd.to_datetime(df_time['time'], errors='coerce')
            df_time = df_time.dropna(subset=['time'])
            df_time['minute'] = df_time['time'].dt.floor('T')
            traffic_per_min = df_time.groupby('minute').size().reset_index(name='Packet Count')
            if not traffic_per_min.empty:
                fig_traffic = px.line(
                    traffic_per_min, x='minute', y='Packet Count', markers=True,
                    line_shape='spline', render_mode='svg', height=350
                )
                fig_traffic.update_layout(margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_traffic, use_container_width=True)
            else:
                st.info("Data waktu kosong.")
        else:
            st.info("Kolom 'time' tidak tersedia dalam data.")
