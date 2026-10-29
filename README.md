# JadwalGA

Aplikasi penjadwalan kuliah menggunakan algoritma genetika, dibuat dengan Streamlit. Algoritma genetikanya ditulis sendiri tanpa library seperti DEAP atau PyGAD.

## Fitur

- Menjalankan algoritma genetika dengan parameter yang bisa diatur
- Pengujian 10 run dengan seed berbeda, beserta perbandingan kombinasi operator
- Tampilan jadwal terbaik dalam bentuk tabel hari x slot
- Ekspor hasil ke CSV, Excel, dan grafik konvergensi (PNG)

## Persyaratan

- Python 3.10 atau lebih baru

## Instalasi

```bash
git clone <URL_REPOSITORI>
cd Project_Penjadwalan_Algoritma-Genetik

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Menjalankan

```bash
streamlit run app.py
```

Lalu buka http://localhost:8501 di browser.

## Testing

```bash
pytest tests/ -v
```

## Cara Kerja Singkat

Satu kromosom mewakili satu jadwal lengkap. Isinya 20 gen, satu gen untuk setiap sesi kuliah, berupa pasangan (timeslot, ruang). Timeslot bernilai 0 sampai 24 (5 hari x 5 slot per hari), ruang bernilai 0 sampai 4.

Fitness dihitung dengan:

```
fitness = 1 / (1 + jumlah_pelanggaran_keras)
```

Fitness 1.0 berarti jadwal tidak punya pelanggaran sama sekali.

Kendala yang diperiksa:

- H1: dosen tidak boleh mengajar dua sesi di waktu yang sama
- H2: satu ruang tidak boleh dipakai dua sesi di waktu yang sama
- H3: satu kelas tidak boleh punya dua sesi di waktu yang sama
- H4: kapasitas ruang harus cukup untuk jumlah mahasiswa
- S1 dan S2 (preferensi waktu dosen dan jeda antar sesi) hanya dihitung sebagai informasi, tidak masuk fitness

## Parameter Default

- Populasi: 100
- Generasi: 300
- Peluang crossover: 0.8
- Peluang mutasi: 0.05 per gen
- Seleksi: turnamen (k=3) atau roulette wheel
- Crossover: uniform atau satu titik
- Elitisme: 2

Setiap run memakai `random.Random(seed)` sendiri, jadi seed yang sama selalu menghasilkan hasil yang sama. Seed untuk pengujian 10 run adalah 11, 22, 33, ..., 110.

## Data

Data default berisi 20 sesi kuliah, 8 dosen, 5 ruang, 6 kelas, dan 25 timeslot. Data bisa dilihat di halaman Data Master atau diubah di `ag/data.py`.

## Struktur Folder

```
penjadwalan-ag/
├── app.py          # entry point
├── ag/             # logika algoritma genetika
├── ui/             # komponen Streamlit
├── pages/          # halaman aplikasi
├── assets/         # CSS
└── tests/          # unit test
```