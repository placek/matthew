---
name: zrodlo-tekstu
description: Jak zbudować albo przebudować db.sqlite — źródło samego tekstu Ewangelii, osobne od egzegezy: greka z aparatem, interlinia polska, Wulgata, morfologia MorphGNT, numeracja Euzebiusza. Zakres: który moduł zasila którą kolumnę, jak dowieść proweniencji, przedzielenie Wulgaty na granice wersetów greckich, import MorphGNT, pułapki. Użyj, gdy zadanie brzmi „zbuduj db.sqlite", „zrób źródło tekstu dla Marka / Łukasza", „brakuje interlinii, Wulgaty albo aparatu", „morfologia jest w złym zapisie" albo „skąd wziął się ten plik".
---

# Źródło tekstu: db.sqlite

`db.sqlite` leży w korzeniu repozytorium i jest źródłem prawdy dla **samego
tekstu** księgi. Nie ma nic wspólnego z bazą egzegezy — ta trzyma komentarz
i powstaje z `data/*.json`. `NOWA_KSIEGA.md` nazywa źródło tekstu
„najdroższym elementem całego przedsięwzięcia" i trzeba je rozstrzygnąć,
zanim napisze się pierwszą perykopę.

W Mateuszu jest odtwarzalne: `make tekst` (`tools/db_tekst_build.py`) składa je
od zera, a `tools/morphgnt_import.py` nanosi morfologię. W Janie leżało jako
gotowy plik binarny bez skryptu — stąd ten dokument. Ten plik jest identyczny
w obu repozytoriach; pełny builder stoi w `../matthew/tools/db_tekst_build.py`
i jest wzorcem do przepisania pod nową księgę, a `tools/morphgnt_import.py`
jest w obu.

## Zasada naczelna

**Każda kolumna ma dowiedzione źródło albo nie ma jej wcale.** Morfologia,
numer Stronga, świadek aparatu i kod gramatyczny to dane faktograficzne
podane z pozorem precyzji: zmyślone albo przeliczone „na oko" są gorsze niż
puste, bo nikt ich potem nie odróżni od prawdziwych. Pusta komórka jest
uczciwa i widoczna; wymyślony kod `n-----dsf-` jest błędem, który przeżyje
całą książkę.

Z tego wynika cała reszta: zanim zaufasz modułowi, **dowiedź**, że to z niego
powstała istniejąca baza (niżej jest na to procedura), a tam, gdzie wydania
czytają inaczej, zostaw dziurę.

## Co jest w środku

Trzy tabele, DDL w `tools/db_tekst_build.py` (celowo skopiowane znak w znak
z bazy Jana, bo `browser/app.py` jest napisany pod nią):

```sql
words(book, chapter, verse, position, text, strong, morphology, translation, red)
latin_verses(book, chapter, verse, text, eusebeios)
commentaries(book, chapter_from, verse_from, chapter_to, verse_to,
             is_preceding, marker, text)
```

`position` liczy od zera. `red` znaczy słowa Jezusa (*verba Christi*).
`words.text` niesie grekę **wraz ze znakami aparatu** (`°`, `⸀`, `⸂`, `⸆`…) —
przeglądarka podświetla je w interlinii i wiąże z notami z `commentaries`
przez kolumnę `marker`.

## Mapa źródeł — sprawdzona wiersz po wierszu

| kolumna / tabela | źródło | uwagi |
|---|---|---|
| `words` (całość) | `../na/<ksiega>.sqlite` | gotowy produkt pipeline'u z `../na/db/`; `mt`, `mk`, `lk` istnieją |
| `words.text` | `../na/db/02.sqlite` — NA27ca, greka ze znakami aparatu | w `mt.sqlite` kropka została kropką, w bazie Jana zamieniono ją na `·` |
| `words.strong` | `../na/db/01.sqlite` — *A Reader's Greek New Testament*, wyd. 3 | |
| `words.translation` | `../na/db/03.sqlite` — przekład międzywierszowy Popowskiego-Wojciechowskiego | rodzajniki dostają `-`; wielowyrazowe glosy bywają przesunięte o jeden token |
| `words.morphology` | **MorphGNT, edycja SBLGNT** — `tools/morphgnt_import.py` | `01.sqlite` niesie kody Robinsona i **nie jest** źródłem morfologii, patrz niżej |
| `words.red` | **żaden moduł** — naniesione ręcznie, już jest w `mt/mk/lk.sqlite` | dla księgi bez gotowego pliku to osobna, ręczna robota |
| `latin_verses.text` | moduł `CVUL` (Wulgata klementyńska) z `../bible-databases` | normalizacja spacji + przedzielenie na granice wersetów greckich |
| `latin_verses.eusebeios` | nagłówki modułu `NA28.commentaries` | nieużywane przez kod; w Janie 206 z 212 wartości zgadza się z tym modułem |
| `commentaries` | moduł `NA27ca.commentaries` | w Janie 1527 z 1528 wierszy identycznych co do znaku |

