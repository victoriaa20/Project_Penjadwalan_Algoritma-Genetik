import streamlit as st
import numpy as np

from ag.data import SEEDS_DEFAULT
from ag.engine import ParameterGA, jalankan_banyak_run, kunci_terbaik, jalankan_perbandingan_operator
from ag.fitness import hitung_pelanggaran, total_pelanggaran
from ui.komponen import (
    inject_css, page_header, render_stat_card,
    render_badge, render_empty_state,
)
from ui.state import init_session_state, ada_hasil_10_run
from ui.visual import plot_konvergensi_10_run, plot_perbandingan_operator

inject_css()
init_session_state()

page_header("🔬 Pengujian 10 Run", "Eksekusi 10 seed berbeda dan analisis statistik hasil AG.")

data  = st.session_state.data
param = st.session_state.param

# Konfigurasi Run
with st.expander("⚙️ Konfigurasi Run", expanded=not ada_hasil_10_run()):
    col_p, col_s = st.columns([3, 2])
    with col_p:
        ukuran_pop   = st.number_input("Ukuran Populasi", 20, 1000, param.ukuran_populasi, 10)
        n_generasi   = st.number_input("Jumlah Generasi",  10, 2000, param.n_generasi,      50)
        p_crossover  = st.slider("Peluang Crossover (pc)", 0.0, 1.0, float(param.p_crossover), 0.05)
        p_mutasi     = st.slider("Peluang Mutasi (pm)",   0.0, 0.5, float(param.p_mutasi),    0.01)
    with col_s:
        metode_seleksi   = st.selectbox("Metode Seleksi",   ["turnamen", "roulette"])
        metode_crossover = st.selectbox("Metode Crossover", ["uniform", "satu_titik"])
        k_turnamen = st.number_input("k Turnamen", 2, 10, param.k_turnamen)
        n_elit     = st.number_input("Elitisme (n)", 0, 10, param.n_elit)

    seeds_input = st.text_input(
        "Seeds (pisahkan dengan koma)", value=", ".join(str(s) for s in SEEDS_DEFAULT),
        help="Minimal 10 seed berbeda."
    )
    berhenti_jika_valid = st.checkbox("Berhenti saat solusi valid", value=False)
    jalankan_perbandingan = st.checkbox(
        "Jalankan perbandingan 4 kombinasi operator (P1)", value=False,
        help="Akan menambah waktu eksekusi sekitar 4×."
    )

try:
    seeds = [int(s.strip()) for s in seeds_input.split(",") if s.strip()]
    if len(seeds) < 2:
        st.warning("Masukkan minimal 2 seed.", icon="⚠️")
        seeds = SEEDS_DEFAULT
except ValueError:
    st.error("Format seed tidak valid. Gunakan angka dipisahkan koma.", icon="❌")
    seeds = SEEDS_DEFAULT

param_10 = ParameterGA(
    ukuran_populasi=int(ukuran_pop), n_generasi=int(n_generasi),
    p_crossover=p_crossover, p_mutasi=p_mutasi,
    metode_seleksi=metode_seleksi, metode_crossover=metode_crossover,
    k_turnamen=int(k_turnamen), n_elit=int(n_elit),
)

# Tombol Jalankan
col_btn, _ = st.columns([2, 5])
with col_btn:
    mulai_10 = st.button("▶️ Jalankan 10 Run", type="primary", use_container_width=True)

if mulai_10:
    st.session_state.param = param_10

    progress_bar  = st.progress(0, text="Menginisialisasi...")
    run_status    = st.empty()
    run_counter   = st.empty()

    run_idx_state = {"current": 0}

    def _cb_10(run_idx: int, persen: int, info: dict) -> None:
        total_persen = int((run_idx * 100 + persen) / len(seeds))
        run_status.markdown(
            f"**Run {run_idx+1}/{len(seeds)}** — Generasi {info['generasi']} "
            f"— Fitness: `{info['fitness']:.4f}`"
        )
        progress_bar.progress(min(total_persen, 100), text=f"Run {run_idx+1}/{len(seeds)}")

    with st.spinner(f"Menjalankan {len(seeds)} run AG..."):
        hasil_runs, df_runs, df_ringkasan = jalankan_banyak_run(
            param_10, seeds, data, berhenti_jika_valid, _cb_10
        )

    st.session_state.hasil_runs    = hasil_runs
    st.session_state.df_runs       = df_runs
    st.session_state.df_ringkasan  = df_ringkasan
    st.session_state.run_terbaik   = min(hasil_runs, key=lambda h: kunci_terbaik(h, data))
    progress_bar.progress(100, text="✅ Selesai!")
    run_status.empty()

    # Perbandingan operator (P1)
    if jalankan_perbandingan:
        with st.spinner("Menjalankan perbandingan 4 kombinasi operator..."):
            hasil_kombinasi, df_kombinasi = jalankan_perbandingan_operator(param_10, seeds, data)
        st.session_state.hasil_kombinasi = hasil_kombinasi
        st.session_state.df_kombinasi    = df_kombinasi

# Tampilkan Hasil
if not ada_hasil_10_run():
    st.markdown("<br>", unsafe_allow_html=True)
    render_empty_state(
        judul="Belum ada hasil 10 run.",
        isi="Klik 'Jalankan 10 Run' untuk memulai pengujian.",
        ikon="🔬",
    )
    st.stop()

hasil_runs   = st.session_state.hasil_runs
df_runs      = st.session_state.df_runs
df_ringkasan = st.session_state.df_ringkasan

st.markdown("---")
st.markdown("### 📊 Hasil 10 Run")

