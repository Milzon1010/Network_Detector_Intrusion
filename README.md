# 🧠 Network Intrusion Detector Dashboard

A Streamlit-based interactive dashboard for analyzing network traffic from `.pcap`, `.pcapng`, or `.csv` files. Built with automated parsing, anomaly detection, and PCA-based visualization, this tool empowers network professionals and students to detect irregularities in traffic flow.

![Banner](background_NIDS.jpg)

---

## 🚀 Features

- **📂 Easy Upload**: Drag & drop `.pcap`, `.pcapng`, or `.csv` files (max 200MB)
- **📊 Analysis Summary**: Packet counts, unique IPs, and protocol detection
- **🚨 Anomaly Detection**: Identify suspiciously large packets (configurable threshold)
- **🧠 PCA Visualization**: Visualize high-dimensional traffic features for anomaly grouping
- **📥 Exportable Results**: Summary report (PDF) generation supported

---

## 🖥️ Interface Overview

- **Top-left**: Title and logo
- **Left Sidebar**: Navigation menu (Upload, Summary, Detection, PCA, Export)
- **Main View**: Dynamic visualizations and results
- **Background**: Transparent dark theme for readability & visual appeal

---

## ⚙️ Tech Stack

- `Python`
- `Streamlit`
- `Pandas`
- `Scikit-learn`
- `Plotly`
- `Matplotlib`, `Seaborn`
- `Tshark`, `pyshark` *(optional, for deeper parsing)*

---

## 🧪 How to Run Locally

```bash
# Clone the repo
git clone https://github.com/Milzon1010/Network_Detector_Intrusion.git
cd Network_Detector_Intrusion

# Set up environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install requirements
pip install -r requirements.txt

# Run Streamlit app
streamlit run dashboard_app.py

📁 Sample Folder Structure
📂 core/
📂 pages/
📂 parsers/
📂 tools/
📄 dashboard_app.py
📄 background_NIDS.jpg

🌐 Try it Online
🌍 View the app on Streamlit Cloud

🙋‍♂️ Author
milzon.ltf@gmail.com
Machine Learning Enthusiast | 23+ years in Telecom | Exploring AI x Network Intelligence
📫 Contact: LinkedIn

📄 License
This project is open source under the MIT License.

