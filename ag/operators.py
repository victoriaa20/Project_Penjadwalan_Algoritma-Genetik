from __future__ import annotations

import random
from typing import List, Tuple

from ag.data import DataJadwal

# Tipe alias
Kromosom = List[Tuple[int, int]]


# Inisialisasi

def buat_individu(rng: random.Random, data: DataJadwal) -> Kromosom:
    return [
        (rng.randrange(data.n_timeslot), rng.randrange(data.n_ruang))
        for _ in range(data.n_gen)
    ]


def buat_populasi(ukuran: int, rng: random.Random, data: DataJadwal) -> List[Kromosom]:
    return [buat_individu(rng, data) for _ in range(ukuran)]


# Seleksi

def seleksi_roulette(
    pop: List[Kromosom],
    fit: List[float],
    rng: random.Random,
    n: int,
) -> List[Kromosom]:
    return rng.choices(pop, weights=fit, k=n)


def seleksi_turnamen(
    pop: List[Kromosom],
    fit: List[float],
    rng: random.Random,
    n: int,
    k: int,
) -> List[Kromosom]:
    hasil: List[Kromosom] = []
    for _ in range(n):
        peserta = rng.sample(range(len(pop)), k)
        pemenang = max(peserta, key=lambda i: fit[i])
        hasil.append(pop[pemenang])
    return hasil


def pilih_orangtua(
    pop: List[Kromosom],
    fit: List[float],
    rng: random.Random,
    param,            # ParameterGA — forward ref untuk hindari circular import
    n: int = 2,
) -> List[Kromosom]:
    if param.metode_seleksi == "roulette":
        return seleksi_roulette(pop, fit, rng, n)
    if param.metode_seleksi == "turnamen":
        return seleksi_turnamen(pop, fit, rng, n, param.k_turnamen)
    raise ValueError(f"metode_seleksi tidak dikenal: {param.metode_seleksi!r}")


# Crossover

def crossover_satu_titik(
    a: Kromosom,
    b: Kromosom,
    rng: random.Random,
    data: DataJadwal,
) -> Tuple[Kromosom, Kromosom]:
    titik = rng.randint(1, data.n_gen - 1)
    return a[:titik] + b[titik:], b[:titik] + a[titik:]


def crossover_uniform(
    a: Kromosom,
    b: Kromosom,
    rng: random.Random,
) -> Tuple[Kromosom, Kromosom]:
    c1, c2 = [], []
    for ga, gb in zip(a, b):
        if rng.random() < 0.5:
            c1.append(ga); c2.append(gb)
        else:
            c1.append(gb); c2.append(ga)
    return c1, c2


def lakukan_crossover(
    a: Kromosom,
    b: Kromosom,
    rng: random.Random,
    param,
    data: DataJadwal,
) -> Tuple[Kromosom, Kromosom]:
    if rng.random() >= param.p_crossover:
        return list(a), list(b)           # tanpa crossover: salin orang tua
    if param.metode_crossover == "satu_titik":
        return crossover_satu_titik(a, b, rng, data)
    if param.metode_crossover == "uniform":
        return crossover_uniform(a, b, rng)
    raise ValueError(f"metode_crossover tidak dikenal: {param.metode_crossover!r}")


# Mutasi

def mutasi(
    k: Kromosom,
    p_mutasi: float,
    rng: random.Random,
    data: DataJadwal,
) -> Kromosom:
    hasil = list(k)
    for i, (t, r) in enumerate(hasil):
        if rng.random() < p_mutasi:
            jenis = rng.choice(("waktu", "ruang", "keduanya"))
            if jenis in ("waktu", "keduanya"):
                t = rng.randrange(data.n_timeslot)
            if jenis in ("ruang", "keduanya"):
                r = rng.randrange(data.n_ruang)
            hasil[i] = (t, r)
    return hasil
