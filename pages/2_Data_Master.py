import streamlit as st

from ui.komponen import inject_css, page_header, render_stat_card, WARNA_KELAS
from ui.state import init_session_state

inject_css()
init_session_state()

data = st.session_state.data

page_header("📋 Data Master", "Entitas dan data bawaan yang digunakan oleh Algoritma Genetika.")

# Ringkasan jumlah entitas
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_stat_card("Sesi Kuliah", str(data.n_gen),       ikon="📚")
with col2:
    render_stat_card("Dosen",       str(len(data.dosen)),  ikon="👨‍🏫")
with col3:
    render_stat_card("Ruang",       str(len(data.ruang)),  ikon="🏫")
with col4:
    render_stat_card("Kelas",       str(len(data.kelas)),  ikon="👥")
with col5:
    render_stat_card("Timeslot",    str(data.n_timeslot),  ikon="🕐",
                     delta=f"{data.n_hari} hari × {data.n_slot} slot")

st.markdown("---")

tab_mk, tab_dosen, tab_ruang, tab_kelas, tab_slot = st.tabs(
    ["📚 Mata Kuliah", "👨‍🏫 Dosen", "🏫 Ruang", "👥 Kelas", "🕐 Slot Waktu"]
)

with tab_mk:
    st.markdown("#### Daftar Sesi Kuliah (20 Sesi)")
    df_mk = data.df_matkul()

    st.dataframe(
        df_mk,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Kode":       st.column_config.TextColumn("Kode", width=80),
            "Mata Kuliah": st.column_config.TextColumn("Mata Kuliah", width=230),
            "Kelas":      st.column_config.TextColumn("Kelas", width=80),
            "ID Dosen":   st.column_config.TextColumn("ID", width=60),
            "Dosen":      st.column_config.TextColumn("Nama Dosen", width=230),
            "SKS":        st.column_config.NumberColumn("SKS", width=60),
            "Jml Mhs":    st.column_config.NumberColumn("Jml Mhs", width=80),
        }
    )

    st.markdown("##### Beban Mengajar per Dosen")
    beban = data.beban_dosen()
    st.dataframe(beban, use_container_width=True, hide_index=True)

    st.markdown("##### Beban Kuliah per Kelas")
    beban_k = data.beban_kelas()
    st.dataframe(beban_k, use_container_width=True, hide_index=True)

with tab_dosen:
    st.markdown("#### Daftar Dosen & Preferensi Slot")
    df_dosen = data.df_dosen()
    st.dataframe(
        df_dosen,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID":    st.column_config.TextColumn("ID", width=60),
            "Nama":  st.column_config.TextColumn("Nama Lengkap", width=280),
            "Singkat": st.column_config.TextColumn("Singkat", width=80),
            "Preferensi Slot": st.column_config.TextColumn("Preferensi Slot", width=250),
        }
    )
    st.info("Preferensi slot dosen digunakan untuk menghitung kendala lunak S1 (tidak masuk ke fungsi fitness).", icon="ℹ️")

with tab_ruang:
    st.markdown("#### Daftar Ruang Kuliah & Kapasitas")
    df_ruang = data.df_ruang()
    st.dataframe(
        df_ruang,
        use_container_width=True,
        hide_index=True,
        column_config={
            "ID":       st.column_config.TextColumn("ID", width=60),
            "Ruang":    st.column_config.TextColumn("Nama Ruang", width=150),
            "Kapasitas": st.column_config.NumberColumn("Kapasitas (kursi)", width=130),
        }
    )

    st.markdown("##### Kapasitas vs Jumlah Mahasiswa Terbesar")
    min_kap = min(v[1] for v in data.ruang.values())
    max_mhs = max(data.kelas.values())
    if min_kap < max_mhs:
        st.warning(
            f"Kapasitas minimum ruang ({min_kap} kursi) lebih kecil dari kelas terbesar "
            f"({max_mhs} mhs). Kendala H4 perlu diperhatikan.",
            icon="⚠️"
        )
    else:
        st.success("Semua ruang mampu menampung kelas terbesar.", icon="✅")

with tab_kelas:
    st.markdown("#### Daftar Kelas Mahasiswa")
    df_kelas = data.df_kelas()

    # Tampilkan badge warna kelas
    kelas_html = ""
    for _, row in df_kelas.iterrows():
        warna = WARNA_KELAS.get(row["Kelas"], "#7FA9B8")
        kelas_html += (
            f'<div style="display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid var(--divider);">'
            f'<div style="width:12px; height:12px; border-radius:50%; background:{warna}; flex-shrink:0;"></div>'
            f'<span style="font-weight:500; min-width:70px;">{row["Kelas"]}</span>'
            f'<span style="color:var(--text-secondary);">{row["Jumlah Mahasiswa"]} mahasiswa</span>'
            f'</div>'
        )
    card_kelas = f'<div class="jadwalga-card" style="padding:16px 20px;">{kelas_html}</div>'
    st.html(card_kelas)

with tab_slot:
    st.markdown("#### Daftar Timeslot (5 Hari × 5 Slot)")
    df_slot = data.df_slot()

    import pandas as pd
    pivot = pd.pivot_table(
        df_slot, values="Timeslot", index="Slot", columns="Hari",
        aggfunc="first"
    )
    pivot = pivot.reindex(columns=data.hari, index=data.slot)
    st.dataframe(pivot, use_container_width=True)
    st.caption(
        f"Total {data.n_timeslot} timeslot. "
        f"Timeslot t: hari = t // {data.n_slot}, slot = t % {data.n_slot}. "
        f"Indeks 0 = {data.hari[0]} {data.slot[0]}, indeks {data.n_timeslot-1} = {data.hari[-1]} {data.slot[-1]}."
    )
