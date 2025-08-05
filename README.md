# 📡 Network Intrusion Detection Dashboard

An interactive Streamlit-based dashboard to **analyze, visualize, and detect anomalies** in network traffic from `.pcap` files. Designed for security analysts, educators, and researchers to explore network intrusion patterns using modern data science techniques.

---

## 🚀 Features

* 📤 **Upload PCAP Files** – Drag & drop or browse `.pcap` / `.pcapng` files to start analysis
* ⚙️ **Auto Parsing** – Uses `tshark`-based backend to extract structured flow/session data
* 📈 **Visual Analysis Pages**:

  * **Summary** – IP stats, top ports, traffic volume timeline
  * **Anomaly Detection** – ML-based anomaly clustering (KMeans, DBSCAN, Isolation Forest)
  * **PCA Analysis** – Principal Component Analysis for pattern & feature projection
* 🖼️ **Stylized UI** – Soft blue-gray sidebar, transparent cyber background, dark-themed graphs
* 💾 **Session Aware** – Upload once, analyze across pages without reprocessing

---

## 📂 Folder Structure

```
📁 Network_Detector_Intrusion
├── dashboard_app.py           # Main Streamlit entry point
├── pages/
│   ├── Analysis_Summary.py
│   ├── Anomaly_Detection.py
│   ├── PCA_Analysis.py
│   └── Summary.py
├── core/
│   └── auto_parser.py         # Handles PCAP parsing using tshark
├── background_nid.jpg         # UI background image (optional)
├── requirements.txt           # Python dependencies
└── output/                    # (Optional) Exported files
```

---

## 🛠️ Installation & Setup

### 🔗 Requirements

* Python 3.9+
* Streamlit
* Tshark (part of Wireshark CLI tools)

### ⏬ Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 🧠 Install Tshark

* **Windows**: Install Wireshark → enable "Tshark in PATH"
* **Linux**: `sudo apt install tshark`
* **Mac**: `brew install wireshark`

### ▶️ Run the App

```bash
streamlit run dashboard_app.py
```

Then open: [http://localhost:8501](http://localhost:8501)

---

## 💡 Sample Use Cases

* 🛡️ Simulate and explore DDoS or ICMP flood patterns
* 🧪 Evaluate anomaly detection algorithms on real packet data
* 🧑‍🏫 Teach network security fundamentals with visual aids
* 📊 Extract insights from traffic capture during pentesting or lab experiments

---

## 📸 Screenshots



---

## 🙌 Contributors

👤 [Milzon](https://www.linkedin.com/in/milzon) – Telecom & AI Enthusiast, Network Infra + AI Transition

---

## 📜 License

This project is open-source for educational and non-commercial research use.

---

## ✅ To Do (Next Milestones)

*🔧 Fungsionalitas Tambahan
 Export ke PDF/CSV

Tombol Download PDF Summary atau Export to CSV

Gunakan fpdf atau pdfkit

 Session Reset Button

Tombol "🔄 Reset Data" di sidebar untuk clear session state

 Multiple File Upload Support

Gabungkan file .pcap atau batch-analisis beberapa file sekaligus

 Filter Interaktif

Filter IP, port, protokol, rentang waktu, dll langsung di sidebar

 Auto-save ke output/ folder

Setiap parsing → simpan csv + summary.json

📊 Visualisasi & Analitik
 Heatmap komunikasi IP (src vs dst)

 Timeline Interaktif (hourly/daily trend)

 Packet Size Distribution

 Anomaly Explanation (SHAP, feature importance)

🧠 ML & Security Enhancements
 Signature-based Detection

Integrasi Suricata/Zeek atau regex rule sederhana

 Model Training Page

Bisa latih model anomaly detection dari file .csv baru

 Explainable ML

Gunakan PCA loading matrix atau LIME/SHAP untuk jelaskan anomali

🌐 Web & Deployment
 Streamlit Cloud or HuggingFace Space

Live link publik untuk portfolio / demo recruiter

 Add Login (optional)

Dengan streamlit-authenticator agar bisa multi-user

 Auto-delete file lama

Jika disimpan di server, jaga agar storage nggak penuh

🧾 Dokumentasi & Branding
 README Bahasa Indonesia

 Tambah badge GitHub (stars, license, last update)

 Demo Video YouTube (pakai narasi kamu)

 LinkedIn carousel post: “Dari packet capture jadi insight”