#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nanosi kody gramatyczne MorphGNT na kolumnę `words.morphology` w db.sqlite.

Kody MorphGNT są zapisem dziesięcioznakowym: część mowy (2 znaki) plus kod
fleksyjny (8 znaków), złożone i zapisane małymi literami — `v-3iai-s--`,
`n-----dsf-`, `ra----nsm-`. Taki zapis ma baza Jana i taki jest w obu
repozytoriach jedynym zapisem morfologii.

    python3 tools/morphgnt_import.py                  # Mateusz, ta baza
    python3 tools/morphgnt_import.py --db ../john/db.sqlite --book 500 \\
            --plik 64-Jn-morphgnt.txt --zachowaj-istniejace

Źródło: MorphGNT, edycja SBLGNT (James K. Tauber, red.), analiza
morfologiczna i lematyzacja na licencji CC-BY-SA 3.0,
https://github.com/morphgnt/sblgnt. Pobieramy wyłącznie **kody**; tekst
grecki bazy pozostaje ten, który wnosi `db_tekst_build.py`.

## Dlaczego dopasowanie, a nie podmiana

MorphGNT idzie za tekstem SBLGNT, a `db.sqlite` za tekstem krytycznym NA wraz
ze znakami aparatu, więc ciągi tokenów nie są identyczne — różnią się tam,
gdzie wydania czytają inaczej (Βηθζαθά / Βηθεσδά w J 5,2), gdzie NA bierze
słowo w nawias edytorski, a SBLGNT je pomija, i gdzie różni się kolejność
(Mt 5,4-5). Tokeny parujemy po znormalizowanej grece (bez akcentów, znaków
aparatu, nawiasów i wielkości liter) w dwóch przebiegach difflib: najpierw
w obrębie rozdziału, potem w obrębie wersetu dla tego, czego pierwszy
przebieg nie dosiągł.

