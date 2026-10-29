from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple

import pandas as pd

from ag.data import DataJadwal

# Tipe alias
Kromosom = List[Tuple[int, int]]


def bangun_daftar(k: Kromosom, data: DataJadwal) -> pd.DataFrame:
    baris = []
    for i, (t, r) in enumerate(k):
        kode, mk, kelas, d_id, sks = data.matkul[i]
        hari, jam = data.nama_timeslot(t)
        baris.append({
            "Hari":        hari,
            "Jam":         jam,
            "Kode":        kode,
            "Mata Kuliah": mk,
            "Kelas":       kelas,
            "Dosen":       data.dosen[d_id][0],
            "Ruang":       data.ruang[data.id_ruang[r]][0],
            "SKS":         sks,
            "_h":          t // data.n_slot,
            "_s":          t % data.n_slot,
        })

    df = (
        pd.DataFrame(baris)
        .sort_values(["_h", "_s", "Ruang"])
        .drop(columns=["_h", "_s"])
        .reset_index(drop=True)
    )
    return df


def bangun_tabel_hari_slot(k: Kromosom, data: DataJadwal) -> pd.DataFrame:
    sel: Dict[Tuple[int, int], List[str]] = defaultdict(list)

    for i, (t, r) in enumerate(k):
        kode, mk, kelas, d_id, _ = data.matkul[i]
        singkat = data.dosen[d_id][1]
        nama_ruang = data.ruang[data.id_ruang[r]][0]
        sel[(t % data.n_slot, t // data.n_slot)].append(
            f"{mk} [{kelas}]\n{singkat} | {nama_ruang}"
        )

    tabel = pd.DataFrame("", index=data.slot, columns=data.hari)
    for (s, h), isi in sel.items():
        tabel.iloc[s, h] = "\n\n".join(isi)

    tabel.index.name = "Slot \\ Hari"
    return tabel


def verifikasi_independen(
    df_jadwal: pd.DataFrame,
    data: DataJadwal,
) -> Tuple[bool, List[str]]:
    pesan: List[str] = []

    # H1 — bentrok dosen
    dup_dosen = df_jadwal[df_jadwal.duplicated(["Hari", "Jam", "Dosen"], keep=False)]
    if not dup_dosen.empty:
        for _, row in dup_dosen.iterrows():
            pesan.append(
                f"[H1 Bentrok Dosen] {row['Dosen']} — {row['Hari']} {row['Jam']}"
            )

    # H2 — bentrok ruang
    dup_ruang = df_jadwal[df_jadwal.duplicated(["Hari", "Jam", "Ruang"], keep=False)]
    if not dup_ruang.empty:
        for _, row in dup_ruang.iterrows():
            pesan.append(
                f"[H2 Bentrok Ruang] {row['Ruang']} — {row['Hari']} {row['Jam']}"
            )

    # H3 — bentrok kelas
    dup_kelas = df_jadwal[df_jadwal.duplicated(["Hari", "Jam", "Kelas"], keep=False)]
    if not dup_kelas.empty:
        for _, row in dup_kelas.iterrows():
            pesan.append(
                f"[H3 Bentrok Kelas] {row['Kelas']} — {row['Hari']} {row['Jam']}"
            )

    # H4 — kapasitas ruang
    kap_map = {info[0]: info[1] for info in data.ruang.values()}
    for _, row in df_jadwal.iterrows():
        kapasitas = kap_map.get(row["Ruang"], 0)
        jml_mhs   = data.kelas.get(row["Kelas"], 0)
        if kapasitas < jml_mhs:
            pesan.append(
                f"[H4 Kapasitas] {row['Mata Kuliah']} ({row['Kelas']}, {jml_mhs} mhs) "
                f"→ {row['Ruang']} (kapasitas {kapasitas})"
            )

    return len(pesan) == 0, pesan
