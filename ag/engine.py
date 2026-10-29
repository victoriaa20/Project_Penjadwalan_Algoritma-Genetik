from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from ag.data import DataJadwal
from ag.fitness import hitung_fitness, hitung_soft, total_pelanggaran
from ag.operators import buat_populasi, lakukan_crossover, mutasi, pilih_orangtua

# Tipe alias
Kromosom = List[Tuple[int, int]]
HasilRun = Dict[str, Any]



@dataclass
class ParameterGA:
    ukuran_populasi:  int   = 100
    n_generasi:       int   = 300
    p_crossover:      float = 0.8
    p_mutasi:         float = 0.05
    metode_seleksi:   str   = "turnamen"
    metode_crossover: str   = "uniform"
    k_turnamen:       int   = 3
    n_elit:           int   = 2



def jalankan_ga(
    param: ParameterGA,
    seed: int,
    data: DataJadwal,
    berhenti_jika_valid: bool = False,
    progress_callback: Optional[Callable[[int, Dict[str, Any]], None]] = None,
) -> HasilRun:
    rng = random.Random(seed)
    t0  = time.perf_counter()

    pop: List[Kromosom] = buat_populasi(param.ukuran_populasi, rng, data)
    riwayat_terbaik: List[float] = []
    riwayat_rata:    List[float] = []
    gen_valid: Optional[int] = None
    terbaik:   Optional[Kromosom] = None
    fit_terbaik: float = -1.0

    for gen in range(param.n_generasi + 1):
        fit = [hitung_fitness(k, data) for k in pop]
        urut = sorted(range(len(pop)), key=fit.__getitem__, reverse=True)

        if fit[urut[0]] > fit_terbaik:
            fit_terbaik = fit[urut[0]]
            terbaik     = pop[urut[0]]

        riwayat_terbaik.append(fit[urut[0]])
        riwayat_rata.append(sum(fit) / len(fit))

        if gen_valid is None and fit[urut[0]] == 1.0:
            gen_valid = gen

        # Laporan progres
        if progress_callback is not None:
            persen = int(gen / param.n_generasi * 100)
            progress_callback(persen, {
                "generasi":      gen,
                "fitness":       fit[urut[0]],
                "gen_valid":     gen_valid,
            })

        # Kondisi berhenti
        if gen == param.n_generasi or (berhenti_jika_valid and gen_valid is not None):
            break

        # Generasi berikutnya: elitisme + seleksi + crossover + mutasi
        baru: List[Kromosom] = [pop[i] for i in urut[:param.n_elit]]
        while len(baru) < param.ukuran_populasi:
            a, b = pilih_orangtua(pop, fit, rng, param, 2)
            c1, c2 = lakukan_crossover(a, b, rng, param, data)
            baru.append(mutasi(c1, param.p_mutasi, rng, data))
            if len(baru) < param.ukuran_populasi:
                baru.append(mutasi(c2, param.p_mutasi, rng, data))
        pop = baru

    return {
        "seed":             seed,
        "kromosom":         terbaik,
        "fitness_terbaik":  fit_terbaik,
        "fitness_rata_akhir": riwayat_rata[-1],
        "gen_valid":        gen_valid,
        "riwayat_terbaik":  riwayat_terbaik,
        "riwayat_rata":     riwayat_rata,
        "waktu_detik":      time.perf_counter() - t0,
    }



def jalankan_banyak_run(
    param: ParameterGA,
    seeds: List[int],
    data: DataJadwal,
    berhenti_jika_valid: bool = False,
    progress_callback: Optional[Callable[[int, int, Dict[str, Any]], None]] = None,
) -> Tuple[List[HasilRun], pd.DataFrame, pd.DataFrame]:
    hasil_runs: List[HasilRun] = []

    for idx, seed in enumerate(seeds):
        def _cb(persen: int, info: Dict[str, Any], _i: int = idx, _s: int = seed) -> None:
            if progress_callback:
                progress_callback(_i, persen, info)

        h = jalankan_ga(param, seed, data, berhenti_jika_valid, _cb)
        hasil_runs.append(h)

    df_runs = pd.DataFrame([{
        "Run":                               i + 1,
        "Seed":                              h["seed"],
        "Fitness Terbaik":                   h["fitness_terbaik"],
        "Fitness Rata-rata (generasi akhir)": h["fitness_rata_akhir"],
        "Generasi Valid Pertama":             h["gen_valid"],
        "Pelanggaran Keras":                  total_pelanggaran(h["kromosom"], data),
        "Waktu (s)":                          h["waktu_detik"],
    } for i, h in enumerate(hasil_runs)])

    num_cols = df_runs.drop(columns=["Run", "Seed"])
    df_ringkasan = pd.DataFrame({
        "Rata-rata":      num_cols.mean(numeric_only=True),
        "Simpangan Baku": num_cols.std(numeric_only=True),
        "Min":            num_cols.min(numeric_only=True),
        "Maks":           num_cols.max(numeric_only=True),
    }).round(4)

    return hasil_runs, df_runs.round(4), df_ringkasan


def kunci_terbaik(h: HasilRun, data: DataJadwal) -> Tuple[float, int]:
    soft = hitung_soft(h["kromosom"], data)
    return (-h["fitness_terbaik"], sum(soft.values()))



def jalankan_perbandingan_operator(
    param_dasar: ParameterGA,
    seeds: List[int],
    data: DataJadwal,
) -> Tuple[Dict[Tuple[str, str], List[HasilRun]], pd.DataFrame]:
    from dataclasses import replace

    kombinasi = [
        (s, c)
        for s in ("roulette", "turnamen")
        for c in ("satu_titik", "uniform")
    ]

    hasil_kombinasi: Dict[Tuple[str, str], List[HasilRun]] = {}
    for s, c in kombinasi:
        p = replace(param_dasar, metode_seleksi=s, metode_crossover=c)
        hasil_kombinasi[(s, c)] = [jalankan_ga(p, sd, data) for sd in seeds]

    baris = []
    for (s, c), lst in hasil_kombinasi.items():
        gv = [h["gen_valid"] for h in lst if h["gen_valid"] is not None]
        baris.append({
            "Seleksi":                       s,
            "Crossover":                     c,
            "Fitness Terbaik (rata-rata)":   float(np.mean([h["fitness_terbaik"] for h in lst])),
            "Run Valid":                     f"{len(gv)}/{len(lst)}",
            "Gen Valid (rata-rata)":         float(np.mean(gv)) if gv else float("nan"),
            "Gen Valid (std)":               float(np.std(gv, ddof=1)) if len(gv) > 1 else float("nan"),
            "Waktu (s, rata-rata)":          float(np.mean([h["waktu_detik"] for h in lst])),
        })

    return hasil_kombinasi, pd.DataFrame(baris).round(3)
