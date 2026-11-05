# Laporan Akhir

## 1. Hasil evaluasi

Tempel keluaran `python evaluate.py` setelah `data/ground_truth.csv` dilengkapi.

```text

```

## 2. Tiga kasus di mana regex salah

Untuk tiap kasus: SQL-nya, kesalahan regex, dan mengapa parser benar (kaitkan dengan konsep
lexing, parsing, atau resolusi).

1.
2.
3.

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1.
2.
3.

## 4. Pembagian kerja

Siapa mengerjakan apa, dan bagaimana kalian memastikan keduanya memahami seluruh kode.

Rincian lengkapnya ada di `docs/PEMBAGIAN_TUGAS.pdf`. Pembagiannya mengikuti urutan pipeline,
supaya tiap orang memegang file sendiri dan tidak saling menimpa pekerjaan.

| | Ghaisan | Hafiz |
| --- | --- | --- |
| Tahap pipeline | lexer, parser (Bab 4, 5, 6) | resolver, analyzer (Bab 11) |
| File utama | `crud/lexer.py`, `crud/parser.py` | `crud/resolver.py`, `crud/analyzer.py` |
| TODO | T3 komentar blok, T1 `INSERT ... SELECT` | T2 kolom tanpa qualifier |
| Bug | A1 sampai A6 | B1 dan seterusnya |
| Test tambahan | 6 regresi, 3 test TODO, 2 kasus tepi | regresi bug B, 3 kasus tepi |
| Kartu desain | no. 1 sampai 3 | no. 4 dan 5 |
| Data dan laporan | LAPORAN_BUG bagian A | ground truth `audit.sql` dan `pemeliharaan.sql`, LAPORAN_AKHIR bagian 1 sampai 3 |

Urutan kerjanya: bagian Ghaisan dikerjakan dan di-push lebih dulu, karena resolver dan analyzer
butuh lexer dan parser yang sudah benar. Setelah itu Hafiz mengerjakan bagiannya di atas commit
terakhir Ghaisan.

Cara memastikan keduanya memahami seluruh kode:

1. Setiap bug dan TODO dikerjakan dalam satu commit sendiri, jadi `git log` bisa dipakai sebagai
   daftar materi demo. Masing-masing membaca diff milik partner, bukan cuma miliknya sendiri.
2. Masing-masing menjelaskan bagian partnernya secara lisan memakai `python -m crud.cli FILE --ast`,
   lalu partner mengoreksi.
3. Latihan prediksi output: satu orang menulis SQL baru, yang lain menebak token, pohon AST,
   hasil resolusi, dan CRUD matrix-nya sebelum dijalankan.
