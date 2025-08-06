import streamlit as st
import pandas as pd
import plotly.express as px

def show_summary(df: pd.DataFrame):
    st.header("📈 Network Summary")

    if df.empty:
        st.warning("⚠️ Data belum tersedia.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total Packets", f"{len(df):,}")
    col2.metric("🔁 Unique Source IPs", df['src'].nunique())
    col3.metric("🎯 Unique Destination IPs", df['dst'].nunique())
    col4.metric("📡 Unique Protocols", df['protocol'].nunique() if 'protocol' in df.columns else "-")

    st.subheader("📍 Top Source IPs")
    top_src = df['src'].value_counts().head(10).reset_index()
    top_src.columns = ['Source IP', 'Jumlah Paket']
    fig_src = px.bar(top_src, x='Jumlah Paket', y='Source IP', orientation='h', color='Jumlah Paket', color_continuous_scale='Blues')
    st.plotly_chart(fig_src, use_container_width=True)

    st.subheader("🎯 Top Destination Ports")
    if 'tcp_dstport' in df.columns or 'udp_dstport' in df.columns:
        port_series = pd.concat([
            df['tcp_dstport'].dropna().astype(int) if 'tcp_dstport' in df else pd.Series(dtype=int),
            df['udp_dstport'].dropna().astype(int) if 'udp_dstport' in df else pd.Series(dtype=int)
        ])
        top_ports = port_series.value_counts().head(10).reset_index()
        top_ports.columns = ['Port Tujuan', 'Jumlah Paket']
        fig_ports = px.bar(top_ports, x='Jumlah Paket', y='Port Tujuan', orientation='h', color='Jumlah Paket', color_continuous_scale='Greens')
        st.plotly_chart(fig_ports, use_container_width=True)
    else:
        st.info("Data port tidak tersedia.")

    st.subheader("📡 Protocol Distribution")
    if 'protocol' in df.columns:
        proto_counts = df['protocol'].value_counts().reset_index()
        proto_counts.columns = ['Protokol', 'Jumlah Paket']
        fig_proto = px.bar(proto_counts, x='Jumlah Paket', y='Protokol', orientation='h', color='Jumlah Paket', color_continuous_scale='Oranges')
        st.plotly_chart(fig_proto, use_container_width=True)
    else:
        st.info("Kolom 'protocol' tidak ditemukan dalam data.")

    st.subheader("⏱️ Traffic Volume per Minute")
    if 'time' in df.columns:
        df_time = df.copy()
        df_time['time'] = pd.to_datetime(df_time['time'], errors='coerce')
        df_time = df_time.dropna(subset=['time'])
        df_time['minute'] = df_time['time'].dt.floor('min')
        traffic_per_min = df_time.groupby('minute').size().reset_index(name='Packet Count')
        fig_traffic = px.line(traffic_per_min, x='minute', y='Packet Count', markers=True)
        st.plotly_chart(fig_traffic, use_container_width=True)
    else:
        st.info("Kolom 'time' tidak tersedia dalam data.")

    st.subheader("🧠 Insight & Rekomendasi")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔍 Insight:")
        st.markdown("- IP dengan paket terbanyak bisa jadi sumber serangan.")
        st.markdown("- Port yang umum (80, 443) bisa jadi target serangan.")
    with col2:
        st.markdown("#### 🛡️ Action Plan:")
        st.markdown("- Lakukan blocking/scrubbing pada IP abnormal.")
        st.markdown("- Monitor port aktif dan protokol dominan.")
