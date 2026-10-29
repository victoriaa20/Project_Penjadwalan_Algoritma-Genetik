import pytest

from ag.data import buat_data_default
from ag.fitness import hitung_fitness, hitung_pelanggaran, total_pelanggaran, hitung_soft


@pytest.fixture(scope="module")
def data():
    return buat_data_default()


@pytest.fixture(scope="module")
def k_valid(data):
    return [(i, 0) for i in range(data.n_gen)]

# (a) Jadwal sengaja bentrok
def test_a_jadwal_bentrok(data):
    k_bentrok = [(0, 0)] * data.n_gen
    assert total_pelanggaran(k_bentrok, data) > 0
    assert hitung_fitness(k_bentrok, data) < 1.0

# (b) Jadwal valid buatan sendiri
def test_b_jadwal_valid(data, k_valid):
    assert total_pelanggaran(k_valid, data) == 0
    assert hitung_fitness(k_valid, data) == 1.0

# (c) Bentrok dosen & kelas
def test_c_bentrok_dosen_kelas(data, k_valid):
    k = list(k_valid)
    k[0] = (22, 0)   
    k[1] = (22, 1)   
    p = hitung_pelanggaran(k, data)
    assert p["H1_dosen"] == 1, f"Harap H1_dosen=1, dapat {p['H1_dosen']}"
    assert p["H2_ruang"] == 0, f"Harap H2_ruang=0, dapat {p['H2_ruang']}"
    assert p["H3_kelas"] == 1, f"Harap H3_kelas=1, dapat {p['H3_kelas']}"

# (d) Bentrok ruang saja
def test_d_bentrok_ruang(data, k_valid):
    k = list(k_valid)
    k[0] = (24, 0)  
    k[6] = (24, 0)  
    p = hitung_pelanggaran(k, data)
    assert p["H2_ruang"] == 1, f"Harap H2_ruang=1, dapat {p['H2_ruang']}"
    assert p["H1_dosen"] == 0, f"Harap H1_dosen=0, dapat {p['H1_dosen']}"
    assert p["H3_kelas"] == 0, f"Harap H3_kelas=0, dapat {p['H3_kelas']}"

# (e) Pelanggaran kapasitas
def test_e_pelanggaran_kapasitas(data, k_valid):
    k = list(k_valid)
    k[0] = (0, 4)   
    p = hitung_pelanggaran(k, data)
    assert p["H4_kapasitas"] == 1, f"Harap H4_kapasitas=1, dapat {p['H4_kapasitas']}"

def test_hitung_soft_tidak_error(data, k_valid):
    soft = hitung_soft(k_valid, data)
    assert "S1_preferensi_dosen" in soft
    assert "S2_jeda_panjang" in soft
    assert isinstance(soft["S1_preferensi_dosen"], int)
    assert isinstance(soft["S2_jeda_panjang"], int)


def test_fitness_range(data):
    k_acak = [(0, 0)] * data.n_gen
    f = hitung_fitness(k_acak, data)
    assert 0 < f <= 1.0
