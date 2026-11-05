# Laporan Bug

Salin blok di bawah untuk setiap bug. Bagian **Akar masalah** wajib ditulis dengan kata-kata
sendiri dan memakai konsep dari *Crafting Interpreters* (sebutkan bab). Bagian ini diuji lisan.

Laporan dibagi dua sesuai pembagian tugas (lihat `docs/PEMBAGIAN_TUGAS.pdf`):

| Kode | Bagian | Tahap pipeline | Bab buku |
| --- | --- | --- | --- |
| A1 sampai A6 | Ghaisan | lexer dan parser | Bab 4, 5, 6 |
| B1 dan seterusnya | Hafiz | resolver dan analyzer | Bab 11 |

Nomor subbab buku mengikuti edisi web *Crafting Interpreters* (Robert Nystrom):
Bab 4 Scanning, Bab 5 Representing Code, Bab 6 Parsing Expressions, Bab 9 Control Flow,
Bab 11 Resolving and Binding.

---

# BAGIAN GHAISAN: lexer dan parser

---

## Bug A1: keyword huruf kecil dibaca sebagai IDENT

**Ditemukan oleh:** Ghaisan (lewat Claude Code) · **Diperbaiki oleh:** Ghaisan (lewat Claude Code)

**Gejala.** `tokenize("select id from pelanggan")` menghasilkan `IDENT 'select'`, `IDENT 'id'`,
`IDENT 'from'`, padahal SPESIFIKASI 2.2 bilang keyword tidak peka huruf besar/kecil dan nilainya
dinormalisasi ke huruf besar (`KEYWORD 'SELECT'`). Akibatnya parser melapor
`Baris 1, kolom 1: diharapkan awal statement (SELECT, INSERT, UPDATE, DELETE), ditemukan 'select'`
dan statement itu tidak masuk CRUD matrix. Seluruh isi `pemeliharaan.sql` ditulis huruf kecil,
jadi file itu ikut kena. Test terlihat `test_keyword_huruf_kecil` juga gagal karena bug ini.

**Reproduksi minimal.**

```sql
select id from pelanggan
```

**Akar masalah.** Di Bab 4.7 (*Reserved Words and Identifiers*), scanner membaca satu lexeme
identifier secara utuh dulu (maximal munch), baru kemudian menentukan **jenis token**-nya dengan
mencari lexeme itu di tabel keyword. Jenis token (Bab 4.2.1, *Token type*) adalah hasil klasifikasi
lexeme. Di kode lama, pencarian di `KEYWORDS` memakai lexeme mentah (`text in KEYWORDS`), padahal isi
tabelnya huruf besar semua. Jadi klasifikasinya ikut bergantung pada huruf besar/kecil. Lox di buku
memang sengaja peka huruf, tetapi SQL di proyek ini tidak, sehingga lexeme harus dinormalisasi
**sebelum** dicocokkan ke tabel keyword. Karena lexer salah mengklasifikasi, parser menerima token
yang salah jenis, dan parser tidak mungkin memperbaikinya sendiri.

**Perbaikan.** `crud/lexer.py`, fungsi `Lexer._word`: lexeme diubah ke huruf besar
(`text.upper()`) lalu dicari di `KEYWORDS`. Kalau keyword, nilai token disimpan dalam huruf besar.
Kalau bukan, IDENT disimpan apa adanya (parser yang mengecilkan nama tabel dan kolom, sesuai 2.2).
Alternatif yang ditolak:
(1) menambah versi huruf kecil ke `KEYWORDS`, ditolak karena `KEYWORDS` termasuk API publik dan
kombinasi seperti `SeLeCt` tidak mungkin didaftar semua;
(2) membandingkan dengan `.upper()` di `_check_kw` parser, ditolak karena klasifikasi token tetap
salah di lexer (`from` huruf kecil bisa terbaca sebagai alias tabel) dan itu bukan tugas parser.

**Test regresi.** `test_bug_a1_keyword_tidak_peka_huruf_besar_kecil`

