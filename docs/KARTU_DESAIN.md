# Kartu Desain

Tuliskan lima keputusan desain penting dalam pekerjaan kalian. Untuk tiap keputusan, sebutkan
alternatif yang ditolak dan alasannya. Contoh topik (boleh memilih yang lain):

- bagaimana parser membedakan `*` sebagai "semua kolom" dan sebagai perkalian;
- di mana dan bagaimana presedensi `AND`/`OR` dinyatakan;
- mengapa error recovery berhenti di `;`, bukan di keyword `SELECT` berikutnya;
- urutan pencarian scope dan akibatnya pada shadowing serta correlated subquery;
- mengapa kolom tanpa qualifier hanya dilihat di scope terdalam, dan apa kelemahannya;
- bagaimana implementasi `INSERT ... SELECT` atau komentar blok kalian.

Kartu 1 sampai 3 milik bagian Ghaisan (lexer dan parser), kartu 4 dan 5 milik bagian Hafiz
(resolver dan analyzer).

| No | Keputusan | Alternatif yang ditolak | Alasan |
| --- | --- | --- | --- |
| 1 | **`*` dibedakan oleh parser, bukan lexer** (Ghaisan). Lexer selalu mengeluarkan satu jenis token `STAR`. Artinya ditentukan oleh posisi di grammar: `STAR` tepat sesudah `SELECT [DISTINCT]` dibaca `_select_list` sebagai `Star` (semua kolom), `STAR` sesudah `(` di `function_call` jadi `COUNT(*)` (`star=True`), dan `STAR` di antara dua operand dibaca `_multiplicative` sebagai perkalian. | Lexer mengeluarkan dua jenis token berbeda, misalnya `ALL_COLUMNS` dan `MULTIPLY`. | Lexer hanya melihat karakter, bukan struktur kalimat. Bahasa leksikal adalah bahasa regular (Bab 4.3), jadi lexer tidak tahu apakah `*` sedang berada di awal `select_list` atau di tengah ekspresi. Informasi itu baru ada di parser (Bab 6.2), yang tahu sedang berada di aturan grammar mana. Satu token `STAR` juga membuat lexer tetap sederhana. |
| 2 | **Presedensi `AND`/`OR` dinyatakan lewat struktur fungsi** (Ghaisan, bug A4). Satu fungsi untuk satu tingkat presedensi, persis seperti grammar spesifikasi: `_expr` memanggil `_or_expr`, lalu `_and_expr`, `_not`, `_comparison`, `_additive`, `_multiplicative`, `_unary`, dan `_primary`. Fungsi yang lebih lemah memanggil yang lebih kuat, dan loop `while` di tiap fungsi membuat operatornya asosiatif kiri. | (a) Pratt parser atau precedence climbing dengan tabel angka presedensi. (b) Satu loop untuk `AND` dan `OR` sekaligus (kode lama). | (a) Bab 6.1 dan 6.2 memakai grammar bertingkat dan recursive descent, dan spesifikasi kita juga sudah ditulis bertingkat, jadi tiap fungsi bisa langsung dicocokkan dengan satu baris grammar saat demo. Pratt parser baru dibahas di bagian clox dan butuh tabel tambahan. (b) Satu loop membuat `AND` dan `OR` setingkat, itulah bug A4. |
| 3 | **Error recovery berhenti sesudah `;`** (Ghaisan, bug A5). Setelah `ParseError`, `_synchronize` membuang token sampai dan termasuk `;` berikutnya, lalu parsing lanjut dari statement sesudahnya. | Berhenti juga di keyword awal statement (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) seperti `synchronize()` di Lox (Bab 6.3.3). | Di SQL, `SELECT` juga muncul di dalam statement: subquery dan `INSERT ... SELECT`. Kalau parser berhenti di `SELECT`, potongan statement rusak bisa ter-parse sebagai statement baru. Contohnya `INSERT INTO t (a b) SELECT x FROM u;` akan menghasilkan statement `SELECT` palsu yang ikut dihitung di CRUD matrix, padahal statement rusak tidak boleh dihitung (SPESIFIKASI 5) dan harus menghasilkan tepat satu error (SPESIFIKASI 6). Dalam grammar kita `;` tidak pernah muncul di dalam statement, jadi batasnya pasti. |
| 4 | (diisi Hafiz) | | |
| 5 | (diisi Hafiz) | | |

Catatan implementasi TODO bagian Ghaisan:

- **T3 komentar blok** dibuat di lexer: setelah `/*`, buang karakter sampai ketemu `*/` yang
  **pertama** (tidak bersarang, sesuai SPESIFIKASI 2.3 dan bagian 9). `*` sendirian tidak menutup komentar.
  Kalau file habis sebelum `*/`, lempar `LexError` dengan posisi awal komentar. Ini mengadaptasi
  challenge 4 di akhir Bab 4, tanpa bagian nesting.
- **T1 `INSERT ... SELECT`** memakai ulang `_select()` yang sudah ada, lalu menyimpan hasilnya di
  `Insert.query` dengan `values = []`. Tidak perlu fungsi baru karena grammar `insert_stmt` memang
  merujuk aturan `select_stmt` yang sama.