Moduły ph4 (`CVUL`, `NA27ca`, `NA28`) leżą w `../bible-databases` jako `.zip`;
`modul()` w `db_tekst_build.py` wyjmuje je do katalogu tymczasowego, więc nie
trzeba ich rozpakowywać. Ścieżki nadpisują `NA_DIR` i `PH4_DIR`.

### Numery ksiąg i pliki MorphGNT

Numeracja modułów ph4 idzie dziesiątkami od Mateusza:

| księga | numer | plik `../na` | plik MorphGNT | słów | wersetów | rozdz. |
|---|---|---|---|---|---|---|
| Mateusz | 470 | `mt.sqlite` | `61-Mt-morphgnt.txt` | 18 346 | 1068 | 28 |
| Marek | 480 | `mk.sqlite` | `62-Mk-morphgnt.txt` | 11 304 | 673 | 16 |
| Łukasz | 490 | `lk.sqlite` | `63-Lk-morphgnt.txt` | 19 480 | 1149 | 24 |
| Jan | 500 | — (w `db.sqlite`) | `64-Jn-morphgnt.txt` | 15 635 | 878 | 21 |

Numer księgi stoi w kodzie jako `KSIEGA_<NAZWA>` w `browser/app.py`
i `tools/db_tekst_build.py`. Przy nowej księdze **zmień nazwę stałej**,
nie tylko wartość — inaczej zostanie kłamliwa.

## Krok 1: dowiedź proweniencji, zanim zaufasz modułowi

Nie zakładaj, że moduł o właściwej nazwie jest tym, z którego powstała
istniejąca baza. W `../bible-databases` leży kilka aparatów i kilka Wulgat,
a różnią się liczbą wierszy i treścią. Procedura jest prosta: weź księgę,
która **już jest** w bazie (Jan, 500), i porównaj ją z kandydatem. Moduły
rozpakuj wcześniej w katalogu roboczym (`unzip ../bible-databases/NA27ca.zip`)
albo podaj do nich pełne ścieżki.

```bash
python3 - <<'PY'
import sqlite3, collections
ro = lambda p: sqlite3.connect(f'file:{p}?mode=ro', uri=True)
j = ro('/srv/data/projects/placek/john/db.sqlite')
kandydat = ro('NA27ca/NA27ca.commentaries.SQLite3')   # podstaw swojego; rozpakuj wcześniej
A = collections.Counter(j.execute(
    '''SELECT chapter_from, verse_from, chapter_to, verse_to, is_preceding,
              marker, text FROM commentaries WHERE book=500''').fetchall())
B = collections.Counter(kandydat.execute(
    '''SELECT chapter_number_from, verse_number_from, chapter_number_to,
              verse_number_to, is_preceding, marker, text
         FROM commentaries WHERE book_number=500''').fetchall())
print('w bazie', sum(A.values()), '| w module', sum(B.values()))
print('tylko w bazie', sum((A - B).values()), '| tylko w module', sum((B - A).values()))
PY
```

Zero po obu stronach (albo jeden-dwa wiersze, jak przy `NA27ca` i ręcznej
poprawce) znaczy, że to **ten** moduł. Rozjazd o setki wierszy znaczy, że to
inny — `NA28.commentaries` ma dla Jana 856 wierszy, `Leo-NA28+` 277,
a `NA27ca` 1528, czyli dokładnie tyle, ile baza.

Dla Wulgaty ta sama metoda z normalizacją, bo moduł zapisuje spację przed
średnikiem po francusku:

```python
norm = lambda s: re.sub(r'\s+', ' ', re.sub(r'\s+([;:,.!?])', r'\1', s)).strip()
```