**Peran AI.** Bug ditemukan Claude Code saat membandingkan `_word` dengan SPESIFIKASI 2.2, lalu
dibuktikan dengan menjalankan reproduksi di atas pada kode asli. Perbaikan ditulis agent. Verifikasi:
test regresi gagal di commit kode asli dan lulus sesudah commit `Bug A1`.

---

## Bug A2: operator `<>` dipecah jadi dua token

**Ditemukan oleh:** Ghaisan (lewat Claude Code) · **Diperbaiki oleh:** Ghaisan (lewat Claude Code)

**Gejala.** `tokenize("a <> b")` menghasilkan `OP '<'` lalu `OP '>'`. Menurut SPESIFIKASI 2.5,
`<>` harus satu token `OP '<>'` (maximal munch). Di parser, query
`SELECT id FROM pesanan WHERE status <> 'LUNAS'` jadi error
`diharapkan ekspresi, ditemukan '>'`. Di `laporan_penjualan.sql`, statement SELECT baris 3
(`o.catatan <> 'FROM rahasia'`) hilang dari CRUD matrix, sehingga `pelanggan R` dan `pesanan R`
di baris 3 terlewat.

**Reproduksi minimal.**

```sql
SELECT id FROM t WHERE a <> 1
```

**Akar masalah.** Bab 4.5.2 (*Operators*) menjelaskan bahwa lexeme dua karakter seperti `!=`, `<=`,
dan `>=` dikenali dengan **lookahead**: setelah membaca karakter pertama, scanner mengintip karakter
berikutnya dengan `match()`. Bab 4.7 menyebut aturannya sebagai **maximal munch**: kalau dua aturan
leksikal sama-sama cocok, ambil yang paling panjang. Cabang `<` di kode lama hanya mengintip `=`,
jadi untuk input `<>` ia tidak pernah mencoba lexeme yang lebih panjang dan langsung memotong di `<`.
Karakter `>` lalu dibaca sebagai token baru. Parser menerima dua operator berurutan, padahal `>`
tidak bisa menjadi awal ekspresi, sehingga statement valid dianggap error sintaks.

**Perbaikan.** `crud/lexer.py`, fungsi `Lexer._scan_token` cabang `<`: setelah `<`, coba `=`
dulu, lalu `>`, baru jatuh ke `<` saja. Alternatif yang ditolak:
(1) parser menggabungkan token `<` yang langsung diikuti `>`, ditolak karena `a < > b` (pakai spasi)
ikut diterima, padahal itu bukan operator; urusan lexeme adalah tugas lexer;
(2) tabel operator umum yang dicocokkan dari yang terpanjang, ditolak karena terlalu besar untuk
satu kasus dan gaya `_match` per karakter sudah dipakai untuk `<=`, `>=`, `!=`.

**Test regresi.** `test_bug_a2_operator_tidak_sama_dengan_satu_token`

**Peran AI.** Ditemukan Claude Code saat membaca cabang operator di `_scan_token` sambil mencocokkan
daftar operator SPESIFIKASI 2.5. Verifikasi: reproduksi di kode asli memberi error
`ditemukan '>'`, test regresi gagal sebelum dan lulus sesudah commit `Bug A2`.

---

## Bug A3: dua kutip `''` di dalam string memotong string

**Ditemukan oleh:** Ghaisan (lewat Claude Code) · **Diperbaiki oleh:** Ghaisan (lewat Claude Code)

**Gejala.** `tokenize("'O''Brien'")` menghasilkan dua token, `STRING 'O'` dan `STRING 'Brien'`.
Menurut SPESIFIKASI 2.4 harusnya satu token `STRING` bernilai `O'Brien`. Di parser,
`... WHERE nama = 'O''Brien'` jadi error `diharapkan ';' di akhir statement, ditemukan 'Brien'`.
Di `pemeliharaan.sql` (dicek setelah T3 dan A1 beres), statement SELECT baris 3 dan UPDATE
baris 8 (`'O''Neil'`) ikut hilang dari CRUD matrix.

