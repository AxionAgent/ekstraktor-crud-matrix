# Ekstraktor CRUD Matrix

Tugas ETS Praktik **Programming Language Pragmatics**, D4 Teknik Informatika Polban kelas 2B.

**Kelompok:** Ghaisan Khoirul Badruzaman dan Hafiz Fauzan Syafrudin

Tool ini membaca file SQL dan menghasilkan **CRUD matrix**: tabel mana yang dibuat (C), dibaca (R),
diubah (U), dan dihapus (D) oleh setiap file. Codebase awalnya dari dosen, sengaja belum lengkap
(3 TODO) dan berisi beberapa bug. Tugas kami: melengkapi, mencari dan memperbaiki bug, membuktikan
perbaikan dengan test, dan menjelaskan akar masalahnya memakai konsep dari buku
*Crafting Interpreters* (Robert Nystrom).

Acuan kebenaran: [`SPESIFIKASI.md`](SPESIFIKASI.md). Kalau kode, komentar, dan spesifikasi berbeda,
yang benar adalah spesifikasi.

```text
 file .sql
    |
    v
 [ lexer ]      teks -> daftar token            crud/lexer.py      Bab 4    BAGIAN GHAISAN
    |
    v
 [ parser ]     token -> pohon AST              crud/parser.py     Bab 5,6  BAGIAN GHAISAN
    |
    v
 [ resolver ]   alias dan kolom -> nama tabel   crud/resolver.py   Bab 11   BAGIAN HAFIZ
    |
    v
 [ analyzer ]   AST -> {tabel: C/R/U/D}         crud/analyzer.py            BAGIAN HAFIZ
    |
    v
 CRUD matrix (crud_matrix.csv, --detail, --kolom)
```

## Cara menjalankan

Butuh Python 3.10 atau lebih baru.

```bash
python -m pip install pytest
python -m pytest                                   # semua test
python -m crud.cli data/sample/*.sql --detail detail.csv --kolom kolom.csv
python -m crud.cli data/sample/audit.sql --ast     # cetak AST hasil parsing dan resolusi
python evaluate.py                                 # bandingkan parser vs regex
```

## Status pengerjaan

| Bagian | Isi | Status |
| --- | --- | --- |
| Ghaisan | lexer dan parser: T1, T3, bug A1 sampai A6, test, laporan | **selesai** |
| Hafiz | resolver dan analyzer: T2, bug B1 dan seterusnya, ground truth, laporan akhir | belum mulai, menunggu giliran |

Hasil `pytest` setelah bagian Ghaisan: **40 lulus, 2 gagal**. Dua test yang masih gagal memang milik
bagian Hafiz (`test_kolom_tanpa_qualifier_satu_tabel` butuh T2, `test_matrix_laporan_penjualan`
butuh perbaikan bug B3).

Pembagian lengkap, alasan 50/50, aturan kerja, dan prompt untuk AI agent ada di
[`docs/PEMBAGIAN_TUGAS.pdf`](docs/PEMBAGIAN_TUGAS.pdf).

---

## Bagian Ghaisan: lexer dan parser (Bab 4, 5, 6)

File yang dipegang: `crud/lexer.py`, `crud/parser.py`.
Satu bug atau TODO = satu commit, jadi tiap baris di bawah bisa dibuka diff-nya saat demo.

| Kode | Masalah | Fungsi | Test di `tests/test_tambahan.py` | Commit |
| --- | --- | --- | --- | --- |
| A1 | Keyword huruf kecil (`select`) dibaca IDENT | `Lexer._word` | `test_bug_a1_keyword_tidak_peka_huruf_besar_kecil` | `209f669` |
| A2 | `<>` dipecah jadi `<` dan `>` (maximal munch) | `Lexer._scan_token` | `test_bug_a2_operator_tidak_sama_dengan_satu_token` | `40ca17f` |
| A3 | `'O''Brien'` dibaca dua string | `Lexer._string` | `test_bug_a3_dua_kutip_dalam_string_jadi_satu_kutip` | `13fac6a` |
| T3 | TODO: komentar blok `/* ... */` | `Lexer._scan_token` | `test_todo_t3_...` (2 test) | `5968b3f` |
| A4 | `AND` dan `OR` setingkat, harusnya `AND` lebih kuat | `_or_expr`, `_and_expr` | `test_bug_a4_and_lebih_kuat_daripada_or` | `0c8c2d0` |
| A5 | Error recovery membuang token sampai akhir file, bukan sampai `;` | `Parser._synchronize` | `test_bug_a5_error_recovery_berhenti_di_titik_koma` | `658568e` |
| A6 | `LEFT OUTER JOIN` ditolak | `Parser._join` | `test_bug_a6_left_outer_join_diterima` | `b5f14f0` |
| T1 | TODO: `INSERT INTO ... SELECT` | `Parser._insert` | `test_todo_t1_...` (2 test) | `59cb894` |

Test kasus tepi bagian Ghaisan (2 dari 5): `test_tepi_komentar_blok_tidak_bersarang`,
`test_tepi_and_milik_between_tidak_tertukar_dengan_and_logika`.

Laporan bagian Ghaisan:

