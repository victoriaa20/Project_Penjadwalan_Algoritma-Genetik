import streamlit as st

from ag.tampilan import bangun_daftar, bangun_tabel_hari_slot, verifikasi_independen
from ui.komponen import (
    inject_css, page_header, render_badge,
    render_empty_state, render_daftar_sesi_harian, WARNA_KELAS,
)
from ui.state import init_session_state, ada_hasil_apapun, get_run_terbaik

inject_css()
init_session_state()

page_header("📅 Jadwal Terbaik", "Matriks hari × slot dan daftar sesi jadwal hasil optimasi terbaik.")

data = st.session_state.data

# Cek ketersediaan hasil
if not ada_hasil_apapun():
    render_empty_state(
        judul="Belum ada jadwal.",
        isi="Jalankan AG terlebih dahulu untuk mendapatkan jadwal terbaik.",
        ikon="📅",
    )
    st.stop()

run_terbaik = get_run_terbaik()
k_terbaik   = run_terbaik["kromosom"]
df_jadwal   = bangun_daftar(k_terbaik, data)
tabel_hs    = bangun_tabel_hari_slot(k_terbaik, data)

# Simpan ke session_state untuk digunakan di halaman Ekspor
st.session_state["_df_jadwal"]  = df_jadwal
st.session_state["_tabel_hs"]   = tabel_hs


# Verifikasi Independen
valid, pesan_error = verifikasi_independen(df_jadwal, data)

col_v, _ = st.columns([3, 4])
with col_v:
    if valid:
        st.markdown(
            render_badge("✅ Valid — Tanpa Bentrok Dosen/Ruang/Kelas & Kapasitas Cukup", "valid")
            + f"&nbsp;&nbsp;<span style='font-size:12px; color:var(--text-secondary);'>seed {run_terbaik.get('seed','?')} | fitness {run_terbaik['fitness_terbaik']:.4f}</span>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            render_badge(f"❌ {len(pesan_error)} Pelanggaran Terdeteksi", "bentrok"),
            unsafe_allow_html=True
        )
        with st.expander("Lihat detail pelanggaran"):
            for p in pesan_error:
                st.warning(p)

st.markdown("---")

# Tabs: Matriks & Daftar Sesi
tab_matriks, tab_daftar, tab_harian = st.tabs(
    ["🗓️ Matriks Hari × Slot", "📋 Daftar Sesi", "📆 Jadwal Harian"]
)

