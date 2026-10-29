import streamlit as st

from ag.fitness import hitung_pelanggaran, hitung_soft
from ag.tampilan import bangun_daftar
from ui.komponen import (
    inject_css, render_hero, render_stat_card,
    render_highlight_card, render_constraint_checklist,
    render_daftar_sesi_harian, render_empty_state,
    sapaan, tanggal_hari_ini, WARNA_KELAS,
)
from ui.state import (
    init_session_state, ada_hasil_apapun,
    ada_hasil_10_run, get_run_terbaik,
)
from ui.visual import plot_konvergensi_tunggal, plot_konvergensi_10_run

inject_css()
init_session_state()

data = st.session_state.data

render_hero(
    subjudul=f"{tanggal_hari_ini()} · Optimasi Penjadwalan Kuliah dengan Algoritma Genetika",
    tampilkan_tombol_run=not ada_hasil_apapun(),
    ada_hasil=ada_hasil_apapun(),
)

# Tombol aksi di bawah hero
col_b1, col_b2, _ = st.columns([1.5, 1.5, 5])
with col_b1:
    if st.button("▶️ Jalankan AG", type="primary", use_container_width=True, key="dashboard_run_btn"):
        st.switch_page("pages/3_Jalankan_AG.py")
with col_b2:
    if ada_hasil_apapun():
        if st.button("📥 Unduh Excel", use_container_width=True, key="dashboard_dl_btn"):
            st.switch_page("pages/6_Ekspor.py")

st.markdown("<br>", unsafe_allow_html=True)

