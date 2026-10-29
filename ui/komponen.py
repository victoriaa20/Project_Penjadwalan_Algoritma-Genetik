from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

WARNA_KELAS: Dict[str, str] = {
    "I-A":   "#0F5F7F",
    "I-B":   "#2E9E6B",
    "III-A": "#7A6FC9",
    "III-B": "#E08A3C",
    "V-A":   "#D9648F",
    "V-B":   "#2BB3B1",
}



def inject_css() -> None:
    css_path = os.path.join(os.path.dirname(__file__), "..", "assets", "style.css")
    css_path = os.path.normpath(css_path)
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)



def sapaan() -> str:
    jam = datetime.now().hour
    if 5 <= jam < 11:
        return "Selamat Pagi"
    elif 11 <= jam < 15:
        return "Selamat Siang"
    elif 15 <= jam < 18:
        return "Selamat Sore"
    else:
        return "Selamat Malam"


def tanggal_hari_ini() -> str:
    HARI_ID = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu","Minggu"]
    BULAN_ID = ["","Januari","Februari","Maret","April","Mei","Juni",
                "Juli","Agustus","September","Oktober","November","Desember"]
    now = datetime.now()
    return f"{HARI_ID[now.weekday()]}, {now.day} {BULAN_ID[now.month]} {now.year}"



def render_hero(
    judul: Optional[str] = None,
    subjudul: str = "Optimasi Penjadwalan Kuliah — Algoritma Genetika",
    tampilkan_tombol_run: bool = True,
    ada_hasil: bool = False,
) -> None:
    sapa = sapaan()
    tgl  = tanggal_hari_ini()
    teks_judul = judul or f"{sapa}, Tim AG! 🧬"

    hero_html = f"""
    <div class="jadwalga-hero">
      <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:16px;">
        <div>
          <p style="font-size:13px; color:rgba(255,255,255,0.65); margin-bottom:8px; font-weight:300;">{tgl}</p>
          <h1 class="jadwalga-hero-title">{teks_judul}</h1>
          <p class="jadwalga-hero-sub">{subjudul}</p>
        </div>
      </div>
    </div>
    """
    st.markdown(hero_html, unsafe_allow_html=True)



def render_stat_card(
    label: str,
    nilai: str,
    ikon: str = "📊",
    delta: Optional[str] = None,
    delta_positif: Optional[bool] = None,
) -> None:
    delta_color = ""
    if delta_positif is True:
        delta_color = "color: var(--positive);"
    elif delta_positif is False:
        delta_color = "color: var(--negative);"

    delta_html = ""
    if delta:
        delta_html = f'<div class="stat-delta" style="{delta_color}">{delta}</div>'

    html = f"""
    <div class="stat-card">
      <div class="stat-icon-box">{ikon}</div>
      <div class="stat-label" title="{label}">{label}</div>
      <div class="stat-value">{nilai}</div>
      {delta_html}
    </div>
    """
    st.html(html)