# Tab 1 — Matriks Hari × Slot
with tab_matriks:
    st.markdown("#### Tabel Jadwal Hari × Slot (5 Slot × 5 Hari)")
    st.caption("Setiap sel menampilkan: Nama Mata Kuliah [Kelas] | Nama Singkat Dosen · Ruang")

    def _warna_sel(teks: str) -> str:
        for kelas, warna in WARNA_KELAS.items():
            if f"[{kelas}]" in teks:
                return warna
        return "#7FA9B8"

    header_html = "<tr><th style='background:var(--primary);color:#fff;padding:10px;border-radius:12px;min-width:110px;'>Slot \\ Hari</th>"
    for hari in data.hari:
        header_html += f"<th style='background:var(--primary);color:#fff;padding:10px;border-radius:12px;text-align:center;min-width:140px;'>{hari}</th>"
    header_html += "</tr>"

    rows_html = ""
    for slot_idx, slot in enumerate(data.slot):
        rows_html += f"<tr><td style='font-size:12px;font-weight:500;padding:8px 12px;color:var(--text-secondary);white-space:nowrap;min-width:110px;'>{slot}</td>"
        for hari_idx, hari in enumerate(data.hari):
            sel_teks = tabel_hs.iloc[slot_idx, hari_idx] if not tabel_hs.empty else ""
            if sel_teks:
                warna = _warna_sel(sel_teks)
                baris_sel = sel_teks.replace("\n\n", "<br><hr style='border:none;border-top:1px solid #ddd;margin:4px 0;'>").replace("\n", "<br>")
                cell = (
                    f'<td style="background:var(--bg-card-inner);border-radius:12px;border:1px solid var(--border-solid);'
                    f'padding:10px 12px;vertical-align:top;font-size:11px;position:relative;min-width:140px;word-break:break-word;">'
                    f'<div style="position:absolute;left:0;top:0;bottom:0;width:3px;background:{warna};border-radius:3px 0 0 3px;"></div>'
                    f'<div style="padding-left:8px;">{baris_sel}</div>'
                    f'</td>'
                )
            else:
                cell = "<td style='background:#F1F4F5;border-radius:12px;min-width:140px;'></td>"
            rows_html += cell
        rows_html += "</tr>"

    tabel_html = (
        '<div style="overflow-x:auto; max-width:100%; border-radius:16px; padding:4px 0;">'
        '<table style="border-collapse:separate;border-spacing:6px;width:100%;min-width:750px;">'
        f'{header_html}'
        f'{rows_html}'
        '</table>'
        '</div>'
    )
    st.html(tabel_html)

    # warna kelas
    st.markdown("<br>", unsafe_allow_html=True)
    legend_html = "<div style='display:flex;gap:16px;flex-wrap:wrap;'>"
    for kelas, warna in WARNA_KELAS.items():
        legend_html += f"<div style='display:flex;align-items:center;gap:6px;font-size:12px;'><div style='width:10px;height:10px;border-radius:2px;background:{warna};'></div>{kelas}</div>"
    legend_html += "</div>"
    st.html(legend_html)

# Tab 2 — Daftar Sesi dengan Filter
with tab_daftar:
    st.markdown("#### Daftar Sesi Lengkap")

    # Filter
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        filter_hari = st.multiselect("Filter Hari", options=data.hari)
    with col_f2:
        filter_kelas = st.multiselect("Filter Kelas", options=list(data.kelas.keys()))
    with col_f3:
        filter_dosen = st.multiselect("Filter Dosen", options=[v[0] for v in data.dosen.values()])
    with col_f4:
        filter_ruang = st.multiselect("Filter Ruang", options=[v[0] for v in data.ruang.values()])

    cari = st.text_input("🔍 Cari (kode/mata kuliah/kelas/dosen/ruang)", "")

    df_filter = df_jadwal.copy()
    if filter_hari:  df_filter = df_filter[df_filter["Hari"].isin(filter_hari)]
    if filter_kelas: df_filter = df_filter[df_filter["Kelas"].isin(filter_kelas)]
    if filter_dosen: df_filter = df_filter[df_filter["Dosen"].isin(filter_dosen)]
    if filter_ruang: df_filter = df_filter[df_filter["Ruang"].isin(filter_ruang)]
    if cari:
        mask = df_filter.apply(lambda row: cari.lower() in str(row.values).lower(), axis=1)
        df_filter = df_filter[mask]

    st.markdown(f"Menampilkan **{len(df_filter)}** dari **{len(df_jadwal)}** sesi.")
    st.dataframe(
        df_filter.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Hari":         st.column_config.TextColumn("Hari", width=80),
            "Jam":          st.column_config.TextColumn("Jam", width=120),
            "Kode":         st.column_config.TextColumn("Kode", width=70),
            "Mata Kuliah":  st.column_config.TextColumn("Mata Kuliah", width=230),
            "Kelas":        st.column_config.TextColumn("Kelas", width=80),
            "Dosen":        st.column_config.TextColumn("Dosen", width=200),
            "Ruang":        st.column_config.TextColumn("Ruang", width=100),
            "SKS":          st.column_config.NumberColumn("SKS", width=60),
        }
    )

# Tab 3 — Jadwal Harian
with tab_harian:
    hari_terpilih = st.selectbox("Pilih Hari", data.hari)
    st.markdown(f"#### Sesi pada hari **{hari_terpilih}**")
    render_daftar_sesi_harian(df_jadwal, hari_terpilih)
