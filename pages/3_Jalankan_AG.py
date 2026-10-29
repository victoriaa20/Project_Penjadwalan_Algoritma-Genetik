import time

import streamlit as st

from ag.engine import ParameterGA, jalankan_ga
from ag.fitness import hitung_pelanggaran, hitung_soft
from ui.komponen import (
    inject_css, page_header, render_stat_card,
    render_constraint_checklist, render_badge, render_empty_state,
)
from ui.state import init_session_state
from ui.visual import plot_konvergensi_tunggal

inject_css()
init_session_state()

page_header("🧬 Jalankan AG", "Konfigurasi parameter dan jalankan satu run Algoritma Genetika.")

data  = st.session_state.data
param = st.session_state.param


# Panel Parameter (sidebar kiri)
with st.sidebar:
    st.markdown("### ⚙️ Parameter AG")

    ukuran_pop = st.number_input(
        "Ukuran Populasi", min_value=20, max_value=1000, value=param.ukuran_populasi, step=10,
        help="Jumlah individu per generasi."
    )
    n_generasi = st.number_input(
        "Jumlah Generasi", min_value=10, max_value=2000, value=param.n_generasi, step=50,
        help="Jumlah iterasi evolusi maksimum."
    )

    st.markdown("---")
    p_crossover = st.slider("Peluang Crossover (pc)", 0.0, 1.0, float(param.p_crossover), 0.05)
    p_mutasi    = st.slider("Peluang Mutasi (pm)",   0.0, 0.5, float(param.p_mutasi),    0.01)

    st.markdown("---")
    metode_seleksi   = st.selectbox("Metode Seleksi",   ["turnamen", "roulette"],      index=["turnamen","roulette"].index(param.metode_seleksi))
    metode_crossover = st.selectbox("Metode Crossover", ["uniform", "satu_titik"],     index=["uniform","satu_titik"].index(param.metode_crossover))
    k_turnamen = st.number_input("k Turnamen", min_value=2, max_value=10, value=param.k_turnamen)
    n_elit     = st.number_input("Elitisme (n)",  min_value=0, max_value=10, value=param.n_elit)

    st.markdown("---")
    seed = st.number_input("Seed", min_value=0, max_value=99999, value=42,
                           help="Seed acak untuk reprodusibilitas.")
    berhenti_jika_valid = st.checkbox(
        "Berhenti saat solusi valid ditemukan",
        value=False,
        help="Menghentikan evolusi lebih awal jika fitness mencapai 1.0."
    )

    param_baru = ParameterGA(
        ukuran_populasi=int(ukuran_pop),
        n_generasi=int(n_generasi),
        p_crossover=p_crossover,
        p_mutasi=p_mutasi,
        metode_seleksi=metode_seleksi,
        metode_crossover=metode_crossover,
        k_turnamen=int(k_turnamen),
        n_elit=int(n_elit),
    )

# Tombol Jalankan AG
col_btn, col_info = st.columns([2, 5])
with col_btn:
    mulai = st.button("▶️ Jalankan AG", type="primary", use_container_width=True)

if mulai:
    st.session_state.param = param_baru

    progress_bar = st.progress(0, text="Memulai algoritma genetika...")
    status_text  = st.empty()

    def _cb(persen: int, info: dict) -> None:
        gen     = info["generasi"]
        fitness = info["fitness"]
        progress_bar.progress(min(persen, 100),
                              text=f"Generasi {gen} — Fitness terbaik: {fitness:.4f}")
        if info.get("gen_valid") is not None:
            status_text.success(f"✅ Solusi valid ditemukan pada generasi {info['gen_valid']}!")

    with st.spinner("Menjalankan AG..."):
        hasil = jalankan_ga(
            param_baru, int(seed), data,
            berhenti_jika_valid=berhenti_jika_valid,
            progress_callback=_cb,
        )

    st.session_state.hasil_run_tunggal = hasil
    progress_bar.progress(100, text="✅ Selesai!")


# Tampilkan Hasil
hasil = st.session_state.get("hasil_run_tunggal")