def render_highlight_card(
    judul: str,
    isi: str,
    label_tombol: Optional[str] = None,
) -> None:
    tombol_html = ""
    if label_tombol:
        tombol_html = f'<div style="margin-top:20px;"><button class="btn btn-solid-light">{label_tombol}</button></div>'

    html = f"""
    <div class="jadwalga-highlight-card">
      <h3>{judul}</h3>
      <p>{isi}</p>
      {tombol_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)



_BADGE_CLASS = {
    "valid":       "badge-valid",
    "kapasitas":   "badge-capacity",
    "bentrok":     "badge-conflict",
    "preferensi":  "badge-preference",
    "netral":      "badge-neutral",
}

def render_badge(teks: str, tipe: str = "netral") -> str:
    kls = _BADGE_CLASS.get(tipe.lower(), "badge-neutral")
    return f'<span class="badge {kls}">{teks}</span>'


def tampilkan_badge(teks: str, tipe: str = "netral") -> None:
    st.markdown(render_badge(teks, tipe), unsafe_allow_html=True)



def render_constraint_checklist(
    h1: int = 0, h2: int = 0, h3: int = 0, h4: int = 0,
    s1: Optional[int] = None, s2: Optional[int] = None,
) -> None:
    def _item(label: str, pelanggaran: int, lunak: bool = False) -> str:
        if lunak:
            if pelanggaran is None:
                ikon = '<span class="constraint-icon-info">ℹ️</span>'
                teks = f"<span style='color:var(--text-muted)'>{label} — belum dihitung</span>"
            elif pelanggaran == 0:
                ikon = '<span class="constraint-icon-info">ℹ️</span>'
                teks = f"{label} — <span style='color:var(--positive)'>0 pelanggaran</span>"
            else:
                ikon = '<span class="constraint-icon-info">⚠️</span>'
                teks = f"{label} — <span style='color:var(--warning)'>{pelanggaran} pelanggaran</span>"
        else:
            if pelanggaran == 0:
                ikon = '<span class="constraint-icon-pass">✅</span>'
                teks = f"{label}"
            else:
                ikon = '<span class="constraint-icon-fail">❌</span>'
                teks = f"{label} — <strong style='color:var(--negative)'>{pelanggaran} bentrok</strong>"
        return f'<div class="constraint-item">{ikon} <div style="flex:1; min-width:0; word-break:break-word;">{teks}</div></div>'

    html = f"""
    <div class="jadwalga-card" style="padding: 16px 20px;">
      <div class="jadwalga-card-title">📋 Catatan Kendala</div>
      {_item("H1 Dosen tanpa bentrok", h1)}
      {_item("H2 Ruang tanpa bentrok", h2)}
      {_item("H3 Kelas tanpa bentrok", h3)}
      {_item("H4 Kapasitas ruang mencukupi", h4)}
      {_item("S1 Sesi di luar preferensi dosen", s1, lunak=True)}
      {_item("S2 Jeda panjang antar sesi", s2, lunak=True)}
    </div>
    """
    st.html(html)



def render_session_item(
    mata_kuliah: str,
    kelas: str,
    jam: str,
    ruang: str,
    dosen: str,
) -> str:
    warna = WARNA_KELAS.get(kelas, "#0F5F7F")
    return (
        '<div class="session-item">'
        f'<div class="session-bar" style="background:{warna};"></div>'
        '<div class="session-content">'
        f'<div class="session-title">{mata_kuliah} <span style="font-size:11px;color:var(--text-muted);">[{kelas}]</span></div>'
        f'<div class="session-meta">🕐 {jam} &nbsp;·&nbsp; 📍 {ruang} &nbsp;·&nbsp; 👤 {dosen}</div>'
        '</div>'
        '</div>'
    )


def render_daftar_sesi_harian(df_jadwal, hari: str) -> None:
    df_hari = df_jadwal[df_jadwal["Hari"] == hari].copy()
    if df_hari.empty:
        st.html(
            '<div class="empty-state" style="padding:24px;">'
            '<div class="empty-state-icon">📅</div>'
            '<div class="empty-state-body">Tidak ada sesi pada hari ini.</div>'
            '</div>'
        )
        return

    html = ""
    for _, row in df_hari.iterrows():
        html += render_session_item(
            row["Mata Kuliah"], row["Kelas"], row["Jam"], row["Ruang"], row["Dosen"]
        )
    st.html(html)



def render_empty_state(
    judul: str = "Belum ada hasil.",
    isi: str = "Jalankan AG untuk membuat jadwal pertama.",
    ikon: str = "🧬",
) -> None:
    html = f"""
    <div class="empty-state jadwalga-card">
      <div class="empty-state-icon">{ikon}</div>
      <div class="empty-state-title">{judul}</div>
      <div class="empty-state-body">{isi}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)



def page_header(judul: str, subjudul: str = "") -> None:
    subjudul_html = f'<p style="color:var(--text-secondary); margin-top:4px; font-size:14px;">{subjudul}</p>' if subjudul else ""
    st.markdown(
        f'<h2 style="font-size:24px; font-weight:400; margin-bottom:4px;">{judul}</h2>{subjudul_html}',
        unsafe_allow_html=True,
    )
    st.markdown("<hr style='border:none;border-top:1px solid var(--divider);margin:12px 0 20px;'>", unsafe_allow_html=True)



def warna_kelas(kelas: str) -> str:
    return WARNA_KELAS.get(kelas, "#7FA9B8")