- [`docs/LAPORAN_BUG.md`](docs/LAPORAN_BUG.md) bug A1 sampai A6 (gejala, reproduksi, akar masalah, perbaikan)
- [`docs/KARTU_DESAIN.md`](docs/KARTU_DESAIN.md) kartu 1 sampai 3
- [`docs/LOG_AI.md`](docs/LOG_AI.md) baris 1 sampai 6
- [`docs/LAPORAN_AKHIR.md`](docs/LAPORAN_AKHIR.md) bagian 4 (pembagian kerja)

Efek ke data contoh: `evaluate.py` recall parser naik dari **0.10** (kode asli) ke **0.90**.
Sisa selisihnya (`pesanan` di UPDATE baris 12 terbaca U, harusnya R) adalah bug B3 milik bagian Hafiz.

---

## Bagian Hafiz: resolver, analyzer, dan data (Bab 11)

File yang dipegang: `crud/resolver.py`, `crud/analyzer.py`, `crud/pipeline.py`, `crud/cli.py`,
`data/ground_truth.csv`.

Temuan awal yang sudah dibuktikan bug-nya (detail dan cara reproduksinya ada di PDF pembagian tugas
bagian 5):

| Kode | Masalah | Fungsi | Status |
| --- | --- | --- | --- |
| T2 | TODO: kolom tanpa qualifier (SPESIFIKASI 4.3) | `Resolver._column` | belum |
| B1 | Qualifier dicari dari scope **terluar** dulu, harusnya terdalam (shadowing salah) | `Resolver._lookup` | belum |
| B2 | Scope `DELETE` tidak ditutup, alias bocor ke statement berikutnya (SPESIFIKASI 4.5) | `Resolver._delete` | belum |
| B3 | Tabel di subquery dalam `UPDATE` ditandai U, harusnya R (SPESIFIKASI 5) | `analyze_statement` | belum |
| B4+ | Bug lain yang mungkin masih ada di file bagian Hafiz | | dicari |

Pekerjaan lain bagian Hafiz:

- label manual `audit.sql` dan `pemeliharaan.sql` di `data/ground_truth.csv`, **bukan** salinan output tool
- `docs/LAPORAN_AKHIR.md` bagian 1 sampai 3 (hasil `evaluate.py`, 3 kasus regex salah, 3 batas pendekatan)
- `docs/LAPORAN_BUG.md` bug B, `docs/KARTU_DESAIN.md` kartu 4 dan 5, `docs/LOG_AI.md` mulai baris 7
- `tests/test_tambahan.py` blok BAGIAN HAFIZ: test regresi bug B dan 3 test kasus tepi

---

## Aturan kerja (berlaku juga untuk AI agent)

1. Kerjakan hanya file milik bagianmu. Kalau menemukan bug di file milik partner, kabari dulu, jangan langsung diubah.
2. Jangan ubah `tests/test_*.py` bawaan dosen, `baseline/regex_extractor.py`, `SPESIFIKASI.md`, dan API publik (SPESIFIKASI bagian 7).
3. Satu bug atau TODO = satu commit, pesan commit diawali kodenya (`Bug B1: ...`, `TODO T2: ...`).
4. Test regresi ditulis dulu dan harus **gagal** sebelum perbaikan, lalu lulus sesudahnya.
5. Kode dan komentar sesederhana mungkin, gaya komentar mengikuti contoh di deskripsi tugas.
6. `data/ground_truth.csv` diisi manual berdasarkan spesifikasi, tidak boleh diisi AI dari output tool.
7. Setiap pemakaian AI dicatat di `docs/LOG_AI.md`.
8. Jalankan `python -m pytest` sebelum push.

## Struktur repo

| Path | Isi |
| --- | --- |
| `SPESIFIKASI.md` | Acuan kebenaran: aturan lexer, grammar, resolver, CRUD |
| `crud/lexer.py` | Lexer |
| `crud/ast_nodes.py` | Node AST, `iter_nodes`, `pretty` |
| `crud/parser.py` | Parser recursive descent |
| `crud/resolver.py` | Resolver scope dan alias |
| `crud/analyzer.py` | Aturan CRUD dan penggunaan kolom |
| `crud/pipeline.py`, `crud/cli.py` | Perangkai pipeline dan antarmuka baris perintah |
| `baseline/regex_extractor.py` | Pembanding berbasis regex (sengaja naif, tidak diubah) |
| `evaluate.py` | Precision dan recall parser vs regex |
| `data/sample/*.sql` | Data uji |
| `data/ground_truth.csv` | Label benar |
| `tests/` | Test bawaan dosen dan `test_tambahan.py` buatan kelompok |
| `docs/` | Laporan bug, kartu desain, laporan akhir, log AI, pembagian tugas |

## Atribusi

Struktur pipeline dan beberapa teknik diadaptasi dari *Crafting Interpreters* karya Robert Nystrom
(https://craftinginterpreters.com):

- scanner per karakter dengan `peek`/`match` dan maximal munch: Bab 4 *Scanning*
- komentar blok: challenge 4 di akhir Bab 4 (versi tanpa nesting)
- grammar bertingkat untuk presedensi dan parser recursive descent: Bab 5 dan 6
- `_or_expr` dan `_and_expr`: aturan `logic_or` dan `logic_and` di Bab 9.3 *Logical Operators*
- panic mode dan `_synchronize`: Bab 6.3 *Syntax Errors*
- resolver sebagai pass terpisah dengan rantai scope: Bab 11 *Resolving and Binding*

Codebase awal (`crud-extractor`) dan `SPESIFIKASI.md` berasal dari dosen pengampu praktikum.