**Reproduksi minimal.**

```sql
SELECT id FROM t WHERE nama = 'O''Brien'
```

**Akar masalah.** Bab 4.6.1 (*String literals*) membaca string dengan loop yang berhenti di kutip
penutup. Bab 4.2.2 (*Literal value*) membedakan **lexeme** (teks mentah di source, termasuk kutip)
dengan **nilai literal** (isi yang sudah diproses). Di SQL, `''` di dalam string adalah *escape* untuk
satu karakter kutip, jadi lexeme `'O''Brien'` punya nilai literal `O'Brien`. Loop di kode lama
menganggap setiap `'` sebagai penutup tanpa melihat karakter sesudahnya. Untuk membedakan "kutip
penutup" dan "kutip ganda" scanner butuh **lookahead satu karakter** (teknik `peek`/`match` dari
Bab 4.5). Karena tidak ada lookahead, satu lexeme terpotong jadi dua token dan kutip ketiga malah
membuka string baru.

**Perbaikan.** `crud/lexer.py`, fungsi `Lexer._string`: saat ketemu `'`, cek apakah karakter
berikutnya juga `'` (`self._match("'")`). Kalau iya, tambahkan satu kutip ke nilai dan lanjut
membaca. Kalau tidak, string selesai. String yang berakhir `''` tanpa penutup tetap `LexError`.
Alternatif yang ditolak:
(1) parser menggabungkan dua token STRING yang berurutan, ditolak karena `'a' 'b'` (dua string
terpisah) ikut tergabung dan kutip di tengahnya hilang;
(2) membaca string dengan regex, ditolak karena gaya scanner ini membaca per karakter (Bab 4.4)
dan regex membuat posisi baris/kolom lebih sulit dijelaskan.

**Test regresi.** `test_bug_a3_dua_kutip_dalam_string_jadi_satu_kutip`

**Peran AI.** Ditemukan Claude Code saat membandingkan `_string` dengan contoh `'O''Brien'` di
SPESIFIKASI 2.4 (contoh yang sama muncul di `pemeliharaan.sql`). Verifikasi: reproduksi di kode asli
dan test regresi sebelum/sesudah commit `Bug A3`.

---

## Bug A4: AND dan OR punya presedensi yang sama

**Ditemukan oleh:** Ghaisan (lewat Claude Code) · **Diperbaiki oleh:** Ghaisan (lewat Claude Code)

**Gejala.** `SELECT id FROM t WHERE a = 1 OR b = 2 AND c = 3` di-parse menjadi
`(a = 1 OR b = 2) AND c = 3` (akar pohon `AND`). Menurut SPESIFIKASI 3.1, AND lebih kuat daripada OR,
jadi pohonnya harus `a = 1 OR (b = 2 AND c = 3)` (akar pohon `OR`). Bug ini tidak mengubah CRUD
matrix, tetapi tetap melanggar spesifikasi (Tips 3 di deskripsi tugas). Kasus nyatanya ada di
`audit.sql` baris 4 sampai 6 dan `pemeliharaan.sql` baris 6; cek dengan `python -m crud.cli FILE --ast`.

**Reproduksi minimal.**

```sql
SELECT id FROM t WHERE a = 1 OR b = 2 AND c = 3
```

**Akar masalah.** Bab 6.1 (*Ambiguity and the Parsing Game*) menjelaskan bahwa presedensi ditulis
di grammar dengan **membuat satu aturan untuk setiap tingkat presedensi**. Aturan untuk tingkat yang
lebih lemah merujuk aturan tingkat yang lebih kuat, jadi operator yang kuat "terikat" lebih dulu dan
berada lebih dalam di pohon. Bab 6.2 (*Recursive Descent Parsing*) lalu menerjemahkan setiap aturan
menjadi satu fungsi. Bab 9.3 (*Logical Operators*) memakai pola yang sama untuk `or` dan `and`:
`logic_or` memanggil `logic_and`. Fungsi lama `_logical` menggabungkan dua tingkat (OR dan AND)
dalam **satu** loop `while self._check_kw("AND", "OR")`. Grammar yang diwakilinya kira-kira
`logical = not_expr { ("AND" | "OR") not_expr }`, sehingga kedua operator dianggap setingkat dan
asosiatif kiri. Grammar seperti itu tidak ambigu, tetapi presedensinya berbeda dengan grammar
spesifikasi (`or_expr` dan `and_expr` dipisah).