if not ada_hasil_apapun():
    render_empty_state(
        judul="Selamat datang di JadwalGA! 🧬",
        isi="Belum ada hasil tersedia. Klik 'Jalankan AG' untuk memulai optimasi penjadwalan.",
        ikon="🧬",
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📖 Petunjuk Singkat")
    cols = st.columns(3)
    petunjuk = [
        ("1️⃣", "Cek Data Master", "Pastikan data 20 matkul, 8 dosen, 5 ruang, dan 6 kelas sudah benar."),
        ("2️⃣", "Jalankan AG",     "Atur parameter dan jalankan satu run atau langsung 10 run pengujian."),
        ("3️⃣", "Unduh Hasil",     "Ekspor jadwal terbaik ke CSV/Excel dan grafik konvergensi ke PNG."),
    ]
    for (nomor, judul, isi), col in zip(petunjuk, cols):
        with col:
            st.html(
                '<div class="jadwalga-card" style="text-align:center; padding:24px;">'
                f'<div style="font-size:32px;">{nomor}</div>'
                f'<div class="jadwalga-card-title" style="margin:12px 0 8px;">{judul}</div>'
                f'<p style="font-size:13px; color:var(--text-secondary);">{isi}</p>'
                '</div>'
            )
    st.stop()

run_terbaik  = get_run_terbaik()
k_terbaik    = run_terbaik["kromosom"]
df_jadwal    = bangun_daftar(k_terbaik, data)
pel          = hitung_pelanggaran(k_terbaik, data)
soft         = hitung_soft(k_terbaik, data)
fit          = run_terbaik["fitness_terbaik"]
gv           = run_terbaik.get("gen_valid")

df_runs  = st.session_state.get("df_runs")
hasil_10 = st.session_state.get("hasil_runs")
n_valid  = int(df_runs["Generasi Valid Pertama"].notna().sum()) if df_runs is not None else 0
n_total  = len(df_runs) if df_runs is not None else 0

st.markdown("### 📊 Statistik Utama")
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_stat_card("Fitness Terbaik", f"{fit:.4f}", ikon="🎯",
                     delta="✅ Valid" if fit == 1.0 else "⚠️ Belum valid",
                     delta_positif=(fit == 1.0))
with c2:
    render_stat_card("Run Valid", f"{n_valid}/{n_total}" if n_total else "—/—", ikon="✅",
                     delta=f"{n_valid} dari {n_total} run valid" if n_total else "Belum ada 10 run",
                     delta_positif=(n_valid == n_total and n_total > 0))
with c3:
    render_stat_card("Generasi Valid Pertama", str(gv) if gv is not None else "—", ikon="🏁",
                     delta=f"Seed {run_terbaik.get('seed','?')}")
with c4:
    waktu = run_terbaik.get("waktu_detik", 0)
    render_stat_card("Waktu Eksekusi", f"{waktu:.1f} dtk", ikon="⏱️",
                     delta="✅ < 10 dtk" if waktu < 10 else "⚠️ > 10 dtk",
                     delta_positif=(waktu < 10))

st.markdown("<br>", unsafe_allow_html=True)

kol1, kol2, kol3 = st.columns([1, 1.4, 1])

with kol1:
    render_constraint_checklist(
        h1=pel["H1_dosen"], h2=pel["H2_ruang"],
        h3=pel["H3_kelas"], h4=pel["H4_kapasitas"],
        s1=soft["S1_preferensi_dosen"], s2=soft["S2_jeda_panjang"],
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Info singkat run terbaik
    st.html(
        '<div class="jadwalga-card" style="padding:16px 20px; font-size:13px;">'
        '<div class="jadwalga-card-title" style="margin-bottom:12px;">🏆 Run Terbaik</div>'
        '<div style="color:var(--text-secondary); line-height:2;">'
        f'Seed: <strong>{run_terbaik.get("seed","?")}</strong><br>'
        f'Fitness: <strong>{fit:.4f}</strong><br>'
        f'Gen Valid: <strong>{gv if gv is not None else "—"}</strong><br>'
        f'Waktu: <strong>{waktu:.2f} dtk</strong>'
        '</div>'
        '</div>'
    )

with kol2:
    with st.container(border=True):
        st.markdown('<div class="jadwalga-card-title">📈 Grafik Konvergensi</div>', unsafe_allow_html=True)
        if hasil_10:
            fig_kv = plot_konvergensi_10_run(hasil_10)
        else:
            fig_kv = plot_konvergensi_tunggal(run_terbaik)
        st.pyplot(fig_kv, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown('<div class="jadwalga-card-title">📅 Jadwal Harian</div>', unsafe_allow_html=True)
        hari_terpilih = st.selectbox("Pilih Hari", data.hari, key="dash_hari_sel", label_visibility="collapsed")
        render_daftar_sesi_harian(df_jadwal, hari_terpilih)

with kol3:
    if fit == 1.0:
        render_highlight_card(
            judul="Solusi valid ditemukan. ✅",
            isi=f"Fitness 1.00 tercapai pada generasi {gv} tanpa pelanggaran H1–H4.",
        )
    else:
        render_highlight_card(
            judul="Belum ada solusi valid.",
            isi=f"Fitness terbaik: {fit:.4f}. Coba naikkan populasi atau generasi untuk menemukan jadwal valid.",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if df_runs is not None:
        # Mini bar chart run valid (sparkline sederhana)
        run_valid_html = ""
        for _, row in df_runs.iterrows():
            is_valid = row.get("Generasi Valid Pertama") is not None and str(row.get("Generasi Valid Pertama")) != "nan"
            warna_bar = "#1F8A4C" if is_valid else "#E4E8EA"
            run_valid_html += f"""
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:6px; font-size:12px;">
              <span style="color:var(--text-muted); width:44px; flex-shrink:0;">Run {int(row['Run'])}</span>
              <div style="flex:1; height:8px; border-radius:4px; background:{warna_bar};"></div>
              <span style="color:var(--text-secondary); width:50px; text-align:right; flex-shrink:0;">{row['Fitness Terbaik']:.4f}</span>
            </div>
            """
        card_10run = f"""
        <div class="jadwalga-card" style="padding:16px 20px;">
          <div class="jadwalga-card-title" style="margin-bottom:12px;">🔬 Ringkasan 10 Run</div>
          {run_valid_html}
        </div>
        """
        st.html(card_10run)
    else:
        st.html("""
        <div class="jadwalga-card" style="padding:16px 20px; text-align:center;">
          <div style="color:var(--text-muted); font-size:13px; padding:16px 0;">
            💡 Jalankan 10 run pengujian untuk melihat perbandingan statistik di sini.
          </div>
        </div>
        """)

st.markdown("---")
st.markdown("### 🔗 Akses Cepat")
ql_cols = st.columns(6)
pages = [
    ("📋", "Data Master",      "pages/2_Data_Master.py"),
    ("🧬", "Jalankan AG",      "pages/3_Jalankan_AG.py"),
    ("🔬", "10 Run",           "pages/4_Pengujian_10_Run.py"),
    ("📅", "Jadwal Terbaik",   "pages/5_Jadwal.py"),
    ("📥", "Ekspor",           "pages/6_Ekspor.py"),
    ("❓", "Bantuan",          "pages/7_Bantuan.py"),
]
for (ikon, label, pg_path), col in zip(pages, ql_cols):
    with col:
        if st.button(f"{ikon} {label}", use_container_width=True, key=f"ql_{label}"):
            st.switch_page(pg_path)
