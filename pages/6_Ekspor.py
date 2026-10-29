import streamlit as st

from ag.ekspor import to_csv_bytes, to_excel_bytes
from ag.tampilan import bangun_daftar, bangun_tabel_hari_slot
from ui.komponen import inject_css, page_header, render_empty_state
from ui.state import init_session_state, ada_hasil_apapun, get_run_terbaik
from ui.visual import fig_konvergensi_gabungan, fig_to_png_bytes

inject_css()
init_session_state()

page_header("📥 Ekspor", "Unduh jadwal terbaik, hasil 10 run, dan grafik konvergensi.")

data = st.session_state.data

if not ada_hasil_apapun():
    render_empty_state(
        judul="Belum ada data untuk diekspor.",
        isi="Jalankan AG terlebih dahulu, lalu kembali ke halaman ini untuk mengunduh hasilnya.",
        ikon="📥",
    )
    st.stop()

# Siapkan data ekspor
run_terbaik = get_run_terbaik()
k_terbaik   = run_terbaik["kromosom"]
df_jadwal   = bangun_daftar(k_terbaik, data)
tabel_hs    = bangun_tabel_hari_slot(k_terbaik, data)

df_runs      = st.session_state.get("df_runs")
df_ringkasan = st.session_state.get("df_ringkasan")
hasil_runs   = st.session_state.get("hasil_runs")

# unduhan
st.markdown("""
<div class="jadwalga-hero" style="padding:28px 28px; margin-bottom:24px;">
  <h2 class="jadwalga-hero-title" style="font-size:24px;">📥 Pusat Unduhan Berkas</h2>
  <p class="jadwalga-hero-sub">Seluruh berkas dibuat secara in-memory — tidak ada file yang disimpan di server.</p>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

# --- Jadwal Terbaik CSV ---
with col1:
    with st.container(border=True):
        st.html(
            '<div style="text-align:center; padding:12px 12px 16px;">'
            '<div style="font-size:40px; margin-bottom:12px;">📄</div>'
            '<div class="jadwalga-card-title">Jadwal Terbaik (CSV)</div>'
            '<p style="font-size:13px; color:var(--text-secondary); margin:8px 0 0;">'
            'Daftar seluruh 20 sesi kuliah terurut hari/slot.<br>'
            'Encoding utf-8-sig (Excel-friendly).'
            '</p>'
            '</div>'
        )
        csv_jadwal = to_csv_bytes(df_jadwal)
        st.download_button(
            label="⬇️ Unduh jadwal_terbaik.csv",
            data=csv_jadwal,
            file_name="jadwal_terbaik.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )

# --- Excel Multi-sheet ---
with col2:
    ada_10_run = df_runs is not None and df_ringkasan is not None
    pesan_10_run = '✅ Data 10 run tersedia.' if ada_10_run else '⚠️ Hanya jadwal terbaik (10 run belum dijalankan).'

    with st.container(border=True):
        st.html(
            '<div style="text-align:center; padding:12px 12px 16px;">'
            '<div style="font-size:40px; margin-bottom:12px;">📊</div>'
            '<div class="jadwalga-card-title">Jadwal + Hasil 10 Run (Excel)</div>'
            '<p style="font-size:13px; color:var(--text-secondary); margin:8px 0 0;">'
            '4 sheet: Daftar Jadwal, Hari × Slot, Hasil 10 Run, Ringkasan 10 Run.<br>'
            f'{pesan_10_run}'
            '</p>'
            '</div>'
        )
        import pandas as pd
        _df_runs_export     = df_runs      if ada_10_run else pd.DataFrame(columns=["Run","Seed","Fitness Terbaik"])
        _df_ringkasan_export = df_ringkasan if ada_10_run else pd.DataFrame()

        excel_bytes = to_excel_bytes(df_jadwal, tabel_hs, _df_runs_export, _df_ringkasan_export)
        st.download_button(
            label="⬇️ Unduh jadwal_terbaik.xlsx",
            data=excel_bytes,
            file_name="jadwal_terbaik.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )

st.markdown("<br>", unsafe_allow_html=True)
col3, col4 = st.columns(2)

# --- Hasil 10 Run CSV ---
with col3:
    ada_10_run = df_runs is not None
    pesan_csv_10 = '✅ Data tersedia.' if ada_10_run else '⚠️ Belum ada data 10 run.'

    with st.container(border=True):
        st.html(
            '<div style="text-align:center; padding:12px 12px 16px;">'
            '<div style="font-size:40px; margin-bottom:12px;">📈</div>'
            '<div class="jadwalga-card-title">Hasil 10 Run (CSV)</div>'
            '<p style="font-size:13px; color:var(--text-secondary); margin:8px 0 0;">'
            'Tabel per run: fitness, generasi valid, dan waktu.<br>'
            f'{pesan_csv_10}'
            '</p>'
            '</div>'
        )
        if ada_10_run:
            csv_runs = to_csv_bytes(df_runs)
            st.download_button(
                label="⬇️ Unduh hasil_10_run.csv",
                data=csv_runs,
                file_name="hasil_10_run.csv",
                mime="text/csv",
                use_container_width=True,
                type="primary",
            )
        else:
            st.button("⬇️ Unduh hasil_10_run.csv", disabled=True, use_container_width=True)

# --- Grafik Konvergensi PNG ---
with col4:
    ada_grafik = hasil_runs is not None or st.session_state.get("hasil_run_tunggal") is not None

    with st.container(border=True):
        st.html(
            '<div style="text-align:center; padding:12px 12px 16px;">'
            '<div style="font-size:40px; margin-bottom:12px;">🖼️</div>'
            '<div class="jadwalga-card-title">Grafik Konvergensi (PNG)</div>'
            '<p style="font-size:13px; color:var(--text-secondary); margin:8px 0 0;">'
            'Grafik konvergensi run terbaik dan rata-rata 10 run.<br>'
            'Resolusi tinggi 150 DPI, siap untuk laporan.'
            '</p>'
            '</div>'
        )
        if ada_grafik:
            hasil_satu = st.session_state.get("hasil_run_tunggal") or (hasil_runs[0] if hasil_runs else None)
            if hasil_satu:
                fig_gabung  = fig_konvergensi_gabungan(hasil_satu, hasil_runs)
                png_bytes   = fig_to_png_bytes(fig_gabung, dpi=150)
                st.download_button(
                    label="⬇️ Unduh grafik_konvergensi.png",
                    data=png_bytes,
                    file_name="grafik_konvergensi.png",
                    mime="image/png",
                    use_container_width=True,
                    type="primary",
                )
        else:
            st.button("⬇️ Unduh grafik_konvergensi.png", disabled=True, use_container_width=True)

# Pratinjau grafik
if ada_grafik:
    st.markdown("---")
    st.markdown("#### Pratinjau Grafik Konvergensi")
    hasil_satu = st.session_state.get("hasil_run_tunggal") or (hasil_runs[0] if hasil_runs else None)
    if hasil_satu:
        fig = fig_konvergensi_gabungan(hasil_satu, hasil_runs)
        st.pyplot(fig, use_container_width=True)
