"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.

File ini dibagi dua blok supaya rapi saat demo:
- BAGIAN GHAISAN: lexer dan parser (bug A1 sampai A6, TODO T1 dan T3)
- BAGIAN HAFIZ: resolver, analyzer, dan data (bug B1 dan seterusnya, TODO T2)
Nomor bug sama dengan nomor di docs/LAPORAN_BUG.md.
"""
import pytest

from crud import ast_nodes as ast
from crud.lexer import LexError, TokenType as T, tokenize
from crud.parser import parse_sql


# Fungsi bantu: ambil daftar (jenis, nilai) semua token, tanpa token EOF.
def token_list(sql):
    return [(tok.type, tok.value) for tok in tokenize(sql) if tok.type != T.EOF]


# Fungsi bantu: parse SQL yang berisi tepat satu statement tanpa error.
def satu_statement(sql):
    script = parse_sql(sql)
    assert script.errors == [], script.errors
    assert len(script.statements) == 1
    return script.statements[0]


# =====================================================================
# BAGIAN GHAISAN: lexer dan parser (Bab 4, 5, 6)
# =====================================================================

# ---- Test regresi, satu test untuk satu bug -------------------------

def test_bug_a1_keyword_tidak_peka_huruf_besar_kecil():
    # Bug A1: dulu "select" dan "FrOm" dibaca sebagai IDENT, bukan KEYWORD.
    # Menurut spesifikasi 2.2, keyword tidak peka huruf besar/kecil
    # dan nilainya selalu disimpan dalam huruf besar.
    assert token_list("select Id FrOm t") == [
        (T.KEYWORD, "SELECT"),
        (T.IDENT, "Id"),
        (T.KEYWORD, "FROM"),
        (T.IDENT, "t"),
    ]
    # Kata yang hanya DIAWALI keyword tetap IDENT.
    assert token_list("selection fromage") == [(T.IDENT, "selection"), (T.IDENT, "fromage")]
    # Akibatnya di parser: query huruf kecil sekarang bisa di-parse.
    stmt = satu_statement("select id from pelanggan where aktif = 1")
    assert stmt.sources[0].name == "pelanggan"


def test_bug_a2_operator_tidak_sama_dengan_satu_token():
    # Bug A2: dulu "<>" dipecah jadi dua token "<" dan ">".
    # Spesifikasi 2.5: lexer selalu mengambil operator terpanjang (maximal munch).
    assert token_list("a <> b") == [(T.IDENT, "a"), (T.OP, "<>"), (T.IDENT, "b")]
    # Operator lain yang diawali "<" tetap benar.
    assert token_list("a <= b < c") == [
        (T.IDENT, "a"), (T.OP, "<="), (T.IDENT, "b"), (T.OP, "<"), (T.IDENT, "c")]
    # Akibatnya di parser: WHERE dengan "<>" tidak lagi dianggap error sintaks.
    stmt = satu_statement("SELECT id FROM pesanan WHERE status <> 'LUNAS'")
    assert stmt.where.op == "<>"


def test_bug_a3_dua_kutip_dalam_string_jadi_satu_kutip():
    # Bug A3: dulu 'O''Brien' dibaca sebagai DUA string: 'O' dan 'Brien'.
    # Spesifikasi 2.4: dua kutip berturut-turut di dalam string artinya satu kutip.
    assert token_list("'O''Brien'") == [(T.STRING, "O'Brien")]
    # String kosong dan string yang isinya hanya satu kutip.
    assert token_list("'' ''''") == [(T.STRING, ""), (T.STRING, "'")]
    # Kalau string berakhir dengan '' tanpa kutip penutup, string belum ditutup.
    with pytest.raises(LexError):
        tokenize("'abc''")


# ---- Test untuk TODO yang dilengkapi (T1 dan T3) --------------------

def test_todo_t3_komentar_blok_lintas_baris_dan_berisi_bintang():
    # TODO T3: komentar blok /* ... */ boleh lintas baris dan boleh berisi "*".
    toks = tokenize("/* baris 1 * masih komentar\n   baris 2 ** */ SELECT")
    assert toks[0].type == T.KEYWORD and toks[0].value == "SELECT"
    # Posisi token sesudah komentar tetap benar: baris 2, kolom 18.
    assert (toks[0].line, toks[0].col) == (2, 18)
    # Komentar blok tidak menghasilkan token apa pun.
    assert token_list("/***/") == []


def test_todo_t3_komentar_blok_tidak_ditutup_adalah_lexerror():
    # Spesifikasi 2.3: komentar blok yang tidak ditutup adalah LexError.
    # Posisi error menunjuk ke awal komentar (baris 2, kolom 3).
    with pytest.raises(LexError) as info:
        tokenize("SELECT 1\n  /* lupa ditutup *")
    assert (info.value.line, info.value.col) == (2, 3)


# ---- Test kasus tepi (2 dari 5, sisanya di bagian Hafiz) ------------

def test_tepi_komentar_blok_tidak_bersarang():
    # Kenapa berisiko: banyak orang mengira komentar blok bisa bersarang.
    # Spesifikasi 2.3 bilang TIDAK bersarang, jadi "*/" pertama langsung
    # menutup komentar. Sisa " c */" harus dibaca sebagai token biasa.
    assert token_list("/* a /* b */ c */") == [
        (T.IDENT, "c"), (T.STAR, "*"), (T.OP, "/")]
