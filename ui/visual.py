
from __future__ import annotations

import io
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # backend non-interaktif untuk Streamlit
import matplotlib.pyplot as plt
import numpy as np

# rcParams sesuai style.json → charts.matplotlibRcParams
_RCPARAMS = {
    "figure.facecolor":     "none",
    "axes.facecolor":       "none",
    "axes.edgecolor":       "#E4E8EA",
    "axes.labelcolor":      "#5E6A70",
    "axes.spines.top":      False,
    "axes.spines.right":    False,
    "axes.grid":            True,
    "grid.color":           "#E4E8EA",
    "grid.linewidth":       0.8,
    "xtick.color":          "#8A969B",
    "ytick.color":          "#8A969B",
    "font.family":          "sans-serif",
    "font.size":            10,
    "legend.frameon":       False,
}

# Warna token 
_C_BEST   = "#0F5F7F"   
_C_MEAN   = "#7FA9B8"   
_C_VALID  = "#1F8A4C"  
_C_BAND   = "#0F5F7F"  


def _apply_rc() -> None:
    plt.rcParams.update(_RCPARAMS)


# (a) Grafik satu run

def plot_konvergensi_tunggal(
    hasil: Dict[str, Any],
    figsize: Tuple[float, float] = (8, 4),
) -> plt.Figure:
    _apply_rc()
    fig, ax = plt.subplots(figsize=figsize)

    riwayat_terbaik = hasil["riwayat_terbaik"]
    riwayat_rata    = hasil["riwayat_rata"]
    gen_valid       = hasil["gen_valid"]
    seed            = hasil.get("seed", "?")

    x = range(len(riwayat_terbaik))

    ax.plot(x, riwayat_terbaik,
            color=_C_BEST, linewidth=2.5, label="Fitness terbaik")
    ax.plot(x, riwayat_rata,
            color=_C_MEAN, linewidth=2.0, linestyle=(0, (4, 3)),
            alpha=0.8, label="Fitness rata-rata populasi")

    if gen_valid is not None:
        ax.axvline(gen_valid, color=_C_VALID, linestyle="--", linewidth=1.5,
                   label=f"Valid pertama (gen {gen_valid})")
        ax.scatter([gen_valid], [riwayat_terbaik[gen_valid]],
                   color=_C_VALID, s=60, zorder=5)

    ax.set_title(f"Konvergensi Run Terbaik (seed {seed})",
                 fontsize=12, color="#5E6A70", pad=10)
    ax.set_xlabel("Generasi", color="#5E6A70")
    ax.set_ylabel("Fitness", color="#5E6A70")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right")

    fig.tight_layout()
    return fig


# (b) Grafik rata-rata 10 run ± std-dev

def plot_konvergensi_10_run(
    hasil_runs: List[Dict[str, Any]],
    figsize: Tuple[float, float] = (8, 4),
) -> plt.Figure:
    _apply_rc()
    fig, ax = plt.subplots(figsize=figsize)

    M_best = np.array([h["riwayat_terbaik"] for h in hasil_runs])
    M_avg  = np.array([h["riwayat_rata"]    for h in hasil_runs])

    # Pastikan semua riwayat panjangnya sama (trim ke minimum)
    min_len = min(M_best.shape[1], M_avg.shape[1])
    M_best  = M_best[:, :min_len]
    M_avg   = M_avg[:, :min_len]
    x = np.arange(min_len)

    mean_best = M_best.mean(axis=0)
    std_best  = M_best.std(axis=0)
    mean_avg  = M_avg.mean(axis=0)

    ax.plot(x, mean_best, color=_C_BEST, linewidth=2.5,
            label="Fitness terbaik (rata-rata 10 run)")
    ax.fill_between(
        x,
        np.maximum(0, mean_best - std_best),
        np.minimum(1, mean_best + std_best),
        color=_C_BAND, alpha=0.14, label="±1 simpangan baku",
    )
    ax.plot(x, mean_avg, color=_C_MEAN, linewidth=2.0, linestyle=(0, (4, 3)),
            alpha=0.8, label="Fitness rata-rata populasi")

    ax.set_title("Konvergensi Rata-Rata 10 Run (±1 Simpangan Baku)",
                 fontsize=12, color="#5E6A70", pad=10)
    ax.set_xlabel("Generasi", color="#5E6A70")
    ax.set_ylabel("Fitness", color="#5E6A70")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right")

    fig.tight_layout()
    return fig


