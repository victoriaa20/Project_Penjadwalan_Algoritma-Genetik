from __future__ import annotations

import streamlit as st

from ag.data import DataJadwal, buat_data_default
from ag.engine import ParameterGA

# Kunci session_state yang digunakan aplikasi
_KEYS = (
    "data",
    "param",
    "hasil_run_tunggal",
    "hasil_runs",
    "run_terbaik",
    "hasil_kombinasi",
    "df_runs",
    "df_ringkasan",
)


def init_session_state() -> None:
    if "data" not in st.session_state:
        st.session_state.data = buat_data_default()
    if "param" not in st.session_state:
        st.session_state.param = ParameterGA()
    for key in ("hasil_run_tunggal", "hasil_runs", "run_terbaik",
                "hasil_kombinasi", "df_runs", "df_ringkasan"):
        if key not in st.session_state:
            st.session_state[key] = None


def reset_hasil_run() -> None:
    for key in ("hasil_run_tunggal", "hasil_runs", "run_terbaik",
                "hasil_kombinasi", "df_runs", "df_ringkasan"):
        st.session_state[key] = None
    st.toast("Hasil run berhasil direset.", icon="🔄")


def reset_semua() -> None:
    for key in _KEYS:
        if key in st.session_state:
            del st.session_state[key]
    st.toast("Semua data berhasil direset ke default.", icon="🗑️")


def ada_hasil_run_tunggal() -> bool:
    return st.session_state.get("hasil_run_tunggal") is not None


def ada_hasil_10_run() -> bool:
    h = st.session_state.get("hasil_runs")
    return h is not None and len(h) > 0


def ada_hasil_apapun() -> bool:
    return ada_hasil_run_tunggal() or ada_hasil_10_run()


def get_run_terbaik():
    rt = st.session_state.get("run_terbaik")
    if rt is not None:
        return rt
    return st.session_state.get("hasil_run_tunggal")