if hasil is None:
    st.markdown("<br>", unsafe_allow_html=True)
    render_empty_state(
        judul="Belum ada hasil.",
        isi="Atur parameter di sidebar kiri, lalu klik 'Jalankan AG'.",
        ikon="🧬",
    )
else:
    st.markdown("---")
    st.markdown("### 📊 Hasil Run Tunggal")

    # Pil statistik utama
    c1, c2, c3, c4 = st.columns(4)
    fit = hasil["fitness_terbaik"]
    gv  = hasil["gen_valid"]

    with c1:
        render_stat_card(
            "Fitness Terbaik",
            f"{fit:.4f}",
            ikon="🎯",
            delta="✅ Valid" if fit == 1.0 else "⚠️ Belum valid",
            delta_positif=(fit == 1.0),
        )
    with c2:
        render_stat_card(
            "Generasi Valid Pertama",
            str(gv) if gv is not None else "—",
            ikon="🏁",
            delta="Fitness 1.0 tercapai" if gv is not None else "Tidak ditemukan",
            delta_positif=(gv is not None),
        )
    with c3:
        render_stat_card(
            "Fitness Rata-rata Akhir",
            f"{hasil['fitness_rata_akhir']:.4f}",
            ikon="📈",
        )
    with c4:
        waktu = hasil["waktu_detik"]
        render_stat_card(
            "Waktu Eksekusi",
            f"{waktu:.1f} dtk",
            ikon="⏱️",
            delta="✅ < 10 dtk" if waktu < 10 else "⚠️ > 10 dtk",
            delta_positif=(waktu < 10),
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Detail pelanggaran
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Kendala & Pelanggaran")
        pel  = hitung_pelanggaran(hasil["kromosom"], data)
        soft = hitung_soft(hasil["kromosom"], data)
        render_constraint_checklist(
            h1=pel["H1_dosen"], h2=pel["H2_ruang"],
            h3=pel["H3_kelas"], h4=pel["H4_kapasitas"],
            s1=soft["S1_preferensi_dosen"], s2=soft["S2_jeda_panjang"],
        )

    with col_right:
        st.markdown("#### Rincian Pelanggaran")
        items = [
            ("H1 Bentrok Dosen",    pel["H1_dosen"],         "valid" if pel["H1_dosen"]==0 else "bentrok"),
            ("H2 Bentrok Ruang",    pel["H2_ruang"],         "valid" if pel["H2_ruang"]==0 else "bentrok"),
            ("H3 Bentrok Kelas",    pel["H3_kelas"],         "valid" if pel["H3_kelas"]==0 else "bentrok"),
            ("H4 Kapasitas",        pel["H4_kapasitas"],     "valid" if pel["H4_kapasitas"]==0 else "bentrok"),
            ("S1 Preferensi Dosen", soft["S1_preferensi_dosen"], "preferensi"),
            ("S2 Jeda Panjang",     soft["S2_jeda_panjang"],     "netral"),
        ]
        rincian_html = ""
        for label, nilai, tipe in items:
            badge = render_badge(str(nilai), tipe if nilai == 0 else ("valid" if nilai == 0 else tipe))
            rincian_html += (
                f'<div style="display:flex; justify-content:space-between; align-items:center; '
                f'padding:10px 0; border-bottom:1px solid var(--divider);">'
                f'<span style="font-size:14px;">{label}</span>'
                f'{badge}'
                f'</div>'
            )
        st.html(
            f'<div class="jadwalga-card" style="padding:16px 20px;">{rincian_html}</div>'
        )

    # Grafik konvergensi
    st.markdown("---")
    st.markdown("#### 📈 Grafik Konvergensi")
    fig = plot_konvergensi_tunggal(hasil)
    st.pyplot(fig, use_container_width=True)

    st.info(
        f"Seed: **{hasil['seed']}** | "
        f"Seleksi: **{param_baru.metode_seleksi}** | "
        f"Crossover: **{param_baru.metode_crossover}** | "
        f"Pop: **{param_baru.ukuran_populasi}** | "
        f"Gen: **{param_baru.n_generasi}**",
        icon="ℹ️"
    )
