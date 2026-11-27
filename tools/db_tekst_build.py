#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Buduje db.sqlite — źródło prawdy dla samego TEKSTU Ewangelii Mateusza,
osobne od bazy egzegetycznej (data/egzegeza_mateusza.sqlite).

W repozytorium Jana `db.sqlite` leżał jako gotowy plik binarny bez skryptu,
który by go odtwarzał — NOWA_KSIEGA.md nazywa go „najdroższym elementem całego
przedsięwzięcia". Tu jest odtwarzalny: trzy tabele powstają z modułów, których
proweniencję sprawdzono wiersz po wierszu wobec `../john/db.sqlite`.

    words         ← ../na/mt.sqlite (Mateusz, księga 470)
                    gotowy produkt pipeline'u z ../na/db/: tekst grecki wraz ze
                    znakami aparatu z 02.sqlite (NA27ca), numery Stronga i kody
                    gramatyczne z 01.sqlite (Reader's GNT), polski przekład
                    międzywierszowy z 03.sqlite (Popowski-Wojciechowski) oraz
                    `red` — znacznik słów Jezusa (verba Christi)
    latin_verses  ← CVUL.SQLite3 (Wulgata klementyńska), księga 470,
                    z normalizacją spacji i przedzieleniem Mt 17 na granice
                    wersetów greckich (patrz PODZIAL_17)
    commentaries  ← NA27ca.commentaries.SQLite3, księga 470 — aparat krytyczny
    eusebeios     ← NA28.commentaries.SQLite3 — numeracja Euzebiusza z nagłówków

Uruchomienie:  python3 tools/db_tekst_build.py
Wynik:         db.sqlite w korzeniu (budowany od zera)

Ścieżki źródeł nadpisują zmienne środowiskowe NA_DIR i PH4_DIR.

UWAGA o kodach gramatycznych. Mateusz dostaje kody Robinsona (`V-PAI-3S`),
bo taki zapis niosą moduły w ../na/db/. Jan ma w `db.sqlite` kody
dziesięcioznakowe MorphGNT (`v-3pai-s--`) z innego źródła. Nie przeliczamy
jednego na drugi: Robinson nie odróżnia medium od strony biernej w imiesłowach
perfecti (`V-RPP-NSM` odpowiada w Janie zarówno `v--xppnsm-`, jak i
`v--xmpnsm-`), więc konwersja dopisywałaby rozróżnienia, których w źródle nie
ma. Polski opis kodu w `browser/index.html` czyta oba zapisy.
"""
import os
import pathlib
import re
import sqlite3
import tempfile
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DB = ROOT / "db.sqlite"
KSIEGA_MATEUSZA = 470

NA_DIR = pathlib.Path(os.environ.get("NA_DIR", ROOT.parent / "na"))
PH4_DIR = pathlib.Path(os.environ.get("PH4_DIR", ROOT.parent / "bible-databases"))

ZRODLO_SLOWA = NA_DIR / "mt.sqlite"
ZRODLO_WULGATA = "CVUL"                    # CVUL.zip -> CVUL.SQLite3
ZRODLO_APARAT = "NA27ca"                   # NA27ca.zip -> NA27ca.commentaries.SQLite3
ZRODLO_EUZEBIUSZ = "NA28"                  # NA28.zip  -> NA28.commentaries.SQLite3

SCHEMA = """
CREATE TABLE words(
  book integer,
  chapter integer,
  verse integer,
  position integer,
  text varchar(255),
  strong varchar(255),
  morphology varchar(255),
  translation varchar(255),
  red boolean default false,
  primary key (book, chapter, verse, position)
);
CREATE TABLE latin_verses(
  book integer,
  chapter integer,
  verse integer,
  text varchar(255), eusebeios int default(0),
  primary key (book, chapter, verse)
);
CREATE TABLE commentaries(
  book numeric,
  chapter_from numeric,
  verse_from numeric,
  chapter_to numeric,
  verse_to numeric,
  is_preceding numeric,
  marker text,
  text text not null default '',
  primary key (book, chapter_from, verse_from, marker)
);
"""

# Wulgata klementyńska dzieli Mt 17 inaczej niż tekst krytyczny: łaciński
# w. 14 obejmuje grecki 14 i 15 (grecki 15 zaczyna się od „καὶ λέγων", czyli
# łacińskiego „dicens:"), a od tego miejsca numeracja idzie o jeden w tył.
# Łaciński w. 20 („Hoc autem genus…") odpowiada greckiemu 17,21, którego NA28
# nie ma — zostaje jako wiersz bez greki, tak jak J 5,4 w bazie Jana.
PODZIAL_17_CIECIE = "dicens:"


def otworz(sciezka):
    return sqlite3.connect(f"file:{sciezka}?mode=ro", uri=True)


_TYMCZASOWY = tempfile.TemporaryDirectory()


def modul(katalog, nazwa, sufiks=""):
    """Moduł ph4 jako ścieżka do .SQLite3 — rozpakowany albo wyjęty z .zip."""
    plik = f"{nazwa}{sufiks}.SQLite3"
    kandydaci = [katalog / plik] + list(katalog.glob(f"**/{plik}"))
    for kandydat in kandydaci:
        if kandydat.exists():
            return kandydat
    archiwum = katalog / f"{nazwa}.zip"
    if archiwum.exists():
        with zipfile.ZipFile(archiwum) as z:
            if plik in z.namelist():
                return pathlib.Path(z.extract(plik, _TYMCZASOWY.name))
    raise SystemExit(
        f"Brak modułu {plik} w {katalog}.\n"
        f"Potrzebny jest {nazwa}.zip (ph4.org) albo rozpakowany moduł; "
        f"katalog wskazuje PH4_DIR."
    )


def normalizuj_lacine(tekst):
    """Spacja przed interpunkcją (zapis francuski) i wielokrotne spacje."""
    return re.sub(r"\s+", " ", re.sub(r"\s+([;:,.!?])", r"\1", tekst)).strip()


def wczytaj_slowa(cur):
    src = otworz(ZRODLO_SLOWA)
    wiersze = src.execute(
        """SELECT book, chapter, verse, position, text, strong, morphology,
                  translation, red
             FROM words WHERE book = ? ORDER BY chapter, verse, position""",
        (KSIEGA_MATEUSZA,)).fetchall()
    cur.executemany("INSERT INTO words VALUES (?,?,?,?,?,?,?,?,?)", wiersze)
    src.close()
    return len(wiersze)


def wczytaj_wulgate(cur):
    src = otworz(modul(PH4_DIR, ZRODLO_WULGATA))
    lac = {(c, v): normalizuj_lacine(t) for c, v, t in src.execute(
        "SELECT chapter, verse, text FROM verses WHERE book_number = ?",
        (KSIEGA_MATEUSZA,))}
    src.close()

    wiersze = []
    for (ch, v), tekst in sorted(lac.items()):
        if ch != 17:
            wiersze.append((ch, v, tekst))
            continue
        if v < 14:
            wiersze.append((ch, v, tekst))
        elif v == 14:
            # jeden werset łaciński na dwa greckie — cięcie przed „dicens:"
            i = tekst.find(PODZIAL_17_CIECIE)
            if i < 0:
                raise SystemExit('''Mt 17,14: nie znaleziono cięcia „dicens:" '''
                                 '''— sprawdź moduł Wulgaty''')
            wiersze.append((ch, 14, tekst[:i].strip()))
            wiersze.append((ch, 15, tekst[i:].strip()))
        else:
            wiersze.append((ch, v + 1, tekst))

    cur.executemany(
        "INSERT INTO latin_verses(book, chapter, verse, text) VALUES (?,?,?,?)",
        [(KSIEGA_MATEUSZA, ch, v, t) for ch, v, t in wiersze])
    return len(wiersze)


def wczytaj_aparat(cur):
    src = otworz(modul(PH4_DIR, ZRODLO_APARAT, ".commentaries"))
    wiersze = src.execute(
        """SELECT book_number, chapter_number_from, verse_number_from,
                  chapter_number_to, verse_number_to, is_preceding, marker, text
             FROM commentaries WHERE book_number = ?""",
        (KSIEGA_MATEUSZA,)).fetchall()
    src.close()
    # klucz główny to (book, chapter_from, verse_from, marker); zderzenia
    # oznaczają dwie noty aparatu o tym samym znaku w jednym wersecie —
    # niech padnie, zamiast cicho połknąć notę
    cur.executemany(
        "INSERT INTO commentaries VALUES (?,?,?,?,?,?,?,?)", wiersze)
    return len(wiersze)


EUZEBIUSZ = re.compile(r"Eusebian section/canon number:.*?<td>(\d+)</td>", re.S)


def wczytaj_euzebiusza(cur):
    src = otworz(modul(PH4_DIR, ZRODLO_EUZEBIUSZ, ".commentaries"))
    n = 0
    for ch, v, tekst in src.execute(
            """SELECT chapter_number_from, verse_number_from, text
                 FROM commentaries WHERE book_number = ?""",
            (KSIEGA_MATEUSZA,)):
        m = EUZEBIUSZ.search(tekst or "")
        if not m:
            continue
        cur.execute("""UPDATE latin_verses SET eusebeios = ?
                        WHERE book = ? AND chapter = ? AND verse = ?""",
                    (int(m.group(1)), KSIEGA_MATEUSZA, ch, v))
        n += cur.rowcount
    src.close()
    return n


def build():
    if not ZRODLO_SLOWA.exists():
        raise SystemExit(f"Brak źródła słów: {ZRODLO_SLOWA}\n"
                         f"Wskaż katalog projektu NA przez NA_DIR.")
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    cur = con.cursor()

    slowa = wczytaj_slowa(cur)
    lacina = wczytaj_wulgate(cur)
    aparat = wczytaj_aparat(cur)
    euzebiusz = wczytaj_euzebiusza(cur)
    con.commit()

    rozdzialy = cur.execute("SELECT max(chapter) FROM words").fetchone()[0]
    wersety = cur.execute(
        "SELECT count(*) FROM (SELECT DISTINCT chapter, verse FROM words)"
    ).fetchone()[0]
    czerwone = cur.execute("SELECT count(*) FROM words WHERE red = 1").fetchone()[0]
    con.close()

    print(f"words            {slowa:6d}  ({wersety} wersetów, {rozdzialy} rozdziałów, "
          f"{czerwone} słów Jezusa)")
    print(f"latin_verses     {lacina:6d}  (numeracja Euzebiusza w {euzebiusz})")
    print(f"commentaries     {aparat:6d}")
    print(f"\nOK -> {DB}")


if __name__ == "__main__":
    build()
