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
