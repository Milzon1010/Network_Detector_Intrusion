# core/auto_parser.py

import os
import logging
import pandas as pd
from pathlib import Path

from core.preprocessor import preprocess_packets  # ⬅️ Untuk preprocessing
# from parsers.parse_pcap_tshark_ipv6 import parse_pcap_file  # ⛔️ Kita tidak pakai ini sekarang

logger = logging.getLogger(__name__)

def parse_pcap_auto(filepath: str) -> pd.DataFrame:
    try:
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File tidak ditemukan: {filepath}")

        ext = Path(filepath).suffix.lower()

        if ext in [".pcap", ".pcapng"]:
            logger.info(f"🔍 Memproses file PCAP: {filepath}")

            # Kamu bisa ganti bagian ini sesuai parser kamu, sementara kita skip:
            # df = parse_pcap_file(filepath)
            logger.warning("⚠️ Parser untuk .pcap belum diimplementasikan. Lewati dulu.")
            return pd.DataFrame()

        elif ext == ".csv":
            logger.info(f"📄 Membaca file CSV: {filepath}")
            df = pd.read_csv(filepath)

        else:
            raise ValueError(f"❌ Format file tidak didukung: {ext}")

        if df is not None and not df.empty:
            df = preprocess_packets(df)
            logger.info(f"✅ Data selesai diproses dan dipreproses. Baris: {len(df)}")
            return df

        return pd.DataFrame()

    except Exception as e:
        logger.error(f"❌ Parsing gagal: {e}")
        return pd.DataFrame()