**Kiedy proweniencji dowieść się nie da** (nowa warstwa, nic do porównania),
powiedz to wprost w `README.md` i nie udawaj pewności. To właśnie przypadek
`eusebeios`: 206 z 212 wartości Jana zgadza się z `NA28.commentaries`, sześć
różni się o jeden, jedna jest tam nieobecna — więc kolumnę zasilamy z tego
modułu, ale z notą, że pochodzenie pozostałych nie jest ustalone. Kolumna
jest martwa (żaden kod jej nie czyta), więc koszt niepewności jest zerowy;
gdyby była czytana, trzeba by ją zostawić pustą.

## Krok 2: `words`

Jeśli `../na/<ksiega>.sqlite` istnieje, to jest cała robota — plik jest już
produktem pipeline'u z `../na/db/` i niesie `text`, `strong`, `translation`
oraz `red`. Przepisz go i nadpisz morfologię (krok 5).

Jeśli nie istnieje, trzeba ten pipeline odtworzyć z `../na/db/`: tokenizacja
greki z `02.sqlite` ze wplecionymi znakami aparatu (`<f>…</f>` rozpakowane do
sąsiedniego tokenu), numery Stronga z `01.sqlite` (format
`wyraz<S>1722</S> <m>PREP</m>`), a przekład polski z `03.sqlite`, który jest
interlinią spłaszczoną do jednej linii — granice słów trzeba odzyskać
dopasowaniem do liczby tokenów greckich. **Jest to robota niebanalna
i obarczona błędem**: w gotowych plikach widać przesunięcia przy glosach
wielowyrazowych (Mt 28,20 `ὅσα` → `(rzeczy)` zamiast `jakie`). Nie zaczynaj
od niej, dopóki nie sprawdzisz, czy gotowy plik już nie leży w `../na`.

`red` nie ma w żadnym module — ani `01`, ani `02`, ani `03` nie mają znacznika
`<J>`. Dla Mt, Mk i Lk jest naniesiony w gotowych plikach; dla księgi bez
takiego pliku to osobna, ręczna decyzja werset po wersecie.

## Krok 3: Wulgata i przedzielenie na granice greckie

Wulgata klementyńska dzieli wersety inaczej niż tekst krytyczny, więc
samo `JOIN` po (rozdział, werset) daje kolumnę łacińską przesuniętą
względem greki. Najpierw **zmierz** rozjazd:

```bash
python3 - <<'PY'
import sqlite3, collections
KSIEGA = 480                      # Marek
cv = sqlite3.connect('file:CVUL/CVUL.SQLite3?mode=ro', uri=True)
g = sqlite3.connect('file:/srv/data/projects/placek/na/mk.sqlite?mode=ro', uri=True)
gs = {(c, v) for c, v in g.execute('SELECT DISTINCT chapter, verse FROM words WHERE book=?', (KSIEGA,))}
ls = {(c, v) for c, v in cv.execute('SELECT chapter, verse FROM verses WHERE book_number=?', (KSIEGA,))}
mg, ml = collections.Counter(), collections.Counter()
for c, v in gs: mg[c] = max(mg[c], v)
for c, v in ls: ml[c] = max(ml[c], v)
print('rozdziały o innej długości:', [(c, mg[c], ml.get(c)) for c in sorted(mg) if mg[c] != ml.get(c)])
print('w grece bez łaciny:', sorted(gs - ls))
print('w łacinie bez greki:', sorted(ls - gs))
PY
```

Wynik dla trzech ksiąg, już policzony:

| księga | rozdziały do przedzielenia | wersety łacińskie bez greki (pominięcia tekstu krytycznego) |
|---|---|---|
| Mateusz | 17 (greka do 27, Wulgata do 26) | 17,21 · 18,11 · 23,14 |
| Marek | 4 · 8 · 9 | 7,16 · 9,44 · 9,46 · 11,26 · 15,28 |
| Łukasz | **żaden** — numeracje się pokrywają | 17,36 · 23,17 |

Wersety łacińskie bez greki **zostają** w bazie jako wiersze bez
odpowiednika — tak samo jak J 5,4 w bazie Jana. Nie usuwaj ich.