**Perbaikan.** `crud/parser.py`: `_logical` diganti dua fungsi yang sama persis dengan grammar,
`_or_expr` (`and_expr { "OR" and_expr }`) dan `_and_expr` (`not_expr { "AND" not_expr }`), dan `_expr`
memanggil `_or_expr`. Alternatif yang ditolak:
(1) Pratt parser atau tabel presedensi (precedence climbing), ditolak karena lebih rumit dijelaskan
dan grammar di spesifikasi sudah dipisah per tingkat;
(2) tetap satu loop tetapi menyimpan angka presedensi tiap operator, ditolak karena logikanya
tersembunyi dan tidak lagi berpadanan satu fungsi satu aturan grammar.

**Test regresi.** `test_bug_a4_and_lebih_kuat_daripada_or`

**Peran AI.** Ditemukan Claude Code saat mencocokkan fungsi parser dengan grammar bagian 3 satu per
satu. Verifikasi: di kode asli akar pohon contoh di atas adalah `AND`, sesudah commit `Bug A4`
akarnya `OR`, dan test regresi berubah dari gagal ke lulus.

---

## Bug A5: error recovery membuang token sampai akhir file

**Ditemukan oleh:** Ghaisan (lewat Claude Code) · **Diperbaiki oleh:** Ghaisan (lewat Claude Code)

**Gejala.** Di `campuran_error.sql`, statement baris 4 (`SELECT id nama, FROM pesanan;`) memang
rusak. Tetapi setelah error itu, UPDATE baris 6 dan DELETE baris 8 yang valid juga hilang. CRUD
matrix file itu cuma `{'pelanggan': 'R'}`, padahal ground truth berisi `produk U` dan `keranjang D`.
Menurut SPESIFIKASI 6, setelah error parser membuang token **sampai dan termasuk `;` berikutnya**,
lalu melanjutkan statement sesudahnya.

**Reproduksi minimal.**

```sql
SELECT id nama, FROM pesanan;
DELETE FROM keranjang;
```

**Akar masalah.** Bab 6.3 (*Syntax Errors*) menyebut dua tuntutan untuk parser saat ketemu error:
melaporkan error lalu **tetap lanjut** supaya error dan kode berikutnya bisa diproses, tanpa
menghasilkan *cascaded error*. Caranya adalah **panic mode** (6.3.1): begitu error, parser masuk
mode panik, lalu **synchronize** (6.3.3) dengan membuang token sampai ke batas statement, di mana
parsing bisa dimulai lagi dengan aman. Di Lox, batas itu adalah token *sesudah* `;`. Fungsi
`_synchronize` lama tidak punya kondisi berhenti selain EOF, jadi ia membuang seluruh sisa file.
Memang tidak ada cascaded error, tetapi semua statement sesudahnya ikut terbuang, sehingga tujuan
error recovery (lanjut ke statement berikutnya) tidak tercapai.

**Perbaikan.** `crud/parser.py`, fungsi `Parser._synchronize`: buang token satu per satu, dan
berhenti setelah token yang dibuang adalah `;`. Kalau error terdeteksi tepat di `;`, `;` itu ikut
dibuang dan parsing lanjut dari statement berikutnya. Alternatif yang ditolak: berhenti juga di
keyword awal statement (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) seperti `synchronize()` Lox. Ini
ditolak karena `SELECT` bisa muncul di **dalam** statement (subquery, `INSERT ... SELECT`). Contoh:
`INSERT INTO t (a b) SELECT x FROM u;` error di `b`, lalu parser akan berhenti di `SELECT` dan mem-parse
`SELECT x FROM u` sebagai statement baru, padahal statement itu rusak dan seharusnya tidak dihitung
sama sekali (SPESIFIKASI 5 dan 6). Dalam grammar kita `;` tidak pernah muncul di dalam statement,
jadi `;` adalah batas yang pasti.

