import streamlit as st

from ui.komponen import inject_css, page_header
from ui.state import init_session_state

inject_css()
init_session_state()

page_header("❓ Bantuan & Tentang AG", "Panduan konsep Algoritma Genetika untuk membantu tanya jawab individu.")

# Tabs utama
tab_ag, tab_kromosom, tab_fitness, tab_operator = st.tabs([
    "🧬 Tentang AG",
    "🔗 Kromosom",
    "🎯 Fitness",
    "⚙️ Operator",
])


# Tab 1 — Tentang AG
with tab_ag:
    st.markdown("""
    <div class="jadwalga-card" style="padding:28px;">
      <h3 style="font-size:20px; font-weight:500; margin-bottom:12px;">Apa itu Algoritma Genetika?</h3>
      <p style="font-size:14px; color:var(--text-secondary); line-height:1.7;">
        Algoritma Genetika (AG) adalah metaheuristik pencarian berbasis populasi yang terinspirasi dari
        proses evolusi biologis (Darwin). AG bekerja dengan mempertahankan sekumpulan solusi kandidat
        (populasi) dan secara iteratif menghasilkan generasi baru yang lebih baik melalui tiga operator:
        seleksi, crossover, dan mutasi.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    cols = st.columns(3)
    konsep = [
        ("🧬", "Populasi", "Sekumpulan N kromosom (solusi kandidat). Semakin besar populasi, semakin luas ruang pencarian yang dieksplorasi, tetapi semakin lambat setiap generasi."),
        ("🔄", "Evolusi", "Setiap generasi, kromosom terbaik dipertahankan (elitisme), lalu kromosom baru dihasilkan melalui seleksi orang tua, crossover, dan mutasi."),
        ("✅", "Konvergensi", "AG dianggap berhasil jika menemukan kromosom dengan fitness = 1.0 (tidak ada pelanggaran kendala keras). Grafik konvergensi menunjukkan laju peningkatan fitness per generasi."),
    ]
    for (ikon, judul, isi), col in zip(konsep, cols):
        with col:
            st.markdown(f"""
            <div class="jadwalga-card" style="text-align:center; padding:24px;">
              <div style="font-size:36px; margin-bottom:12px;">{ikon}</div>
              <div class="jadwalga-card-title" style="margin-bottom:8px;">{judul}</div>
              <p style="font-size:13px; color:var(--text-secondary); line-height:1.6;">{isi}</p>
            </div>
            """, unsafe_allow_html=True)

# Tab 2 — Kromosom
with tab_kromosom:
    st.markdown("""
    <div class="jadwalga-card" style="padding:28px;">
      <h3 style="font-size:18px; font-weight:500; margin-bottom:16px;">Representasi Kromosom</h3>
      <p style="font-size:14px; color:var(--text-secondary); line-height:1.7; margin-bottom:16px;">
        Satu kromosom = jadwal lengkap untuk seluruh 20 sesi kuliah.
        Kromosom direpresentasikan sebagai <strong>list panjang 20</strong>, di mana tiap elemen (gen ke-<em>i</em>)
        mewakili penugasan sesi kuliah ke-<em>i</em>.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="jadwalga-card" style="padding:20px;">
          <div class="jadwalga-card-title">📐 Struktur Gen</div>
          <br>
          <code style="font-size:14px; background:rgba(15,95,127,0.08); padding:8px 12px; border-radius:8px; display:block;">
            kromosom[i] = (timeslot, indeks_ruang)
          </code>
          <br>
          <table style="width:100%; font-size:13px; border-collapse:collapse;">
            <tr style="border-bottom:1px solid var(--divider);">
              <td style="padding:8px 0; color:var(--text-secondary);">timeslot</td>
              <td style="padding:8px 0;"><strong>Integer [0, 24]</strong><br>
                <span style="color:var(--text-muted); font-size:12px;">Hari = t // 5, Slot = t % 5</span>
              </td>
            </tr>
            <tr style="border-bottom:1px solid var(--divider);">
              <td style="padding:8px 0; color:var(--text-secondary);">indeks_ruang</td>
              <td style="padding:8px 0;"><strong>Integer [0, 4]</strong><br>
                <span style="color:var(--text-muted); font-size:12px;">0=GKTA-LT4, 1=GKTA-LT5, 2=FT4, 3=FT5, 4=FT6</span>
              </td>
            </tr>
            <tr>
              <td style="padding:8px 0; color:var(--text-secondary);">panjang</td>
              <td style="padding:8px 0;"><strong>20 gen</strong> (1 gen = 1 sesi kuliah)</td>
            </tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="jadwalga-card" style="padding:20px;">
          <div class="jadwalga-card-title">🗺️ Peta Timeslot</div>
          <br>
          <table style="width:100%; font-size:12px; border-collapse:collapse; text-align:center;">
            <tr style="background:var(--primary); color:#fff; border-radius:8px;">
              <th style="padding:6px;">t</th>
              <th style="padding:6px;">Hari</th>
              <th style="padding:6px;">Slot</th>
            </tr>
            <tr style="border-bottom:1px solid var(--divider);">
              <td style="padding:6px;">0</td><td>Senin</td><td>07.00–09.30</td>
            </tr>
            <tr style="border-bottom:1px solid var(--divider);">
              <td style="padding:6px;">1</td><td>Senin</td><td>09.30–12.00</td>
            </tr>
            <tr style="border-bottom:1px solid var(--divider);">
              <td style="padding:6px;">4</td><td>Senin</td><td>17.00–19.30</td>
            </tr>
            <tr style="border-bottom:1px solid var(--divider);">
              <td style="padding:6px;">5</td><td>Selasa</td><td>07.00–09.30</td>
            </tr>
            <tr>
              <td style="padding:6px;">24</td><td>Jumat</td><td>17.00–19.30</td>
            </tr>
          </table>
          <p style="font-size:11px; color:var(--text-muted); margin-top:8px;">
            Total: 5 hari × 5 slot = 25 timeslot (indeks 0–24)
          </p>
        </div>
        """, unsafe_allow_html=True)

# Tab 3 — Fitness
with tab_fitness:
    st.markdown("""
    <div class="jadwalga-card" style="padding:28px;">
      <h3 style="font-size:18px; font-weight:500; margin-bottom:16px;">Fungsi Fitness Berbasis Penalti</h3>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Formula
    st.latex(r"\text{fitness}(k) = \frac{1}{1 + \text{total\_pelanggaran\_keras}(k)}")

    st.markdown("""
    <div class="jadwalga-card" style="padding:20px; margin-top:16px;">
      <div class="jadwalga-card-title">Nilai Fitness</div>
      <ul style="font-size:14px; color:var(--text-secondary); line-height:2; margin-top:8px; padding-left:20px;">
        <li><strong>fitness = 1.0</strong> → Jadwal sempurna, tidak ada pelanggaran keras (H1–H4)</li>
        <li><strong>fitness &lt; 1.0</strong> → Ada pelanggaran; semakin kecil, semakin banyak bentrok</li>
        <li>Rentang: <strong>(0, 1]</strong> — selalu positif</li>
      </ul>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_h, col_s = st.columns(2)
    with col_h:
        st.markdown("""
        <div class="jadwalga-card" style="padding:20px;">
          <div class="jadwalga-card-title" style="color:var(--negative);">⛔ Kendala Keras (H1–H4)</div>
          <p style="font-size:12px; color:var(--text-muted); margin:4px 0 12px;">Masuk ke fungsi fitness — harus = 0</p>
          <table style="width:100%; font-size:13px; border-collapse:collapse;">
            <tr style="border-bottom:1px solid var(--divider);">
              <td style="padding:8px 0; font-weight:500; color:var(--primary); width:40px;">H1</td>
              <td style="padding:8px 0;">Dosen tidak mengajar di 2 tempat pada slot yang sama</td>
            </tr>
            <tr style="border-bottom:1px solid var(--divider);">
              <td style="padding:8px 0; font-weight:500; color:var(--primary);">H2</td>
              <td style="padding:8px 0;">Ruang tidak dipakai 2 kelas sekaligus</td>
            </tr>
            <tr style="border-bottom:1px solid var(--divider);">
              <td style="padding:8px 0; font-weight:500; color:var(--primary);">H3</td>
              <td style="padding:8px 0;">Kelas mahasiswa tidak bentrok pada slot yang sama</td>
            </tr>
            <tr>
              <td style="padding:8px 0; font-weight:500; color:var(--primary);">H4</td>
              <td style="padding:8px 0;">Kapasitas ruang ≥ jumlah mahasiswa kelas</td>
            </tr>
          </table>
        </div>
        """, unsafe_allow_html=True)

    with col_s:
        st.markdown("""
        <div class="jadwalga-card" style="padding:20px;">
          <div class="jadwalga-card-title" style="color:var(--warning);">⚠️ Kendala Lunak (S1–S2)</div>
          <p style="font-size:12px; color:var(--text-muted); margin:4px 0 12px;">Informatif saja — tidak masuk fitness</p>
          <table style="width:100%; font-size:13px; border-collapse:collapse;">
            <tr style="border-bottom:1px solid var(--divider);">
              <td style="padding:8px 0; font-weight:500; color:var(--warning); width:40px;">S1</td>
              <td style="padding:8px 0;">Sesi di luar slot preferensi dosen (mis. dosen lebih suka mengajar pagi)</td>
            </tr>
            <tr>
              <td style="padding:8px 0; font-weight:500; color:var(--warning);">S2</td>
              <td style="padding:8px 0;">Jeda panjang antar sesi kelas dalam satu hari (mahasiswa menunggu terlalu lama)</td>
            </tr>
          </table>
          <p style="font-size:12px; color:var(--text-muted); margin-top:12px;">
            S1 dan S2 digunakan untuk memilih run terbaik di antara run-run yang sama-sama fitness = 1.0.
          </p>
        </div>
        """, unsafe_allow_html=True)

# Tab 4 — Operator
with tab_operator:
    st.markdown("""
    <div class="jadwalga-card" style="padding:28px;">
      <h3 style="font-size:18px; font-weight:500; margin-bottom:8px;">Operator Algoritma Genetika</h3>
      <p style="font-size:14px; color:var(--text-secondary);">
        Semua operator ditulis dari awal tanpa library AG eksternal.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    ops = [
        ("🌱", "Inisialisasi", "buat_populasi()",
         "Setiap gen diisi secara acak seragam: timeslot ∈ [0,24] dan ruang ∈ [0,4]. "
         "Menggunakan instance random.Random(seed) agar deterministik."),
        ("🏆", "Seleksi Turnamen", "seleksi_turnamen(k=3)",
         "Dari populasi, dipilih k=3 individu secara acak. Yang memiliki fitness tertinggi "
         "menjadi orang tua. Cocok untuk ruang pencarian kompleks karena tidak bergantung pada "
         "skala fitness absolut."),
        ("🎡", "Seleksi Roulette", "seleksi_roulette()",
         "Probabilitas terpilih sebanding dengan fitness relatif (fitness/total_fitness). "
         "Rentan terhadap premature convergence bila ada individu dengan fitness jauh lebih tinggi."),
        ("✂️", "Crossover Uniform", "crossover_uniform(p=0.5/gen)",
         "Setiap gen dari anak dipilih secara acak dari salah satu orang tua dengan p=50%. "
         "Menghasilkan variasi lebih tinggi. Direkomendasikan untuk masalah dengan banyak variabel."),
        ("✂️", "Crossover 1 Titik", "crossover_satu_titik()",
         "Titik potong dipilih acak. Gen sebelum titik dari orang tua A, setelahnya dari B. "
         "Cocok saat sesi-sesi yang berurutan saling berkaitan (karena mempertahankan blok gen)."),
        ("🔀", "Mutasi Acak", "mutasi(pm=0.05/gen)",
         "Setiap gen dimutasi dengan probabilitas pm=5%. Jenis mutasi dipilih acak: "
         "ubah waktu saja, ubah ruang saja, atau ubah keduanya. "
         "Mencegah populasi terjebak di optima lokal."),
        ("👑", "Elitisme", "n_elit=2",
         "n_elit individu terbaik dari generasi t langsung disalin ke generasi t+1 "
         "tanpa melalui crossover/mutasi. Memastikan fitness terbaik tidak menurun."),
    ]

    for i in range(0, len(ops), 2):
        col_a, col_b = st.columns(2)
        for col, item in zip([col_a, col_b], ops[i:i+2]):
            ikon, nama, kode, penjelasan = item
            with col:
                st.markdown(f"""
                <div class="jadwalga-card" style="padding:20px; margin-bottom:16px;">
                  <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                    <span style="font-size:24px;">{ikon}</span>
                    <div>
                      <div class="jadwalga-card-title">{nama}</div>
                      <code style="font-size:11px; color:var(--primary);">{kode}</code>
                    </div>
                  </div>
                  <p style="font-size:13px; color:var(--text-secondary); line-height:1.6;">{penjelasan}</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="jadwalga-card" style="padding:20px; background:rgba(15,95,127,0.06);">
      <div class="jadwalga-card-title">🔄 Siklus Evolusi Lengkap</div>
      <div style="display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-top:12px; font-size:13px; color:var(--text-secondary);">
        <span style="background:var(--primary);color:#fff;padding:4px 12px;border-radius:999px;">Inisialisasi</span> →
        <span style="background:var(--bg-card-solid);padding:4px 12px;border-radius:999px;border:1px solid var(--divider);">Evaluasi Fitness</span> →
        <span style="background:var(--bg-card-solid);padding:4px 12px;border-radius:999px;border:1px solid var(--divider);">Elitisme</span> →
        <span style="background:var(--bg-card-solid);padding:4px 12px;border-radius:999px;border:1px solid var(--divider);">Seleksi Orang Tua</span> →
        <span style="background:var(--bg-card-solid);padding:4px 12px;border-radius:999px;border:1px solid var(--divider);">Crossover</span> →
        <span style="background:var(--bg-card-solid);padding:4px 12px;border-radius:999px;border:1px solid var(--divider);">Mutasi</span> →
        <span style="background:var(--positive);color:#fff;padding:4px 12px;border-radius:999px;">Generasi Baru</span>
        <span style="color:var(--text-muted); font-size:12px;">← diulang hingga n_generasi atau solusi valid</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
