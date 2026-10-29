from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, List, Tuple

from ag.data import DataJadwal

# Tipe alias
Kromosom = List[Tuple[int, int]]


def hitung_pelanggaran(k: Kromosom, data: DataJadwal) -> Dict[str, int]:
    c_dosen:  Counter = Counter()
    c_ruang:  Counter = Counter()
    c_kelas:  Counter = Counter()
    kapasitas_kurang = 0

    for i, (t, r) in enumerate(k):
        c_dosen[(t, data.dosen_idx[i])] += 1
        c_ruang[(t, r)] += 1
        c_kelas[(t, data.kelas_idx[i])] += 1
        if data.kapasitas[r] < data.ukuran[i]:
            kapasitas_kurang += 1

    def _bentrok(c: Counter) -> int:
        return sum(v - 1 for v in c.values() if v > 1)

    return {
        "H1_dosen":     _bentrok(c_dosen),
        "H2_ruang":     _bentrok(c_ruang),
        "H3_kelas":     _bentrok(c_kelas),
        "H4_kapasitas": kapasitas_kurang,
    }


def total_pelanggaran(k: Kromosom, data: DataJadwal) -> int:
    return sum(hitung_pelanggaran(k, data).values())


def hitung_fitness(k: Kromosom, data: DataJadwal) -> float:
    return 1.0 / (1.0 + total_pelanggaran(k, data))


def hitung_soft(k: Kromosom, data: DataJadwal) -> Dict[str, int]:
    # S1 — sesi di luar slot preferensi dosen
    pref = sum(
        1 for i, (t, _) in enumerate(k)
        if (t % data.n_slot) not in data.pref_slot[data.dosen_idx[i]]
    )

    # S2 — jeda panjang antar sesi kelas dalam satu hari
    per_kelas_hari: Dict[Tuple[int, int], List[int]] = defaultdict(list)
    for i, (t, _) in enumerate(k):
        per_kelas_hari[(data.kelas_idx[i], t // data.n_slot)].append(t % data.n_slot)

    jeda = 0
    for slots in per_kelas_hari.values():
        s = sorted(slots)
        jeda += sum(max(0, b - a - 1) for a, b in zip(s, s[1:]))

    return {"S1_preferensi_dosen": pref, "S2_jeda_panjang": jeda}
