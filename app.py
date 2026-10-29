import streamlit as st

# Konfigurasi halaman (harus dipanggil pertama kali)
st.set_page_config(
    page_title="JadwalGA",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from ui.komponen import inject_css
from ui.state import init_session_state

# Injeksi stylesheet Lumio Glass
inject_css()

# Inisialisasi session state
init_session_state()

# Navigasi multi-halaman dengan st.navigation
dashboard_page   = st.Page("pages/1_Dashboard.py",        title="Dashboard",        icon="🏠", default=True)
data_page        = st.Page("pages/2_Data_Master.py",       title="Data Master",       icon="📋")
jalankan_page    = st.Page("pages/3_Jalankan_AG.py",       title="Jalankan AG",       icon="🧬")
pengujian_page   = st.Page("pages/4_Pengujian_10_Run.py",  title="Pengujian 10 Run",  icon="🔬")
jadwal_page      = st.Page("pages/5_Jadwal.py",            title="Jadwal Terbaik",    icon="📅")
ekspor_page      = st.Page("pages/6_Ekspor.py",            title="Ekspor",            icon="📥")
bantuan_page     = st.Page("pages/7_Bantuan.py",           title="Bantuan & AG",      icon="❓")

pg = st.navigation(
    {
        "Utama": [dashboard_page, data_page, jalankan_page, pengujian_page, jadwal_page, ekspor_page],
        "Lainnya": [bantuan_page],
    },
    position="sidebar",
)

pg.run()