**Test regresi.** `test_bug_a5_error_recovery_berhenti_di_titik_koma`

**Peran AI.** Ditemukan Claude Code dari komentar `_synchronize` yang menyebut panic mode tetapi
loop-nya tanpa titik berhenti. Verifikasi: di kode asli `campuran_error.sql` cuma menghasilkan
`pelanggan R`; sesudah commit `Bug A5` keluar `pelanggan R`, `produk U`, `keranjang D` dengan tepat
satu error di baris 4. Test terlihat `test_pesan_error_berisi_baris` tetap lulus.

---

## Bug A6: `LEFT OUTER JOIN` ditolak parser

**Ditemukan oleh:** Ghaisan (lewat Claude Code) · **Diperbaiki oleh:** Ghaisan (lewat Claude Code)

**Gejala.** `SELECT c.id FROM pelanggan c LEFT OUTER JOIN alamat a ON a.pid = c.id` menghasilkan error
`Baris 1, kolom 35: diharapkan JOIN, ditemukan 'OUTER'`, padahal grammar bagian 3 menerima
`"LEFT" [ "OUTER" ] "JOIN"`. Di `pemeliharaan.sql` baris 3 sampai 6, SELECT dengan
`left outer join crm.alamat` hilang dari CRUD matrix (`crm.pelanggan R` dan `crm.alamat R` terlewat).
Statement yang sama juga kena A3 karena berisi `'O''Brien'`, jadi satu gejala di sini punya dua bug
(Tips 4), dan baru hilang setelah keduanya diperbaiki.

**Reproduksi minimal.**

```sql
SELECT a.id FROM a LEFT OUTER JOIN b ON b.x = a.x
```

**Akar masalah.** Bab 5.1 (*Context-Free Grammars*) menjelaskan bahwa grammar mendefinisikan
himpunan string yang valid, dan 5.1.2 (*Enhancing our notation*) memperkenalkan notasi untuk bagian
**opsional** (`?` di buku, `[ ]` di spesifikasi kita). Di Bab 6.2, setiap aturan diterjemahkan menjadi
satu fungsi, dan bagian opsional diterjemahkan menjadi `if match(...)`. Fungsi `_join` lama lupa
menerjemahkan `[ "OUTER" ]`, sehingga bahasa yang diterima fungsi itu **lebih sempit** daripada bahasa
yang didefinisikan grammar. Ini persis pertanyaan di Tips 2: "apakah fungsi ini menerima semua yang
diterima grammar, dan hanya itu?". Jawabannya tidak, ada input valid yang ditolak.

**Perbaikan.** `crud/parser.py`, fungsi `Parser._join`: setelah `LEFT`, tambahkan
`self._match_kw("OUTER")`. `kind` tetap `"LEFT"` karena artinya sama. Alternatif yang ditolak:
mengizinkan `OUTER` setelah `INNER` juga, atau `OUTER JOIN` tanpa `LEFT`, ditolak karena keduanya
tidak ada di grammar (fungsi harus menerima "hanya itu"). Test regresi juga memastikan
`INNER OUTER JOIN` tetap error.

**Test regresi.** `test_bug_a6_left_outer_join_diterima`

**Peran AI.** Ditemukan Claude Code saat mencocokkan `_join` dengan aturan `join` di grammar.
Verifikasi: reproduksi di kode asli memberi error di atas, sesudah commit `Bug A6` tidak ada error dan
`kind == "LEFT"`.

---

# BAGIAN HAFIZ: resolver dan analyzer

Diisi Hafiz dengan format yang sama (Bug B1, B2, ...). Daftar temuan awal yang sudah dibuktikan ada
di `docs/PEMBAGIAN_TUGAS.pdf` bagian 5.

---
