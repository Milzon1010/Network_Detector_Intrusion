# parsers/parse_pcap_tshark_ipv6.py
# from __future__ import annotations

#"""
#Parser PCAP/PCAPNG untuk NID Dashboard (aman untuk Windows + Streamlit).

#Urutan fallback:
#  1) TShark (sinkron, TSV, cepat & stabil field)
#  2) PyShark (opsional; dibatasi timeout agar tak hang)
#  3) Scapy PcapReader (streaming; low memory; backfill non-IP dengan ARP/MAC)
#  4) Demo row (opsional via env) agar UI tak blank saat presentasi

#Alasan desain:
#- Menghindari masalah asyncio ("no current event loop") di Streamlit thread.
#- Menangani output TShark yang kadang “berisik” (multi-value, koma di nilai).
#- Menjamin output schema konsisten: ["ts", "src", "dst", "length"] untuk modul
#  Analysis Summary, Anomaly Detection, dan PCA.
#"""

import io
import os
import shlex
import time
import subprocess
import pandas as pd

# ===== ENV TOGGLES =====
# ON saat demo agar UI tetap ada isi walau parsing gagal total.
DEMO_MODE = os.getenv("NID_DEMO_MODE", "0") == "1"
# OFF default (0) demi stabilitas Windows; aktifkan hanya jika perlu.
ALLOW_PYSHARK = os.getenv("NID_ALLOW_PYSHARK", "0") == "1"
# Batas waktu PyShark agar tidak hang (detik).
PYSHARK_TIMEOUT = float(os.getenv("NID_PYSHARK_TIMEOUT", "5"))