Przedzielenie rób tak, jak jest w `wczytaj_wulgate()`: znajdź po treści
miejsce, w którym jeden werset łaciński obejmuje dwa greckie, przetnij go
i przesuń resztę rozdziału. W Mateuszu łaciński w. 14 obejmuje grecki 14 i 15
(grecki 15 otwiera καὶ λέγων — „i mówiąc", po łacinie *dicens*), więc cięcie
idzie przed `dicens:`, a od w. 15 numeracja przesuwa się o jeden.

**Cięcie znajdź przez porównanie treści, nie przez zgadywanie.** Wypisz obok
siebie grekę, polski i łacinę dla kilkunastu wersetów wokół rozjazdu
i zobacz, gdzie łacina łączy dwa greckie zdania:

```bash
python3 - <<'PY'
import sqlite3
cv = sqlite3.connect('file:CVUL/CVUL.SQLite3?mode=ro', uri=True)
g = sqlite3.connect('file:/srv/data/projects/placek/na/mk.sqlite?mode=ro', uri=True)
KSIEGA, ROZDZIAL = 480, 4                 # Marek 4
ile = g.execute('SELECT max(verse) FROM words WHERE book=? AND chapter=?',
                (KSIEGA, ROZDZIAL)).fetchone()[0]
for v in range(1, ile + 1):
    gr = ' '.join(r[0] for r in g.execute(
        '''SELECT text FROM words WHERE book=? AND chapter=? AND verse=?
             ORDER BY position''', (KSIEGA, ROZDZIAL, v)))
    la = cv.execute('SELECT text FROM verses WHERE book_number=? AND chapter=? AND verse=?',
                    (KSIEGA, ROZDZIAL, v)).fetchone()
    print(f'{ROZDZIAL},{v}\n  GR {gr[:85]}\n  LA {(la[0][:85] if la else None)}')
PY
```

Przejrzyj **cały** rozdział, nie sam początek: łaciński werset łączący dwa
greckie stoi zwykle dalej, a do niego wszystko idzie równo. W Mk 4 pierwsze
czternaście wersetów odpowiada sobie jeden do jednego i rozjazd zaczyna się
dopiero przy końcu rozdziału.

Dla Marka cięcia są już zlokalizowane tą metodą i można je wziąć wprost:
łaciński **4,40** obejmuje grecki 4,40 i 4,41 (grecki 4,41 otwiera
καὶ ἐφοβήθησαν φόβον μέγαν — „i zlękli się lękiem wielkim", po łacinie
*et timuerunt timore magno*), więc cięcie idzie przed *et timuerunt*.
Rozdziały 8 i 9 mają rozjazd w drugą stronę — łacina ma tam werset więcej —
i trzeba je przejrzeć tą samą pętlą przed przebudową.

Po przebudowie sprawdź niezmiennik: **każdy werset grecki ma wiersz
łaciński**, a wierszy bez greki jest dokładnie tyle, ile pominięć tekstu
krytycznego.

## Krok 4: aparat i numeracja Euzebiusza

Aparat przepisuje się bez przeróbek — `browser/app.py` sam czyści z niego
HTML wewnętrznych odsyłaczy (`href="C:@1018 0"`). Klucz główny
`commentaries` to `(book, chapter_from, verse_from, marker)`, więc dwie noty
o tym samym znaku w jednym wersecie wysadzą `INSERT`. **Niech wysadzą** —
cicha utrata noty jest gorsza niż padnięty build.

Numerację Euzebiusza wyciąga się z nagłówków `NA28.commentaries` wyrażeniem
`Eusebian section/canon number:.*?<td>(\d+)</td>`.

## Krok 5: morfologia z MorphGNT, nigdy z Robinsona

Oba repozytoria trzymają morfologię w **zapisie dziesięcioznakowym MorphGNT**:
część mowy (2 znaki) plus kod fleksyjny (8 znaków), małymi literami —
`v-3iai-s--`, `n-----dsf-`, `ra----nsm-`. Pozycje: część mowy (0–1), osoba (2),
czas (3), strona (4), tryb (5), przypadek (6), liczba (7), rodzaj (8),
stopień (9). Plik MorphGNT podaje je rozdzielnie, więc kod bazy to po prostu
`(kolumna 2 + kolumna 3).lower()`.

Moduły interlinii (`01.sqlite`, Tischendorf, ph4) niosą kody **Robinsona**
(`V-PAI-3S`) i **nie są** źródłem morfologii. Robinsona na MorphGNT
przeliczyć się nie da bez zmyślania: nie odróżnia medium od strony biernej
w imiesłowach perfecti, więc jednemu `V-RPP-NSM` odpowiadają w Janie
zarówno `v--xppnsm-`, jak i `v--xmpnsm-`. Konwersja musiałaby wybrać jedno
i podać to z pozorem precyzji.

Zamiast przeliczać, bierz kody z samego MorphGNT:

```bash
MORPHGNT_DIR=/sciezka/do/kopii python3 tools/morphgnt_import.py \
    --db db.sqlite --book 480 --plik 62-Mk-morphgnt.txt
```

Parowanie idzie po znormalizowanej grece (bez akcentów, znaków aparatu,
nawiasów i wielkości liter) w dwóch przebiegach `difflib`: najpierw w obrębie
rozdziału, potem wersetu dla tego, czego pierwszy przebieg nie dosiągł.
Drugi przebieg jest potrzebny, bo bloki `difflib` pomijają pojedyncze zgodne
tokeny w otoczeniu różnic.

**Parowanie po treści, nie po indeksie.** MorphGNT idzie za tekstem SBLGNT,
baza za tekstem krytycznym NA, więc ciągi tokenów nie są identyczne.
Dopasowanie po pozycji wyglądałoby poprawnie do pierwszej różnicy i było
przesunięte wszędzie dalej — a przesunięta morfologia jest wiarygodna
w każdym miejscu i fałszywa w każdym. Dopasowanie po treści degraduje się
w **dziury**, które widać.

Spodziewane pokrycie: Mateusz 18 288 z 18 346 (99,68%), Jan 15 414 z 15 635
(98,59%). Tokenów bez pary **nie zgaduj i nie uzupełniaj ręcznie** — to
dokładnie te miejsca, gdzie wydania czytają inaczej: NA bierze słowo
w nawias edytorski, a SBLGNT je pomija (Mt 3,16 `[αὐτῷ]`, Mt 6,25
`ἢ τί πίητε`), albo różni się lekcja czy kolejność (Mt 2,14 `παρέλαβεν`,
Mt 5,4-5; Βηθζαθά w J 5,2 wobec Βηθεσδά).

Przełącznik `--zachowaj-istniejace` zostawia tokenom bez pary kod, który już
mają. Używa się go **tylko** przy bazie, która miała wcześniej poprawną
morfologię z innej edycji — tak jest w Janie, gdzie 221 tokenów trzyma kody
starszej edycji CCAT. Przy świeżej bazie nie ma czego zachowywać.

**Atrybucja jest wymagana.** MorphGNT: SBLGNT Edition, red. James K. Tauber,
<https://github.com/morphgnt/sblgnt>, DOI 10.5281/zenodo.376200 — analiza
morfologiczna na CC-BY-SA 3.0. Sam tekst SBLGNT ma odrębną licencję i **nie
wchodzi** do repozytorium: importujemy wyłącznie kody.

## Krok 6: weryfikuj produkt, nie kod wyjścia

Build, który przeszedł, nie znaczy, że dane są na miejscu. Lekcja z ligatur
RGreekL w Janie: brak kroju dawał `greek_rgreekl: null` we wszystkich 878
wersetach, nieskopiowany font w `site/` i `unknown font family` od Typsta —
a wszystkie trzy kroki kończyły się kodem 0 i Pages wdrażało się na zielono
bez ligatur.

Niezmienniki do sprawdzenia po przebudowie:

```bash
python3 - <<'PY'
import sqlite3
c = sqlite3.connect('file:db.sqlite?mode=ro', uri=True)
gs = {(a, b) for a, b in c.execute('SELECT DISTINCT chapter, verse FROM words')}
ls = {(a, b) for a, b in c.execute('SELECT chapter, verse FROM latin_verses')}
print('wersetów greckich', len(gs), '| wierszy łacińskich', len(ls))
print('greka bez łaciny (musi być puste):', sorted(gs - ls))
print('łacina bez greki (pominięcia tekstu krytycznego):', sorted(ls - gs))
print('słów bez morfologii:', c.execute("SELECT count(*) FROM words WHERE morphology=''").fetchone()[0])
print('długości kodów (musi być [10]):',
      sorted({len(m) for (m,) in c.execute("SELECT DISTINCT morphology FROM words WHERE morphology<>''")}))
print('kody Robinsona (wielkie litery; musi być 0):',
      c.execute("SELECT count(*) FROM words WHERE morphology GLOB '*[A-Z]*'").fetchone()[0])
print('słowa Jezusa:', c.execute('SELECT count(*) FROM words WHERE red=1').fetchone()[0])
PY
```

Potem obejrzyj **gotową stronę**, nie samo API: zbuduj próbną perykopę,
otwórz `/api/pericope?id=1` i sprawdź, czy przychodzą wszystkie cztery
warstwy — `interlinia` (z `strong`, `morphology`, `red`), `lacina`, `aparat`
i `greek_rgreekl` różne od `null`. Perykopę próbną potem usuń i przebuduj
bazę egzegezy od zera.

## Pułapki

**Moduł o właściwej nazwie bywa inną edycją.** `NA28.commentaries` to nie
`NA27ca.commentaries`, choć oba są „aparatem Nestle-Alanda". Różnica: 856
wierszy wobec 1528 dla Jana. Dowodź, nie zakładaj.

**Interlinia polska bywa przesunięta.** `03.sqlite` jest spłaszczoną
interlinią i granice słów odzyskano dopasowaniem; przy glosach
wielowyrazowych widać przesunięcia o jeden token. To zastany stan danych,
identyczny w Janie i Mateuszu — nie „naprawiaj" go ręcznie w pojedynczych
wersetach, bo rozjedziesz się z drugą księgą.

**Kropka a `·`.** Baza Jana ma w `words.text` kropkę zamienioną na ano teleia
(`λόγος·`), gotowe pliki `../na/*.sqlite` zostawiają kropkę. Nie ujednolicaj
wstecz — to widoczna różnica między księgami, ale nic od niej nie zależy.

**`footnote` i `references`.** `../na/db.sqlite` ma w `words` dodatkową
kolumnę `footnote` (111 przypisów tłumacza dla Jana) i całobiblijną tabelę
`references` (344 789 odsyłaczy). `../john/db.sqlite` ich **nie ma**
i `browser/app.py` ich nie czyta. Nie dokładaj ich bez potrzeby; przypisy
`[* …]` z `03.sqlite` są dostępne, jeśli kiedyś będą potrzebne.

**Polski cudzysłów wysadza parser Pythona.** Znak zamykający `„…"` to zwykłe
ASCII `"`, więc wewnątrz łańcucha w podwójnych cudzysłowach kończy łańcuch.
Wysadził parser przy pisaniu `db_tekst_build.py`. Treści z `„…"` pisz
w potrójnych apostrofach.

**`sed` i znak `#`.** Nie używaj `#` jako separatora `sed`, gdy wzorzec albo
zamiennik sam zawiera `#` — polecenie podmieni wtedy wcięcia w całym pliku.
Do podmian w kodzie używaj Pythona.

## Czego nie robić

- Nie przeliczaj kodów Robinsona na MorphGNT.
- Nie uzupełniaj ręcznie tokenów, które MorphGNT pominął.
- Nie generuj morfologii ani numerów Stronga „z głowy".
- Nie dopasowuj MorphGNT po indeksie tokenu — tylko po treści.
- Nie usuwaj wersetów łacińskich bez odpowiednika greckiego.
- Nie edytuj `db.sqlite` ręcznie — zmiany idą przez `make tekst`.
- Nie wciągaj tekstu SBLGNT do repozytorium; importuj same kody.
- Nie wierz kodowi wyjścia 0. Weryfikuj produkt.

## Checklist dla nowej księgi

- [ ] Numer księgi ustalony (`470` Mt, `480` Mk, `490` Lk, `500` J) i stała
      `KSIEGA_<NAZWA>` **przemianowana** w `db_tekst_build.py` i `browser/app.py`
- [ ] Sprawdzone, czy `../na/<ksiega>.sqlite` już istnieje
- [ ] Proweniencja aparatu i Wulgaty dowiedziona wobec księgi już obecnej
- [ ] Rozjazd Wulgaty zmierzony; cięcia znalezione przez porównanie treści
- [ ] MorphGNT zaimportowany; pokrycie odnotowane, dziury **nieuzupełnione**
- [ ] Niezmienniki przeszły: każdy werset grecki ma łacinę, kody mają 10 znaków,
      zero kodów z wielkimi literami
- [ ] Cztery warstwy widać na próbnej perykopie w `/api/pericope`
- [ ] Atrybucja MorphGNT w `README.md`
- [ ] Liczby (słowa, wersety, rozdziały, `red`, Wulgata, aparat) wpisane
      do `README.md`; `db.sqlite` **commitowany**, bo CI buduje z checkoutu