# (c) Perbandingan 4 kombinasi operator

def plot_perbandingan_operator(
    hasil_kombinasi: Dict[Tuple[str, str], List[Dict[str, Any]]],
    max_gen: int = 120,
    figsize: Tuple[float, float] = (9, 4.2),
) -> plt.Figure:
    _apply_rc()
    fig, ax = plt.subplots(figsize=figsize)

    PALETTE = ["#0F5F7F", "#2E9E6B", "#E08A3C", "#D9648F"]

    for (seleksi, crossover), lst in hasil_kombinasi.items():
        rata = np.mean([h["riwayat_terbaik"] for h in lst], axis=0)
        label = f"{seleksi} + {crossover}"
        ax.plot(rata[:max_gen], linewidth=1.8, label=label)

    ax.set_title(f"Perbandingan Operator (Fitness Rata-Rata, {max_gen} Generasi Pertama)",
                 fontsize=12, color="#5E6A70", pad=10)
    ax.set_xlabel("Generasi", color="#5E6A70")
    ax.set_ylabel("Fitness terbaik (rata-rata 10 run)", color="#5E6A70")
    ax.set_xlim(0, max_gen)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="lower right", fontsize=9)

    fig.tight_layout()
    return fig


# Konversi Figure -> bytes PNG

def fig_to_png_bytes(fig: plt.Figure, dpi: int = 150) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    buf.seek(0)
    return buf.getvalue()


def fig_konvergensi_gabungan(
    hasil_run_tunggal: Dict[str, Any],
    hasil_runs: Optional[List[Dict[str, Any]]] = None,
    figsize: Tuple[float, float] = (12, 4.3),
) -> plt.Figure:

    _apply_rc()

    if hasil_runs and len(hasil_runs) > 1:
        fig, axs = plt.subplots(1, 2, figsize=figsize)
        _plot_tunggal_ke_ax(axs[0], hasil_run_tunggal)
        _plot_10run_ke_ax(axs[1], hasil_runs)
    else:
        fig, ax = plt.subplots(figsize=(figsize[0] / 2, figsize[1]))
        _plot_tunggal_ke_ax(ax, hasil_run_tunggal)

    fig.tight_layout()
    return fig


def _plot_tunggal_ke_ax(ax: plt.Axes, hasil: Dict[str, Any]) -> None:
    riwayat_terbaik = hasil["riwayat_terbaik"]
    riwayat_rata    = hasil["riwayat_rata"]
    gen_valid       = hasil.get("gen_valid")
    seed            = hasil.get("seed", "?")

    x = range(len(riwayat_terbaik))
    ax.plot(x, riwayat_terbaik, color=_C_BEST, linewidth=2.5, label="Fitness terbaik")
    ax.plot(x, riwayat_rata,    color=_C_MEAN, linewidth=2.0,
            linestyle=(0, (4, 3)), alpha=0.8, label="Fitness rata-rata")
    if gen_valid is not None:
        ax.axvline(gen_valid, color=_C_VALID, linestyle="--", linewidth=1.5,
                   label=f"Valid gen {gen_valid}")
    ax.set_title(f"Run Terbaik (seed {seed})", fontsize=11, color="#5E6A70")
    ax.set_xlabel("Generasi"); ax.set_ylabel("Fitness")
    ax.set_ylim(0, 1.05); ax.legend(fontsize=8, loc="lower right")


def _plot_10run_ke_ax(ax: plt.Axes, hasil_runs: List[Dict[str, Any]]) -> None:
    M = np.array([h["riwayat_terbaik"] for h in hasil_runs])
    x = np.arange(M.shape[1])
    ax.plot(x, M.mean(0), color=_C_BEST, linewidth=2.5, label="Rata-rata terbaik")
    ax.fill_between(x, np.maximum(0, M.mean(0)-M.std(0)),
                    np.minimum(1, M.mean(0)+M.std(0)), color=_C_BAND, alpha=0.14,
                    label="±1 simpangan baku")
    ax.set_title("Rata-Rata 10 Run (±1 Std)", fontsize=11, color="#5E6A70")
    ax.set_xlabel("Generasi"); ax.set_ylabel("Fitness")
    ax.set_ylim(0, 1.05); ax.legend(fontsize=8, loc="lower right")