# Banner validitas
n_valid = int(df_runs["Generasi Valid Pertama"].notna().sum())
n_total = len(df_runs)
if n_valid == n_total:
    st.success(f"✅ Seluruh {n_valid} dari {n_total} run menemukan solusi valid!", icon="🎉")
elif n_valid > 0:
    st.info(f"ℹ️ {n_valid} dari {n_total} run menemukan solusi valid.", icon="✅")
else:
    st.warning("⚠️ Tidak ada run yang menemukan solusi valid. Coba naikkan populasi/generasi.", icon="⚠️")

# Pil statistik ringkasan
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_stat_card("Fitness Terbaik (maks)", f"{df_runs['Fitness Terbaik'].max():.4f}", ikon="🎯")
with c2:
    render_stat_card("Run Valid", f"{n_valid}/{n_total}", ikon="✅")
with c3:
    gv_mean = df_runs["Generasi Valid Pertama"].mean()
    render_stat_card("Rerata Gen Valid", str(round(gv_mean)) if not np.isnan(gv_mean) else "—", ikon="🏁")
with c4:
    render_stat_card("Rerata Waktu/Run", f"{df_runs['Waktu (s)'].mean():.2f} dtk", ikon="⏱️")

st.markdown("<br>", unsafe_allow_html=True)

# Tabel per run
st.markdown("#### Tabel Hasil Per Run")
st.dataframe(
    df_runs,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Run":   st.column_config.NumberColumn("Run", width=60),
        "Seed":  st.column_config.NumberColumn("Seed", width=70),
        "Fitness Terbaik": st.column_config.NumberColumn("Fitness Terbaik", format="%.4f"),
        "Fitness Rata-rata (generasi akhir)": st.column_config.NumberColumn("Fitness Rata-rata", format="%.4f"),
        "Generasi Valid Pertama": st.column_config.NumberColumn("Gen Valid"),
        "Pelanggaran Keras": st.column_config.NumberColumn("Pelanggaran"),
        "Waktu (s)": st.column_config.NumberColumn("Waktu (s)", format="%.2f"),
    }
)

# Tabel ringkasan
st.markdown("#### Tabel Ringkasan Statistik")
st.dataframe(df_ringkasan, use_container_width=True)

# Grafik konvergensi 10 run
st.markdown("---")
st.markdown("#### 📈 Grafik Konvergensi 10 Run")
fig_10 = plot_konvergensi_10_run(hasil_runs)
st.pyplot(fig_10, use_container_width=True)

# Run Terbaik
run_terbaik = st.session_state.get("run_terbaik")
if run_terbaik:
    st.markdown("---")
    st.markdown("#### 🏆 Run Terbaik")
    rt = run_terbaik
    pelang = hitung_pelanggaran(rt["kromosom"], data)
    total_pel = sum(pelang.values())

    col_info, col_detail = st.columns(2)
    with col_info:
        card_info = (
            '<div class="jadwalga-card" style="padding:20px;">'
            '<div class="jadwalga-card-title">🏆 Run Terbaik Terpilih</div>'
            '<table style="width:100%; font-size:14px; border-collapse:collapse;">'
            f'<tr><td style="padding:6px 0; color:var(--text-secondary);">Seed</td><td><strong>{rt["seed"]}</strong></td></tr>'
            f'<tr><td style="padding:6px 0; color:var(--text-secondary);">Fitness Terbaik</td><td><strong>{rt["fitness_terbaik"]:.4f}</strong></td></tr>'
            f'<tr><td style="padding:6px 0; color:var(--text-secondary);">Generasi Valid</td><td><strong>{rt["gen_valid"] if rt["gen_valid"] is not None else "—"}</strong></td></tr>'
            f'<tr><td style="padding:6px 0; color:var(--text-secondary);">Pelanggaran Keras</td><td><strong>{total_pel}</strong></td></tr>'
            f'<tr><td style="padding:6px 0; color:var(--text-secondary);">Waktu</td><td><strong>{rt["waktu_detik"]:.2f} dtk</strong></td></tr>'
            '</table>'
            '</div>'
        )
        st.html(card_info)
    with col_detail:
        label_map = {
            "H1_dosen": "H1 Bentrok Dosen",
            "H2_ruang": "H2 Bentrok Ruang",
            "H3_kelas": "H3 Bentrok Kelas",
            "H4_kapasitas": "H4 Kapasitas Ruang",
        }
        rinci_html = ""
        for k, v in pelang.items():
            badge = render_badge(str(v), "valid" if v == 0 else "bentrok")
            lbl = label_map.get(k, k)
            rinci_html += (
                f'<div style="display:flex; justify-content:space-between; align-items:center; '
                f'padding:8px 0; border-bottom:1px solid var(--divider);">'
                f'<span style="font-size:13px;">{lbl}</span> {badge}'
                f'</div>'
            )
        card_detail = (
            '<div class="jadwalga-card" style="padding:16px 20px;">'
            '<div class="jadwalga-card-title" style="margin-bottom:12px;">Rincian Pelanggaran Keras</div>'
            f'{rinci_html}'
            '</div>'
        )
        st.html(card_detail)

    st.info("Jadwal terbaik dari run ini tersedia di halaman **Jadwal Terbaik** dan **Ekspor**.", icon="💡")

# Perbandingan Operator (P1)
hasil_kombinasi = st.session_state.get("hasil_kombinasi")
df_kombinasi    = st.session_state.get("df_kombinasi")

if hasil_kombinasi and df_kombinasi is not None:
    st.markdown("---")
    st.markdown("#### 🔁 Perbandingan 4 Kombinasi Operator (P1)")
    st.dataframe(df_kombinasi, use_container_width=True, hide_index=True)

    fig_op = plot_perbandingan_operator(hasil_kombinasi)
    st.pyplot(fig_op, use_container_width=True)
