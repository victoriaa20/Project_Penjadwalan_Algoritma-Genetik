from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

import pandas as pd

_HARI_DEFAULT: List[str] = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
_SLOT_DEFAULT: List[str] = [
    "07.00–09.30",
    "09.30–12.00",
    "12.00–14.30",
    "14.30–17.00",
    "17.00–19.30",
]

# Dosen: id 
_DOSEN_DEFAULT: Dict[str, Tuple[str, str, Set[int]]] = {
    "D1": ("Felicia Sylviana, S.T., M.M.",               "Felicia",  {0, 1, 2}),
    "D2": ("Widiatry, S.T., M.T.",                        "Widiatry", {0, 1}),
    "D3": ("Efrans Christian, S.T., M.T.",                "Efrans",   {1, 2, 3}),
    "D4": ("Deddy Ronaldo, S.T., M.T.",                   "Deddy",    {0, 1, 2}),
    "D5": ("Devi Karolita, S.Kom., M.Kom., Ph.D.",        "Devi",     {0, 1, 2}),
    "D6": ("Agus Sehatman Saragih, S.T., M.Eng.",         "Agus",     {1, 2, 3}),
    "D7": ("Septian Geges, S.Kom., M.Kom.",               "Septian",  {0, 1, 2, 3}),
    "D8": ("Nahumi Nugrahaningsih, S.T., M.T., Ph.D.",    "Nahumi",   {0, 1}),
}

# Ruang: id 
_RUANG_DEFAULT: Dict[str, Tuple[str, int]] = {
    "R1": ("GKTA-LT4", 50),
    "R2": ("GKTA-LT5", 50),
    "R3": ("FT4",      40),
    "R4": ("FT5",      40),
    "R5": ("FT6",      35),
}

# Kelas mahasiswa
_KELAS_DEFAULT: Dict[str, int] = {
    "I-A":   45,
    "I-B":   38,
    "III-A": 36,
    "III-B": 33,
    "V-A":   30,
    "V-B":   28,
}

# Sesi kuliah: (kode, mata_kuliah, kelas, id_dosen, sks)
_MATKUL_DEFAULT: List[Tuple[str, str, str, str, int]] = [
    ("MK01", "Aljabar Linear Matriks",              "I-A",   "D1", 3),
    ("MK02", "Pengantar Teknik Informatika",         "I-A",   "D1", 3),
    ("MK03", "Metodologi Penelitian",               "V-A",   "D1", 3),
    ("MK04", "Logika Diskrit",                      "I-A",   "D2", 3),
    ("MK05", "Algoritma dan Pemrograman I",         "I-A",   "D2", 3),
    ("MK06", "Pemrograman Berorientasi Objek",      "III-A", "D2", 3),
    ("MK07", "Logika Diskrit",                      "I-B",   "D3", 3),
    ("MK08", "Pemrograman Berorientasi Objek",      "III-B", "D3", 3),
    ("MK09", "Basis Data I",                        "III-B", "D3", 3),
    ("MK10", "Data Mining",                         "V-B",   "D3", 3),
    ("MK11", "Analisis dan Desain Perangkat Lunak", "V-B",   "D4", 3),
    ("MK12", "Pengolahan Citra Digital",            "V-B",   "D8", 3),
    ("MK13", "Metodologi Penelitian",               "V-B",   "D5", 3),
    ("MK14", "Interaksi Manusia dan Komputer",      "III-A", "D5", 3),
    ("MK15", "Basis Data I",                        "III-A", "D5", 3),
    ("MK16", "Keamanan Data dan Informasi",         "V-A",   "D6", 3),
    ("MK17", "Kompleksitas Algoritma",              "III-A", "D6", 3),
    ("MK18", "Sistem Digital",                      "I-B",   "D7", 3),
    ("MK19", "Jaringan Syaraf Tiruan",              "V-A",   "D7", 3),
    ("MK20", "Sistem Digital",                      "I-A",   "D8", 3),
]

# Seed untuk 10 run pengujian awal (sesuai ketentuan)
SEEDS_DEFAULT: List[int] = [11, 22, 33, 44, 55, 66, 77, 88, 99, 110]


# Dataclass DataJadwal — membungkus data + indeks turunan

