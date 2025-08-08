# core/auto_parser.py
from __future__ import annotations

import logging
from pathlib import Path
import pandas as pd

from core.preprocessor import preprocess_packets
# Parser utama dengan fallback berlapis (TSHARK -> PYSHARK -> SCAPY -> DEMO)
from parsers.parse_pcap_tshark_ipv6 import parse_pcap_file as parse_with_tshark_ipv6

log = logging.getLogger(__name__)

def parse_pcap_auto(path: str) -> pd.DataFrame:
    """
    Auto-parse file input untuk NID Dashboard.

    - .pcap / .pcapng  → parse_with_tshark_ipv6
      Parser ini mencoba:
        1) Tshark sinkron
        2) Pyshark (async ke sinkron)
        3) Scapy (streaming)
        4) Demo dataframe minimal (agar UI tidak blank saat presentasi)

    - .csv → pd.read_csv
      Untuk file hasil ekspor atau tes manual.

    Apapun hasilnya → diproses preprocess_packets() agar bentuk kolom
    konsisten untuk modul Analysis Summary, Anomaly Detection, dan PCA.
    """
    p = Path(path)
    ext = p.suffix.lower()

    try:
        # === Handle PCAP/PCAPNG ===
        if ext in (".pcap", ".pcapng"):
            log.info(f"🔍 Parsing PCAP: {p}")
            df = parse_with_tshark_ipv6(str(p))

        # === Handle CSV ===
        elif ext == ".csv":
            log.info(f"📄 Membaca CSV: {p}")
            df = pd.read_csv(p)

        else:
            raise ValueError(f"❌ Format file tidak didukung: {ext}")

        # === Validasi & Preprocess ===
        if df is None or df.empty:
            log.warning("⚠️ DataFrame kosong setelah parsing.")
            return pd.DataFrame()

        df = preprocess_packets(df)
        log.info(f"✅ Selesai preprocess. Baris: {len(df)}")
        return df

    except Exception as e:
        log.warning(f"⚠️ Parsing gagal: {e}")
        return pd.DataFrame()