# ===== UTIL =====
def _safe_series(df: pd.DataFrame, col: str) -> pd.Series:
    """Selalu balikan Series berukuran len(df). Jika kolom hilang → Series NA."""
    if col in df.columns:
        s = df[col]
        return s if isinstance(s, pd.Series) else pd.Series([pd.NA] * len(df))
    return pd.Series([pd.NA] * len(df))

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalisasi ke schema final:
      - ts: float64 (frame.time_epoch → numeric)
      - src/dst: gabungan IPv4/IPv6 (ip.src/ip.dst vs ipv6.src/ipv6.dst)
      - length: Int64 (frame.len → numeric; isi 0 kalau kosong)
    Buang baris tanpa src/dst (tidak berguna untuk analitik).
    """
    ts = pd.to_numeric(_safe_series(df, "frame.time_epoch"), errors="coerce")

    ip_src   = _safe_series(df, "ip.src")
    ipv6_src = _safe_series(df, "ipv6.src")
    src = ip_src.fillna(ipv6_src)

    ip_dst   = _safe_series(df, "ip.dst")
    ipv6_dst = _safe_series(df, "ipv6.dst")
    dst = ip_dst.fillna(ipv6_dst)

    length = pd.to_numeric(_safe_series(df, "frame.len"), errors="coerce")

    out = pd.DataFrame({"ts": ts, "src": src, "dst": dst, "length": length})
    out = out.dropna(subset=["src", "dst"]).reset_index(drop=True)
    out["ts"] = out["ts"].astype("float64")
    out["length"] = out["length"].fillna(0).astype("Int64")
    return out[["ts", "src", "dst", "length"]]

# ===== TSHARK (PRIORITAS UTAMA) =====
def _parse_with_tshark(path: str) -> pd.DataFrame:
    """
    Kenapa duluan? Cepat & deterministik untuk fields tertentu.
    Trik stabilitas:
      - separator=\t (hindari koma dalam nilai)
      - occurrence=f (ambil first occurrence saat multi-value)
      - quote=d (nilai “aneh” tetap parseable)
    """
    cmd = (
        'tshark -r "{p}" -T fields '
        '-e frame.time_epoch -e ip.src -e ip.dst -e ipv6.src -e ipv6.dst -e frame.len '
        '-E header=y -E separator=\t -E occurrence=f -E quote=d'
    ).format(p=path)

    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout.strip():
        return pd.DataFrame()

    try:
        df = pd.read_csv(io.StringIO(proc.stdout), sep="\t")
    except Exception:
        df = pd.read_csv(io.StringIO(proc.stdout), sep="\t", engine="python")

    try:
        return _normalize_columns(df)
    except Exception:
        return pd.DataFrame()

# ===== PYSHARK (OPSIONAL, TIMEOUT) =====
def _parse_with_pyshark(path: str) -> pd.DataFrame:
    """
    Default dimatikan (ALLOW_PYSHARK=0) demi stabilitas Windows.
    Saat diaktifkan, parsing dibatasi waktu untuk menghindari hang.
    """
    if not ALLOW_PYSHARK:
        return pd.DataFrame()

    try:
        import pyshark  # type: ignore
    except Exception:
        return pd.DataFrame()

    rows = []
    start = time.time()
    cap = pyshark.FileCapture(path, only_summaries=False)
    try:
        for pkt in cap:
            if time.time() - start > PYSHARK_TIMEOUT:
                raise TimeoutError("PyShark parsing timeout")

            try:
                ts = float(getattr(pkt, "sniff_timestamp", None) or "nan")

                # frame.len (best effort)
                length = None
                if hasattr(pkt, "frame_info") and hasattr(pkt.frame_info, "len"):
                    try:
                        length = int(pkt.frame_info.len)
                    except Exception:
                        length = None

                # IPv4/IPv6 src/dst
                src = dst = None
                if hasattr(pkt, "ip"):
                    src = getattr(pkt.ip, "src", None)
                    dst = getattr(pkt.ip, "dst", None)
                if (src is None or dst is None) and hasattr(pkt, "ipv6"):
                    src = src or getattr(pkt.ipv6, "src", None)
                    dst = dst or getattr(pkt.ipv6, "dst", None)

                if src or dst:
                    rows.append({
                        "frame.time_epoch": ts,
                        "ip.src": src,
                        "ip.dst": dst,
                        "frame.len": length
                    })
            except Exception:
                continue
    finally:
        try:
            cap.close()
        except Exception:
            pass

    if not rows:
        return pd.DataFrame()
    return _normalize_columns(pd.DataFrame(rows))

# ===== SCAPY PCAPREADER (STREAMING) =====
def _parse_with_scapy(path: str) -> pd.DataFrame:
    """
    Streaming reader → tidak load seluruh file ke RAM.
    Jika tidak ada layer IP/IPv6, fallback pakai ARP atau Ethernet MAC agar src/dst tetap terisi.
    """
    try:
        from scapy.utils import PcapReader  # type: ignore
        from scapy.layers.inet import IP  # type: ignore
        from scapy.layers.inet6 import IPv6  # type: ignore
        from scapy.layers.l2 import ARP, Ether  # type: ignore
    except Exception:
        return pd.DataFrame()

    rows = []
    try:
        with PcapReader(path) as pr:
            for p in pr:
                try:
                    ts = float(getattr(p, "time", "nan"))
                    length = int(len(p))
                    src = dst = None

                    if p.haslayer(IP):
                        src = p[IP].src; dst = p[IP].dst
                    elif p.haslayer(IPv6):
                        src = p[IPv6].src; dst = p[IPv6].dst
                    elif p.haslayer(ARP):
                        # ARP kadang bawa IP (psrc/pdst); kalau tidak, pakai MAC
                        src = getattr(p[ARP], "psrc", None) or getattr(p[ARP], "hwsrc", None)
                        dst = getattr(p[ARP], "pdst", None) or getattr(p[ARP], "hwdst", None)
                    elif p.haslayer(Ether):
                        src = getattr(p[Ether], "src", None)
                        dst = getattr(p[Ether], "dst", None)

                    if src or dst:
                        rows.append({
                            "frame.time_epoch": ts,
                            "ip.src": src,
                            "ip.dst": dst,
                            "frame.len": length
                        })
                except Exception:
                    continue
    except Exception:
        return pd.DataFrame()

    if not rows:
        return pd.DataFrame()
    return _normalize_columns(pd.DataFrame(rows))

# ===== PUBLIC API =====
def parse_pcap_file(path: str) -> pd.DataFrame:
    """
    Entry point untuk auto-parse PCAP/PCAPNG dengan fallback berlapis.
    Hasil: DataFrame schema ["ts", "src", "dst", "length"] atau dummy row (Demo Mode).
    """
    if not os.path.exists(path):
        return pd.DataFrame()

    # 1) TShark
    df = _parse_with_tshark(path)
    if not df.empty:
        return df

    # 2) PyShark (opsional; bounded)
    try:
        df = _parse_with_pyshark(path)
        if not df.empty:
            return df
    except TimeoutError:
        # timeouts → lanjut ke Scapy
        pass
    except Exception:
        # error → lanjut ke Scapy
        pass

    # 3) Scapy (streaming)
    df = _parse_with_scapy(path)
    if not df.empty:
        return df

    # 4) Demo safety net
    if DEMO_MODE:
        return pd.DataFrame([{"ts": 0.0, "src": "0.0.0.0", "dst": "255.255.255.255", "length": 60}])

    return pd.DataFrame()
