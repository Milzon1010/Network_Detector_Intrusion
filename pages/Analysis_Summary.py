# pages/Analysis_Summary.py
from __future__ import annotations
"""
Analysis Summary – cepat dan aman untuk dataset besar.

Fokus optimisasi:
- Guardrail kolom: src/dst/length/ts bisa aja gak ada → tampilkan info yang tersedia saja.
- Tabel besar diringkas: batasi baris tampilan (top-N), dan sampling untuk chart time-series.
- Konversi ts → datetime dilakukan malas (lazy) & aman.
"""

import streamlit as st
import pandas as pd

TOP_N = 15             # tampilkan maksimal 15 baris untuk tabel ringkasan
MAX_TS_ROWS = 200_000  # kalau data lebih dari ini, sample dulu sebelum bikin time-series


def _exists(df: pd.DataFrame, cols: list[str]) -> bool:
    return all(c in df.columns for c in cols)


def _maybe_to_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Konversi kolom `ts` (epoch seconds) → datetime pada kolom baru `dt`.
    Aman untuk:
      - ts non-numerik (akan di-coerce jadi NaT)
      - ts sudah bertipe datetime (hanya rename ke dt)
      - fallback membuat Series NaT sepanjang df jika terjadi error
    """
    if "ts" not in df.columns:
        return df

    s = df["ts"]

    # Jika sudah datetime, cukup rename -> dt
    if pd.api.types.is_datetime64_any_dtype(s):
        return df.rename(columns={"ts": "dt"})

    # Coba konversi epoch seconds -> datetime (coerce error -> NaT)
    try:
        ts_num = pd.to_numeric(s, errors="coerce")
        dt = pd.to_datetime(ts_num, unit="s", errors="coerce")
        return df.assign(dt=dt)
    except Exception:
        # Fallback aman: isi dt sebagai NaT sepanjang df
        return df.assign(dt=pd.Series([pd.NaT] * len(df), index=df.index))


def show_analysis_summary():
    st.subheader("📊 Analysis Summary")

    if "df" not in st.session_state or st.session_state["df"].empty:
        st.warning("⚠️ Data belum tersedia. Upload file dulu ya.")
        return

    df = st.session_state["df"]

    # ===== KPI Dasar =====
    total_rows = len(df)
    uniq_src = df["src"].nunique() if "src" in df.columns else 0
    uniq_dst = df["dst"].nunique() if "dst" in df.columns else 0
    mean_len = float(pd.to_numeric(df["length"], errors="coerce").mean()) if "length" in df.columns else 0.0
    p95_len = float(pd.to_numeric(df["length"], errors="coerce").quantile(0.95)) if "length" in df.columns else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Packets", f"{total_rows:,}")
    c2.metric("Unique Sources", f"{uniq_src:,}")
    c3.metric("Unique Destinations", f"{uniq_dst:,}")
    c4.metric("Avg Len / P95", f"{mean_len:.1f} / {p95_len:.0f}")

    st.markdown("---")

    # ===== Top Talkers (by count & bytes) =====
    if _exists(df, ["src"]):
        top_src_cnt = df.groupby("src").size().sort_values(ascending=False).head(TOP_N).rename("count")
        st.markdown("#### 🔝 Top Sources (by packets)")
        st.dataframe(top_src_cnt.reset_index(), use_container_width=True, height=360)
    else:
        st.info("Kolom `src` tidak tersedia.")

    if _exists(df, ["dst"]):
        top_dst_cnt = df.groupby("dst").size().sort_values(ascending=False).head(TOP_N).rename("count")
        st.markdown("#### 🎯 Top Destinations (by packets)")
        st.dataframe(top_dst_cnt.reset_index(), use_container_width=True, height=360)
    else:
        st.info("Kolom `dst` tidak tersedia.")

    if _exists(df, ["src", "length"]):
        top_src_bytes = (
            df.assign(length=pd.to_numeric(df["length"], errors="coerce").fillna(0))
              .groupby("src")["length"].sum().sort_values(ascending=False).head(TOP_N)
              .rename("bytes")
        )
        st.markdown("#### 📦 Top Sources (by bytes)")
        st.dataframe(top_src_bytes.reset_index(), use_container_width=True, height=360)

    if _exists(df, ["dst", "length"]):
        top_dst_bytes = (
            df.assign(length=pd.to_numeric(df["length"], errors="coerce").fillna(0))
              .groupby("dst")["length"].sum().sort_values(ascending=False).head(TOP_N)
              .rename("bytes")
        )
        st.markdown("#### 🧳 Top Destinations (by bytes)")
        st.dataframe(top_dst_bytes.reset_index(), use_container_width=True, height=360)

    st.markdown("---")

    # ===== Throughput/time-series (opsional) =====
    if "ts" in df.columns:
        st.markdown("#### ⏱️ Traffic Over Time")
        # Sampling dulu kalau baris kebanyakan biar gak lemot
        df_ts = df
        if len(df_ts) > MAX_TS_ROWS:
            st.caption(f"Sampling {MAX_TS_ROWS:,} dari {len(df_ts):,} baris untuk menjaga performa.")
            df_ts = df_ts.sample(MAX_TS_ROWS, random_state=42)

        df_ts = _maybe_to_datetime(df_ts)
        if "dt" in df_ts.columns and df_ts["dt"].notna().any():
            ts_agg = (
                df_ts[df_ts["dt"].notna()]
                .assign(length=pd.to_numeric(df_ts.get("length", pd.Series([0] * len(df_ts), index=df_ts.index)), errors="coerce").fillna(0))
                .set_index("dt")
                .resample("1min")
                .agg(packets=("length", "size"), bytes=("length", "sum"))
                .reset_index()
            )
            if not ts_agg.empty:
                st.line_chart(ts_agg.set_index("dt")[["packets", "bytes"]])
            else:
                st.info("Data time-series kosong setelah agregasi.")
        else:
            st.info("Kolom waktu tidak dapat diproses.")
    else:
        st.info("Kolom `ts` tidak tersedia, lewati grafik time-series.")