Tokenów niedopasowanych **nie zgadujemy**. Zostają bez kodu (albo z kodem
dotychczasowym, gdy podano `--zachowaj-istniejace`) i skrypt wypisuje ich
liczbę. To są dokładnie te miejsca, w których tekst NA różni się od SBLGNT,
czyli te, dla których kod MorphGNT byłby wymysłem.
"""
import argparse
import collections
import difflib
import os
import pathlib
import re
import sqlite3
import unicodedata
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
MORPHGNT_URL = "https://raw.githubusercontent.com/morphgnt/sblgnt/{wersja}/{plik}"
WERSJA = os.environ.get("MORPHGNT_WERSJA", "6.12")

# Znaki, które nie należą do słowa: aparat krytyczny NA, nawiasy edytorskie,
# indeksy powtórzonych znaków aparatu.
SIGLA = set("°˸⸀⸁⸂⸃⸄⸅⸆⸇⸈⸉⸊⸋⸌⸍⸎⸏⸐⸑⸒⸓⸔⸕⸖⸗⸘⸙⸚⸛⸜⸝⸞⸟¹²³[]()⟦⟧")


def baza(s):
    """Forma do parowania: bez sigli, nawiasów, diakrytyki i wielkości liter."""
    s = "".join(c for c in (s or "") if c not in SIGLA)
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^α-ω]", "", s.replace("ς", "σ"))


def wczytaj_morphgnt(plik, katalog=None):
    """Lista tokenów MorphGNT. Kolejno: bcv, część mowy, kod fleksyjny, tekst,
    słowo bez interpunkcji, forma znormalizowana, lemat."""
    if katalog:
        tresc = (pathlib.Path(katalog) / plik).read_text(encoding="utf-8")
    else:
        url = MORPHGNT_URL.format(wersja=WERSJA, plik=plik)
        with urllib.request.urlopen(url, timeout=60) as r:
            tresc = r.read().decode("utf-8")
    tokeny = []
    for linia in tresc.splitlines():
        cz = linia.split()
        if len(cz) < 5:
            continue
        bcv = cz[0]
        tokeny.append({"chapter": int(bcv[2:4]), "verse": int(bcv[4:6]),
                       "kod": (cz[1] + cz[2]).lower(), "baza": baza(cz[4])})
    if not tokeny:
        raise SystemExit(f"Plik MorphGNT {plik} nie dał ani jednego tokenu.")
    return tokeny


def wczytaj_slowa(con, ksiega):
    return [{"chapter": ch, "verse": v, "position": p, "text": t, "kod": m,
             "baza": baza(t)}
            for ch, v, p, t, m in con.execute(
                """SELECT chapter, verse, position, text, morphology FROM words
                   WHERE book = ? ORDER BY chapter, verse, position""", (ksiega,))]


def _paruj(indeksy, slowa, tokeny, wynik, zajete):
    A = [slowa[i]["baza"] for i in indeksy]
    B = [t["baza"] for t in tokeny]
    dopasowania = difflib.SequenceMatcher(a=A, b=B, autojunk=False).get_matching_blocks()
    for a0, b0, n in dopasowania:
        for k in range(n):
            i, j = indeksy[a0 + k], b0 + k
            if wynik[i] is None and j not in zajete:
                wynik[i] = tokeny[j]["kod"]
                zajete.add(j)


def dopasuj(slowa, tokeny):
    """Lista kodów równoległa do `slowa`; None tam, gdzie nie ma pary."""
    wynik = [None] * len(slowa)
    mg_rozdzial, mg_werset = collections.defaultdict(list), collections.defaultdict(list)
    for t in tokeny:
        mg_rozdzial[t["chapter"]].append(t)
        mg_werset[(t["chapter"], t["verse"])].append(t)
    db_rozdzial, db_werset = collections.defaultdict(list), collections.defaultdict(list)
    for i, w in enumerate(slowa):
        db_rozdzial[w["chapter"]].append(i)
        db_werset[(w["chapter"], w["verse"])].append(i)

    for ch, indeksy in db_rozdzial.items():
        _paruj(indeksy, slowa, mg_rozdzial.get(ch, []), wynik, set())
    for klucz, indeksy in db_werset.items():
        brak = [i for i in indeksy if wynik[i] is None]
        if brak:
            _paruj(brak, slowa, mg_werset.get(klucz, []), wynik, set())
    return wynik


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--db", default=str(ROOT / "db.sqlite"))
    p.add_argument("--book", type=int, default=470, help="numer księgi (Mt 470, J 500)")
    p.add_argument("--plik", default="61-Mt-morphgnt.txt",
                   help="plik MorphGNT (Mt 61-Mt-morphgnt.txt, J 64-Jn-morphgnt.txt)")
    p.add_argument("--katalog", default=os.environ.get("MORPHGNT_DIR"),
                   help="lokalny katalog z plikami MorphGNT; bez niego pobieramy z GitHuba")
    p.add_argument("--zachowaj-istniejace", action="store_true",
                   help="tokenom bez pary zostaw kod, który już mają")
    a = p.parse_args()

    tokeny = wczytaj_morphgnt(a.plik, a.katalog)
    con = sqlite3.connect(a.db)
    slowa = wczytaj_slowa(con, a.book)
    if not slowa:
        raise SystemExit(f"W {a.db} nie ma księgi {a.book}.")
    kody = dopasuj(slowa, tokeny)

    zmiany, bez_pary, bez_kodu = 0, 0, 0
    for w, kod in zip(slowa, kody):
        if kod is None:
            bez_pary += 1
            if a.zachowaj_istniejace:
                continue
            kod = ""
        if kod != (w["kod"] or ""):
            zmiany += 1
        con.execute("""UPDATE words SET morphology = ?
                        WHERE book = ? AND chapter = ? AND verse = ? AND position = ?""",
                    (kod, a.book, w["chapter"], w["verse"], w["position"]))
        if not kod:
            bez_kodu += 1
    con.commit()
    con.close()

    pokryte = len(slowa) - bez_pary
    print(f"MorphGNT {WERSJA} / {a.plik}: {len(tokeny)} tokenów źródła")
    print(f"księga {a.book} w {a.db}: {len(slowa)} słów")
    print(f"  dopasowane  {pokryte:6d}  ({pokryte / len(slowa) * 100:.2f}%)")
    print(f"  bez pary    {bez_pary:6d}  ({bez_pary / len(slowa) * 100:.2f}%)"
          + ("  — kod dotychczasowy zachowany" if a.zachowaj_istniejace
             else f", z tego bez kodu {bez_kodu}"))
    print(f"  zmienione   {zmiany:6d}")


if __name__ == "__main__":
    main()
