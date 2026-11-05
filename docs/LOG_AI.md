# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

Alat yang dipakai bagian Ghaisan: Claude Code (coding agent). Bagian Hafiz menambahkan barisnya
sendiri di bawah, mulai nomor 7.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |
| 1 | Ghaisan | Membaca deskripsi tugas, SPESIFIKASI.md, dan seluruh kode, menjalankan test terlihat, lalu mendaftar setiap bagian yang melanggar spesifikasi. | Diterima sebagian. Hasilnya 3 TODO dan 9 dugaan bug (6 di lexer/parser, 3 di resolver/analyzer). Satu usulan ditolak: menganggap `:1` sebagai PARAM. | Semua dugaan yang diterima punya bagian spesifikasi yang jelas dilanggar. Usulan `:1` ditolak karena SPESIFIKASI 2.6 tidak memberi contoh parameter yang diawali angka, jadi perilaku kode lama (LexError) tidak terbukti salah. | Setiap dugaan direproduksi dengan potongan SQL kecil di kode asli sebelum diperbaiki. Hasilnya dicatat di bagian Gejala tiap bug di LAPORAN_BUG.md. |
| 2 | Ghaisan | Membuat dokumen pembagian tugas 50/50 (PDF) dan README yang memisahkan bagian Ghaisan dan Hafiz. | Diterima. | Pembagian mengikuti urutan pipeline supaya bagian Hafiz tidak bentrok dengan bagian Ghaisan. | Dicek terhadap tabel deliverable dan tabel penilaian di deskripsi tugas. |
| 3 | Ghaisan | Memperbaiki bug lexer A1, A2, A3 dan melengkapi TODO T3 (komentar blok), dengan komentar kode sederhana. | Diterima. | Perbaikan kecil dan lokal di satu fungsi masing-masing, sesuai SPESIFIKASI 2.2 sampai 2.5. | Tiap perbaikan satu commit. Test regresinya gagal di commit sebelumnya dan lulus sesudahnya, dan seluruh `pytest` dijalankan ulang tiap commit. |
| 4 | Ghaisan | Memperbaiki bug parser A4, A5, A6 dan melengkapi TODO T1 (`INSERT ... SELECT`). | Diterima. Untuk A5 ada alternatif sinkronisasi di keyword `SELECT` seperti Lox, ditolak (lihat KARTU_DESAIN no. 3). | Fungsi parser dibuat sama persis dengan aturan grammar bagian 3. | Test regresi sebelum/sesudah, `python -m crud.cli data/sample/*.sql --ast` dibaca untuk `audit.sql` dan `pemeliharaan.sql`, dan `python evaluate.py` (recall parser naik dari 0.10 ke 0.90 setelah bagian Ghaisan). |
| 5 | Ghaisan | Menulis test di `tests/test_tambahan.py` blok Ghaisan: 6 test regresi, 3 test TODO, 2 test kasus tepi. | Diterima. Satu angka kolom yang salah hitung di test T3 dibetulkan (17 jadi 18). | Test harus gagal sebelum perbaikan supaya benar-benar membuktikan bug. | Tiap test regresi dijalankan di kode sebelum perbaikan (gagal) dan sesudah perbaikan (lulus). Folder `tests/` asli tidak diubah. |
| 6 | Ghaisan | Menulis LAPORAN_BUG A1 sampai A6, KARTU_DESAIN no. 1 sampai 3, dan LAPORAN_AKHIR bagian 4. | Diterima. | Akar masalah dikaitkan ke subbab buku. | Nama subbab dicocokkan dengan daftar heading di source buku `craftinginterpreters/book/*.md` (scanning, representing-code, parsing-expressions, control-flow, resolving-and-binding). |

**Refleksi (3-5 kalimat).** Di bagian mana AI paling membantu? Di mana AI keliru atau
menyesatkan, dan bagaimana kalian mengetahuinya?

- **Ghaisan:** AI paling membantu saat mencocokkan kode dengan spesifikasi baris per baris, karena
  beberapa bug (presedensi AND/OR dan error recovery) tidak tertangkap test terlihat dan tidak mengubah
  hasil di semua file. AI juga sempat mengusulkan perubahan yang tidak didukung spesifikasi (parameter
  `:1`) dan salah menghitung kolom di satu test, keduanya ketahuan karena setiap klaim harus
  dibuktikan dengan menjalankan kode. Karena itu setiap perbaikan dibuat satu commit dengan test yang
  gagal dulu, supaya hasil AI bisa dicek satu per satu.
- **Hafiz:** (diisi Hafiz)