@dataclass
class DataJadwal:
    # Entitas utama
    hari:   List[str]                               = field(default_factory=lambda: list(_HARI_DEFAULT))
    slot:   List[str]                               = field(default_factory=lambda: list(_SLOT_DEFAULT))
    dosen:  Dict[str, Tuple[str, str, Set[int]]]    = field(default_factory=lambda: dict(_DOSEN_DEFAULT))
    ruang:  Dict[str, Tuple[str, int]]              = field(default_factory=lambda: dict(_RUANG_DEFAULT))
    kelas:  Dict[str, int]                          = field(default_factory=lambda: dict(_KELAS_DEFAULT))
    matkul: List[Tuple[str, str, str, str, int]]    = field(default_factory=lambda: list(_MATKUL_DEFAULT))

    # Indeks turunan (diisi oleh __post_init__)
    id_dosen:   List[str] = field(init=False, repr=False, default_factory=list)
    id_ruang:   List[str] = field(init=False, repr=False, default_factory=list)
    id_kelas:   List[str] = field(init=False, repr=False, default_factory=list)
    n_gen:      int       = field(init=False, repr=False, default=0)
    n_hari:     int       = field(init=False, repr=False, default=0)
    n_slot:     int       = field(init=False, repr=False, default=0)
    n_timeslot: int       = field(init=False, repr=False, default=0)
    n_ruang:    int       = field(init=False, repr=False, default=0)
    dosen_idx:  List[int] = field(init=False, repr=False, default_factory=list)
    kelas_idx:  List[int] = field(init=False, repr=False, default_factory=list)
    ukuran:     List[int] = field(init=False, repr=False, default_factory=list)
    kapasitas:  List[int] = field(init=False, repr=False, default_factory=list)
    pref_slot:  List[Set[int]] = field(init=False, repr=False, default_factory=list)

    def __post_init__(self) -> None:
        self._rebuild()

    def _rebuild(self) -> None:
        self.id_dosen   = list(self.dosen)
        self.id_ruang   = list(self.ruang)
        self.id_kelas   = list(self.kelas)

        self.n_gen      = len(self.matkul)
        self.n_hari     = len(self.hari)
        self.n_slot     = len(self.slot)
        self.n_timeslot = self.n_hari * self.n_slot
        self.n_ruang    = len(self.ruang)

        self.dosen_idx  = [self.id_dosen.index(m[3]) for m in self.matkul]
        self.kelas_idx  = [self.id_kelas.index(m[2]) for m in self.matkul]
        self.ukuran     = [self.kelas[m[2]] for m in self.matkul]
        self.kapasitas  = [self.ruang[r][1] for r in self.id_ruang]
        self.pref_slot  = [self.dosen[d][2] for d in self.id_dosen]

    # Helper: konversi timeslot integer <-> (hari_str, slot_str)

    def nama_timeslot(self, t: int) -> Tuple[str, str]:
        return self.hari[t // self.n_slot], self.slot[t % self.n_slot]

    # Helper: DataFrame untuk tampilan di UI

    def df_matkul(self) -> pd.DataFrame:
        rows = []
        for i, (kode, mk, kls, d, sks) in enumerate(self.matkul):
            rows.append({
                "Kode":       kode,
                "Mata Kuliah": mk,
                "Kelas":      kls,
                "ID Dosen":   d,
                "Dosen":      self.dosen[d][0],
                "SKS":        sks,
                "Jml Mhs":    self.ukuran[i],
            })
        return pd.DataFrame(rows)

    def df_dosen(self) -> pd.DataFrame:
        rows = []
        for d_id, (nama, singkat, prefs) in self.dosen.items():
            pref_str = ", ".join(self.slot[s] for s in sorted(prefs)) if prefs else "–"
            rows.append({
                "ID":     d_id,
                "Nama":   nama,
                "Singkat": singkat,
                "Preferensi Slot": pref_str,
            })
        return pd.DataFrame(rows)

    def df_ruang(self) -> pd.DataFrame:
        return pd.DataFrame(
            [{"ID": r_id, "Ruang": info[0], "Kapasitas": info[1]}
             for r_id, info in self.ruang.items()]
        )

    def df_kelas(self) -> pd.DataFrame:
        return pd.DataFrame(
            [{"Kelas": k, "Jumlah Mahasiswa": n}
             for k, n in self.kelas.items()]
        )

    def df_slot(self) -> pd.DataFrame:
        rows = []
        for t in range(self.n_timeslot):
            h, s = self.nama_timeslot(t)
            rows.append({"Timeslot": t, "Hari": h, "Slot": s})
        return pd.DataFrame(rows)

    def beban_dosen(self) -> pd.DataFrame:
        df = self.df_matkul()
        return df.groupby("Dosen").size().rename("Jumlah Sesi").to_frame().reset_index()

    def beban_kelas(self) -> pd.DataFrame:
        df = self.df_matkul()
        return df.groupby("Kelas").size().rename("Jumlah Sesi").to_frame().reset_index()


# Factory function

def buat_data_default() -> DataJadwal:
    return DataJadwal()
