# Egzegeza Ewangelii według św. Mateusza — baza SQLite

Baza `egzegeza_mateusza.sqlite` przechowuje pełną egzegezę perykopa po
perykopie. Zakres docelowy: **cała Ewangelia, Mt 1,1–28,20**, w sześćdziesięciu
trzech perykopach. Stan dziś: maszyneria stoi, delimitacja jest zatwierdzona,
**Wprowadzenie napisane** (7 sekcji, 21 podsekcji), opracowanych jest
**dwanaście pierwszych perykop** (Mt 1,1–6,34, wszystkie w statusie `w_opracowaniu`).
Źródło samego tekstu (`db.sqlite`) jest kompletne.

Repozytorium powstało na wzór `../john` wedle procedury z `NOWA_KSIEGA.md`.
Kształt pracy nad perykopą opisuje `SKILL.md` i jest on dla obu ksiąg ten sam.

## Układ repozytorium

Dane są oddzielone od narzędzi — pliki `.json` przechowują całą treść, a
skrypty w `tools/` są **wyłącznie** narzędziami, które z nich budują bazę.

```
data/                     ← źródła (pod kontrolą wersji)
  schema.sql              schemat bazy (DDL, warstwy 1–8)
  wprowadzenie.json       Wprowadzenie do całej księgi (meta + intro_section)
  <slug>.json             perykopy — nazwy plików w tabeli na końcu
  REVIEW_LOG.md           dziennik recenzji naukowej, wiersz na plik
  egzegeza_mateusza.sqlite  baza generowana (make build; poza gitem)
tools/
  egzegeza_mateusza_build.py  buduje data/egzegeza_mateusza.sqlite z data/*.json
  db_tekst_build.py       buduje db.sqlite — źródło tekstu (make tekst)
  export_pericope.py      regeneruje Markdown perykopy z bazy
  export_typst.py         baza → Typst → PDF
  export_site.py          baza → site/ (wersja statyczna dla GitHub Pages)
  rgreekl.py              enkoder ligatur RGreekL
browser/
  app.py                  backend (serwer + API, biblioteka standardowa)
  index.html              interfejs przeglądarki
db.sqlite                 źródło tekstu Ewangelii (greka, polski, Wulgata, aparat)
Makefile                  make build | serve | export | site | typst | pdf | tekst | clean
```

## Źródło tekstu: `db.sqlite`

W korzeniu leży `db.sqlite` — **źródło prawdy dla samego tekstu** Ewangelii
(Mateusz ma w nim numer księgi `470`):

| tabela | wiersze | zawartość |
|---|---|---|
| `words` | 18 346 | interlinia grecko-polska słowo po słowie: `text` (greka wraz ze znakami aparatu), `translation` (polski odpowiednik), `strong`, `morphology` oraz **`red`** — znacznik słów Jezusa (*verba Christi*), 10 426 słów |
| `latin_verses` | 1071 | Wulgata klementyńska, werset po wersecie — trzecia kolumna tekstu paralelnego; kolumna `eusebeios` niesie numerację Euzebiusza (345 wersetów) |
| `commentaries` | 1425 | aparat krytyczny Nestle-Aland, powiązany ze znakami (`marker`) wplecionymi w tekst grecki |

Tekst liczy 1068 wersetów z greką w 28 rozdziałach. Trzy wiersze łacińskie
(Mt 17,21; 18,11; 23,14) nie mają odpowiednika greckiego, bo tekst krytyczny
tych wersetów nie zawiera — zostają w bazie jak J 5,4 w bazie Jana.

### Czym to różni się od bazy Jana

`db.sqlite` Jana leżał w repozytorium jako gotowy plik binarny bez skryptu,
który by go odtwarzał, i `NOWA_KSIEGA.md` nazywa go „najdroższym elementem
całego przedsięwzięcia". Tutaj jest odtwarzalny — `make tekst` składa go
z modułów projektu `../na`:

| tabela | źródło |
|---|---|
| `words` | `../na/mt.sqlite` — produkt pipeline'u z `../na/db/`: tekst grecki wraz ze znakami aparatu z `02.sqlite` (Nestle-Aland z aparatem), numery Stronga i kody gramatyczne z `01.sqlite` (*A Reader's Greek New Testament*), przekład międzywierszowy z `03.sqlite` (Popowski-Wojciechowski), `red` naniesiony osobno |
| `latin_verses` | moduł `CVUL` (Wulgata klementyńska) z normalizacją spacji i przedzieleniem Mt 17 na granice wersetów greckich |
| `commentaries` | moduł `NA27ca.commentaries` — ten sam aparat, który stoi w bazie Jana (tam 1528 wierszy dla księgi 500) |
| `morphology` | MorphGNT, edycja SBLGNT — `tools/morphgnt_import.py` nadpisuje kody Robinsona z `01.sqlite` (patrz niżej) |
| `eusebeios` | nagłówki modułu `NA28.commentaries` |

**Mt 17 wymaga uwagi.** Wulgata klementyńska dzieli ten rozdział inaczej niż
tekst krytyczny: łaciński w. 14 obejmuje grecki 14 i 15 (grecki 15 otwiera
καὶ λέγων — „i mówiąc", po łacinie *dicens*), a od tego miejsca numeracja
łacińska idzie o jeden w tył. `db_tekst_build.py` przecina łaciński w. 14
przed *dicens:* i przesuwa resztę rozdziału; poza Mt 17 numeracje się
pokrywają. Po przebudowie każdy werset grecki ma swój wiersz łaciński.

### Kody gramatyczne: MorphGNT w obu księgach

Morfologia stoi w zapisie **dziesięcioznakowym MorphGNT** — część mowy (2 znaki)
plus kod fleksyjny (8 znaków), małymi literami: `v-3pai-s--`, `n-----dsf-`,
`ra----nsm-`. Ten sam zapis ma baza Jana, więc `browser/index.html` i
`export_typst.py` są w obu repozytoriach identyczne.

Moduły w `../na/db/` niosą kody **Robinsona** (`V-PAI-3S`), więc nie są
źródłem morfologii: przeliczenie Robinsona na MorphGNT jest niemożliwe bez
zmyślania, bo Robinson nie odróżnia medium od strony biernej w imiesłowach
perfecti (`V-RPP-NSM` odpowiada w Janie zarówno `v--xppnsm-`, jak i
`v--xmpnsm-`). Zamiast przeliczać, kody bierzemy z samego MorphGNT:
`tools/morphgnt_import.py` paruje tokeny po znormalizowanej grece (bez
akcentów, znaków aparatu, nawiasów i wielkości liter) w dwóch przebiegach
`difflib` — najpierw w obrębie rozdziału, potem wersetu.

MorphGNT idzie za tekstem SBLGNT, a `db.sqlite` za tekstem krytycznym NA, więc
pokrycie nie jest pełne: **18 288 z 18 346 słów (99,68%)** dostaje kod,
a 58 tokenów zostaje bez niego. To dokładnie te miejsca, gdzie wydania czytają
inaczej — NA bierze słowo w nawias edytorski, a SBLGNT je pomija (Mt 3,16
`[αὐτῷ]`, Mt 6,25 `ἢ τί πίητε`), albo różni się lekcja czy kolejność
(Mt 2,14 `παρέλαβεν`, Mt 5,4-5). Tokenów bez pary **nie zgadujemy**: kod
MorphGNT byłby tam wymysłem, a `opiszMorfologie()` po prostu nic nie pokaże.
Robinson zostaje w `../na/mt.sqlite` i jest o jedno `make tekst` stąd, więc nic
nie przepada.

`make tekst` pobiera plik MorphGNT z GitHuba; `MORPHGNT_DIR` wskazuje lokalną
kopię, a `MORPHGNT_WERSJA` wybiera wydanie (domyślnie 6.12). Tekst SBLGNT
**nie wchodzi** do repozytorium — bierzemy wyłącznie kody.

**Atrybucja.** MorphGNT: SBLGNT Edition, red. James K. Tauber, wersja 6.12,
<https://github.com/morphgnt/sblgnt>, DOI 10.5281/zenodo.376200. Analiza
morfologiczna i lematyzacja na licencji CC-BY-SA 3.0; sam tekst SBLGNT podlega
odrębnej licencji SBLGNT i w tej bazie nie występuje.

Baza egzegetyczna (`data/egzegeza_mateusza.sqlite`) pozostaje magazynem
**komentarza** — analiz, kateny, aparatu autorskiego i odniesień; tekst do
prezentacji bierzemy z `db.sqlite`. W sekcji „Analiza wers po wersie"
przeglądarka wykorzystuje warstwy `words` oraz `commentaries`:

- **interlinia** — greka nad polskim odpowiednikiem, słowa Jezusa czerwienią;
- **Strong i morfologia** — kliknięcie (lub Enter na zaznaczonym) słowa otwiera
  okienko z formą grecką, znaczeniem, numerem Stronga (odsyłacz do konkordancji)
  i **rozwiniętym po polsku** kodem morfologicznym: `v--papnsm-` czyta się jako
  „czasownik · praesens · strona czynna · imiesłów · mianownik · liczba
  pojedyncza · rodzaj męski";
- **aparat** — wpisy z `commentaries` przypięte do wersetów bloku; znaki
  aparatu (`°`, `⸀`, `⸂`…) są podświetlone również wewnątrz greki interlinii, więc
  widać, do którego słowa odnosi się dana nota.

## Warstwy schematu

Schemat jest skopiowany z bazy Jana **bez zmian** — osiem warstw jest
niezależne od księgi.

0. **Wprowadzenie**: `intro_section` (+ klucze `intro_*` w `meta`) — otwiera
   przeglądarkę (strona domyślna `#wprowadzenie`) i PDF (pierwszy rozdział)
1. **Kanon**: `book`, `verse` (tekst grecki + przekład roboczy per werset)
2. **Perykopa**: `pericope` (zakres, tytuł, motto, status opracowania)
3. **Komentarz**: `section` (drzewo sekcji I–VII), `commentary_block` (zakres
   wersetów, np. „w. 6–8"), `analysis_unit` (fraza grecka + akapit analizy —
   najmniejszy klocek egzegezy)
4. **Słowniki wielokrotnego użytku**: `lexeme` (βασιλεία, δικαιοσύνη…),
   `semitic_term` (malkuta, cedaka…), `lexeme_semitic` (podwójne dno
   grecko-semickie), `lexeme_occurrence` (mapa wystąpień słów-kluczy)
5. **Aparat**: `scripture_ref` (odniesienia z typem relacji), `textual_note`
   (warianty i interpunkcja), `work` + `citation` (autorzy i dzieła)
6. **Katena patrystyczna**: `patristic_comment` — komentarz Ojca Kościoła
   (work + locus + treść) przypięty do bloku wersetowego; widok `v_catena`;
   sekcja VIII w eksporcie składa się z tej tabeli automatycznie
7. **Przekroje**: `theme` + `theme_link` (nici tematyczne przez całą księgę)
8. **Warsztat**: `meta`, `revision_log`, triggery `updated_at`, FTS5

## Otwieranie

- CLI: `sqlite3 data/egzegeza_mateusza.sqlite` (na tym środowisku:
  `python3 -c "import sqlite3..."`)
- GUI: DBeaver, DB Browser for SQLite, Datasette
  (`datasette data/egzegeza_mateusza.sqlite`)

## Wyszukiwanie pełnotekstowe

```sql
SELECT entity, entity_id, snippet(fts_tresc, 0, '[', ']', '…', 12)
FROM fts_tresc WHERE fts_tresc MATCH 'Szechina';
```

Uwaga: `remove_diacritics` w FTS5 zdejmuje tylko diakrytykę łacińską (ó, é…).
Grekę, hebrajski i polskie „ł" wyszukuj w pełnym zapisie: `MATCH 'βασιλεία'`,
`MATCH 'światłość'`. Triggery synchronizują FTS automatycznie przy każdej
zmianie w `analysis_unit`, `section`, `commentary_block`, `lexeme`.

## Przykładowe zapytania

```sql
-- spis perykop z licznikami
SELECT * FROM v_spis_perykop;

-- pełna analiza w. 3: frazy i treść
SELECT u.phrase_greek, u.body_md
FROM analysis_unit u JOIN commentary_block b ON b.id = u.block_id
WHERE b.label = 'w. 3' ORDER BY u.position;

-- mapa semantyczna słowa-klucza
SELECT * FROM v_leksykon WHERE lemma = 'βασιλεία';

-- wszystkie typologie ST dla perykopy
SELECT target_label, note_md FROM scripture_ref
WHERE pericope_id = 1 AND relation = 'typologia';
```

## Dodawanie kolejnej perykopy

Nie dotyka się kodu — dopisuje się dane. Pełna procedura: `SKILL.md`.

1. Utwórz `data/<slug>.json` wedle tabeli delimitacji i dopisz jego nazwę
   **na końcu** listy `PHASES` w `tools/egzegeza_mateusza_build.py` oraz do
   `SOURCES` w `Makefile`. Kolejność `PHASES` wyznacza identyfikatory wierszy,
   więc nigdy nie wstawiaj pliku w środek listy.
2. `make build` — przebuduj bazę od zera z `data/*.json`.
3. `python3 tools/export_pericope.py 1 /tmp/kontrola.md` — kontrola.

Struktura pojedynczej perykopy (`bundle`): `pericope`, `intro` (sekcja I),
`blocks` (z `units`), `sections` (II…), `refs`, `patristic`, `textual`,
`theme_links`; opcjonalnie `struktura`, `section_viii`, `citations`,
`revision_note`.

Status perykopy (`szkic` → `w_opracowaniu` → `ukonczona` → `do_rewizji`)
i `revision_log` służą do prowadzenia pracy na lata. Status `ukonczona`
nadaje wyłącznie człowiek po weryfikacji przy źródłach.

## Katena — przykładowe zapytania

```sql
-- wszyscy Ojcowie komentujący w. 3
SELECT autor, locus, body_md FROM v_catena WHERE blok = 'w. 3';

-- wszystkie komentarze Chryzostoma w całej bazie
SELECT blok, locus, body_md FROM v_catena WHERE autor = 'św. Jan Chryzostom';

-- pełnotekstowo po katenie
SELECT snippet(fts_tresc,0,'[',']','…',12) FROM fts_tresc
WHERE fts_tresc MATCH 'sprawiedliwość' AND entity = 'patristic_comment';
```

## Delimitacja: 63 perykopy

Podział całej Ewangelii na perykopy jest decyzją kompozycyjną, nie techniczną,
i wedle `NOWA_KSIEGA.md` zapada **przed** pisaniem treści — zmiana w połowie
pracy oznacza przepisywanie odniesień i klamer. Poniższy podział został
**zatwierdzony 27 XI 2026** i jest od tej chwili wiążący: zakresy są ciągłe
i rozłączne, pokrywają Mt 1,1–28,20 i wszystkie 1068 wersetów, mediana
długości perykopy to 16 wersetów (u Jana 45 perykop na 878 wersetów).
Granicę perykopy wolno przesunąć tylko po uzgodnieniu z człowiekiem.

Trzy części idą za formułą **ἀπὸ τότε ἤρξατο ὁ Ἰησοῦς** (od tego czasu zaczął
Jezus) w Mt 4,17 i 16,21 — szwem, który zaznacza sam ewangelista. Granice padają
w środku rozdziału, dlatego przeglądarka i eksport Typst grupują perykopy po
parze rozdział-werset, nie po samym rozdziale. Pięć wielkich mów (Mt 5–7;
10; 13; 18; 24–25), zamykanych formułą καὶ ἐγένετο ὅτε ἐτέλεσεν ὁ Ἰησοῦς
(i stało się, gdy skończył Jezus), rozkłada się wewnątrz tych części; mowy
dłuższe są dzielone po wewnętrznych szwach, nie po równej liczbie wersetów.

Kolumna „Status" wypełnia się dopiero wraz z plikiem danych.

### Osoba Mesjasza (Mt 1,1–4,16)

| # | Siglum | Tytuł | Plik danych | Status |
|---|---|---|---|---|
| 1 | Mt 1,1–17 | Rodowód Jezusa Chrystusa | `rodowod.json` | w_opracowaniu |
| 2 | Mt 1,18–25 | Narodzenie Jezusa i imię Emmanuel | `narodzenie.json` | w_opracowaniu |
| 3 | Mt 2,1–12 | Magowie ze Wschodu | `magowie.json` | w_opracowaniu |
| 4 | Mt 2,13–23 | Ucieczka do Egiptu, rzeź niewiniątek i Nazaret | `egipt.json` | w_opracowaniu |
| 5 | Mt 3,1–12 | Jan Chrzciciel na pustyni | `chrzciciel.json` | w_opracowaniu |
| 6 | Mt 3,13–17 | Chrzest Jezusa | `chrzest.json` | w_opracowaniu |
| 7 | Mt 4,1–16 | Kuszenie na pustyni i powrót do Galilei | `kuszenie.json` | w_opracowaniu |

### Głoszenie Królestwa (Mt 4,17–16,20)

| # | Siglum | Tytuł | Plik danych | Status |
|---|---|---|---|---|
| 8 | Mt 4,17–25 | Początek nauczania i pierwsi uczniowie | `poczatek.json` | — |
| 9 | Mt 5,1–16 | Błogosławieństwa, sól i światło | `blogoslawienstwa.json` | — |
| 10 | Mt 5,17–48 | Wypełnienie Prawa i antytezy | `prawo.json` | — |
| 11 | Mt 6,1–18 | Jałmużna, modlitwa Pańska i post | `sprawiedliwosc.json` | — |
| 12 | Mt 6,19–34 | Skarb w niebie i troska o życie | `skarb.json` | — |
| 13 | Mt 7,1–12 | Nie sądźcie; proście | `sad.json` | — |
| 14 | Mt 7,13–29 | Ciasna brama, owoce i dom na skale | `brama.json` | — |
| 15 | Mt 8,1–17 | Trędowaty, sługa setnika i teściowa Piotra | `uzdrowienia.json` | — |
| 16 | Mt 8,18–27 | Koszt naśladowania i burza na jeziorze | `nasladowanie.json` | — |
| 17 | Mt 8,28 – 9,8 | Opętani z Gadary i paralityk | `gadareni.json` | — |
| 18 | Mt 9,9–17 | Powołanie Mateusza, post i nowe wino | `mateusz.json` | — |
| 19 | Mt 9,18–34 | Córka przełożonego, krwotok, niewidomi i niemy | `corka.json` | — |
| 20 | Mt 9,35 – 10,15 | Żniwo, wybór Dwunastu i mowa misyjna | `zniwo.json` | — |
| 21 | Mt 10,16–42 | Prześladowania, wyznanie i miecz | `przesladowania.json` | — |
| 22 | Mt 11,1–19 | Posłowie Chrzciciela i świadectwo o nim | `poslowie.json` | — |
| 23 | Mt 11,20–30 | Biada miastom i jarzmo łagodne | `jarzmo.json` | — |
| 24 | Mt 12,1–21 | Spory o szabat i Sługa Pański | `szabat.json` | — |
| 25 | Mt 12,22–50 | Beelzebul, znak Jonasza i prawdziwa rodzina | `beelzebul.json` | — |
| 26 | Mt 13,1–23 | Przypowieść o siewcy i cel przypowieści | `siewca.json` | — |
| 27 | Mt 13,24–43 | Chwast, ziarno gorczycy i zaczyn | `chwast.json` | — |
| 28 | Mt 13,44–52 | Skarb, perła, sieć i nowe ze starym | `perla.json` | — |
| 29 | Mt 13,53 – 14,12 | Odrzucenie w Nazarecie i śmierć Chrzciciela | `nazaret.json` | — |
| 30 | Mt 14,13–21 | Rozmnożenie chlebów | `rozmnozenie.json` | — |
| 31 | Mt 14,22–36 | Kroczenie po jeziorze | `chodzenie.json` | — |
| 32 | Mt 15,1–20 | Tradycja starszych i to, co czyni nieczystym | `tradycja.json` | — |
| 33 | Mt 15,21–39 | Kananejka i drugie rozmnożenie | `kananejka.json` | — |
| 34 | Mt 16,1–12 | Żądanie znaku i kwas faryzeuszów | `znak.json` | — |
| 35 | Mt 16,13–20 | Wyznanie Piotra w Cezarei Filipowej | `cezarea.json` | — |

### Męka i zmartwychwstanie (Mt 16,21–28,20)

| # | Siglum | Tytuł | Plik danych | Status |
|---|---|---|---|---|
| 36 | Mt 16,21–28 | Pierwsza zapowiedź męki i warunki naśladowania | `zapowiedz.json` | — |
| 37 | Mt 17,1–13 | Przemienienie | `przemienienie.json` | — |
| 38 | Mt 17,14–27 | Epileptyk, druga zapowiedź i podatek na świątynię | `epileptyk.json` | — |
| 39 | Mt 18,1–14 | Najmniejszy w Królestwie i zgubiona owca | `najmniejszy.json` | — |
| 40 | Mt 18,15–35 | Upomnienie braterskie i nielitościwy dłużnik | `upomnienie.json` | — |
| 41 | Mt 19,1–15 | Nierozerwalność małżeństwa, bezżeństwo i dzieci | `malzenstwo.json` | — |
| 42 | Mt 19,16–30 | Bogaty młodzieniec i nagroda | `bogaty.json` | — |
| 43 | Mt 20,1–16 | Robotnicy w winnicy | `robotnicy.json` | — |
| 44 | Mt 20,17–34 | Trzecia zapowiedź, synowie Zebedeusza i niewidomi | `zebedeusz.json` | — |
| 45 | Mt 21,1–17 | Wjazd do Jerozolimy i oczyszczenie świątyni | `wjazd.json` | — |
| 46 | Mt 21,18–32 | Figowiec, pytanie o władzę i dwaj synowie | `figowiec.json` | — |
| 47 | Mt 21,33–46 | Przewrotni rolnicy | `winnica.json` | — |
| 48 | Mt 22,1–14 | Uczta królewska | `uczta.json` | — |
| 49 | Mt 22,15–46 | Podatek, zmartwychwstanie, przykazanie i Syn Dawida | `pytania.json` | — |
| 50 | Mt 23,1–39 | Biada uczonym w Piśmie i faryzeuszom | `biada.json` | — |
| 51 | Mt 24,1–28 | Zburzenie świątyni i wielkie utrapienie | `zburzenie.json` | — |
| 52 | Mt 24,29–51 | Przyjście Syna Człowieczego i czujność | `przyjscie.json` | — |
| 53 | Mt 25,1–30 | Dziesięć panien i talenty | `panny.json` | — |
| 54 | Mt 25,31–46 | Sąd Ostateczny: owce i kozły | `owce.json` | — |
| 55 | Mt 26,1–16 | Namaszczenie w Betanii i zdrada Judasza | `namaszczenie.json` | — |
| 56 | Mt 26,17–35 | Ostatnia Wieczerza | `wieczernik.json` | — |
| 57 | Mt 26,36–56 | Getsemani i pojmanie | `getsemani.json` | — |
| 58 | Mt 26,57–75 | Przed Sanhedrynem i zaparcie się Piotra | `sanhedryn.json` | — |
| 59 | Mt 27,1–26 | Koniec Judasza i proces przed Piłatem | `pilat.json` | — |
| 60 | Mt 27,27–56 | Ukrzyżowanie i śmierć | `golgota.json` | — |
| 61 | Mt 27,57–66 | Pogrzeb i straż u grobu | `pogrzeb.json` | — |
| 62 | Mt 28,1–15 | Pusty grób i przekupieni strażnicy | `grob.json` | — |
| 63 | Mt 28,16–20 | Rozesłanie uczniów | `rozeslanie.json` | — |

## Aplikacja webowa

```bash
make serve              # startuje na http://localhost:8008
make serve PORT=9000    # inny port
# równoważnie: PORT=9000 python3 browser/app.py
```

Bez zależności zewnętrznych — tylko biblioteka standardowa Pythona; baza
otwierana w trybie tylko do odczytu (`mode=ro`), więc przeglądanie nie może
uszkodzić danych. Zatrzymanie: Ctrl+C. Port ustawia zmienna `PORT`
(domyślnie 8008 — Jan stoi na 8007, więc oba serwery mogą działać obok
siebie). Jeśli baza nie istnieje, uruchom najpierw `make build`.

**Co jest w interfejsie**

Perykopa jest jednym ciągłym dokumentem (bez zakładek), ułożonym tak, jak się ją
czyta — od tekstu do szczegółu:

1. **Tekst perykopy** — trzy kolumny *paralelnie*, werset przy wersecie:
   greka, przekład roboczy i **Wulgata** (z `latin_verses`), z numeracją
   na marginesie (perykopy przekraczające granicę rozdziałów dostają znaczniki
   rozdziału i numery w postaci `9,8`). Kolumnę łacińską można schować
   przyciskiem; wybór pamięta się między perykopami
2. **Komentarz** — „Struktura całości" oraz sekcje II–VII z podsekcjami
   i zakończenie; sekcję „Nota warsztatowa" przeglądarka filtruje (tak samo
   PDF — wchodzi tylko do eksportu Markdown)
3. **Ojcowie Kościoła** — katena z autorem, dziełem, miejscem (locus) i blokiem
   wersetowym, którego dotyczy
4. **Analiza wers po wersie** — blok po bloku: **interlinia** grecko-polska
   z `db.sqlite` (nad każdym słowem greka, pod nim polski odpowiednik; słowa
   Jezusa na czerwono, kliknięcie słowa otwiera Stronga i morfologię po
   polsku), pod nią przekład ciągły, jednostki analizy frazowej, *leksykon*
   słów-kluczy tego bloku, *aparat* z `commentaries` oraz autorskie
   *noty tekstualne* przypisane do jego wersetów
5. **Odniesienia i motywy** — tabela odniesień biblijnych i motywy przekrojowe

Do tego: lewa kolumna z listą perykop pogrupowaną w trzy części Ewangelii,
przyklejony spis części (podświetla sekcję, którą właśnie czytasz), górne
przyciski *Leksykon* i *Motywy*, tryb ciemny wedle ustawień systemu, układ
responsywny (na wąskim ekranie greka staje nad przekładem) i arkusz do druku.
Wyszukiwarka u góry działa pełnotekstowo po FTS5 (analizy, sekcje, katena,
leksykon); kliknięcie wyniku otwiera perykopę. Grekę i „ł" wpisuj w pełnym
zapisie.

**Punkty API** (przydatne przy własnych narzędziach):
`/api/pericopes`, `/api/pericope?id=N`, `/api/search?q=…`, `/api/lexicon`, `/api/themes`
— wszystkie zwracają JSON.

## Kroje greckie i ligatury RGreekL

Greka stoi w dwóch krojach. Kolumna grecka sekcji „Tekst perykopy" idzie
krojem **RGreekL** (`rgreek.ttf`, rodzina `Rgreekl2`), który rysuje ligatury
rękopiśmienne; cała pozostała greka — interlinia, leksykon, analiza, aparat —
zostaje na **New Athena Unicode** (`newathu.ttf`).

RGreekL nie przyjmuje Unicode: tekst trzeba zakodować na znaki z zakresów
łacińskich, które wyglądają jak greka dopiero pod tym krojem. Robi to
`tools/rgreekl.py`, wciągany jako moduł przez `browser/app.py`, i wynik idzie
do API jako `greek_rgreekl` — lista odcinków `{lig, text}`. Odcinki `lig=false`
to nawiasy edytorskie, które muszą zostać poza krojem ligaturowym, bo ten
font mapuje `( )` na przydechy, a `[ ]` na litery.

Silnik i krój **leżą w repozytorium**, bo GitHub Actions buduje stronę i PDF
z samego checkoutu. Trzymane obok repo były dla runnera niewidoczne i ligatury
cicho znikały: `greek_rgreekl` schodziło do `null`, `rgreek.ttf` nie trafiał
do `site/`, a `typst` wypisywał `unknown font family: Rgreekl2` i kończył
sukcesem — Pages wdrażało się na zielono bez ligatur. Ścieżkę nadal nadpisuje
`RGREEKL_DIR`; gdy silnika nie ma, pole jest `null` i rysuje się zwykła greka
Unicode, a build, `site` i `pdf` przechodzą.

W tekście Mateusza stoją trzy miejsca z diakrytykiem pisanym osobno przed
wielką literą: `῏Η` (U+1FCF) w Mt 27,55 i 27,61 oraz `῞Ω` (U+1FDE) w Mt 25,14.
Enkoder normalizuje wejście do NFD i taki znak rozkłada mu się na spację
z markami, bez litery bazowej, więc `browser/app.py` składa je w locie
(`_zloz_marki`). W **danych perykop** pisz zawsze formę złożoną (NFC).

**Licencja.** RGreekL jest freeware Vernona E. Kooya: wolno go rozprowadzać
i osadzać w dokumencie, nie wolno modyfikować **ani używać komercyjnie** —
szczegóły w `rgreek.ttf.LICENSE`. Przy płatnej publikacji trzeba go zastąpić
albo uzyskać zgodę autora. `newathu.ttf` ma własne, odrębne warunki.

## GitHub Pages (wersja statyczna)

GitHub Pages nie uruchomi Pythona, więc przeglądarkę publikuje się w wersji
statycznej: `make site` woła `tools/export_site.py`, który importuje
`browser/app.py` i zamienia każdy endpoint API w plik JSON w `site/api/`
(perykopy, leksykon, motywy oraz `szukaj.json` — indeks dla wyszukiwarki
działającej wtedy po stronie przeglądarki, bez FTS5). Kopiowany
`index.html` dostaje atrybut `data-static` i sam przełącza się na pliki.

Publikacją zajmuje się workflow `.github/workflows/pages.yml`: przy każdym
pushu na `master` buduje bazę, generuje `site/` i wdraża na Pages.
Jednorazowo trzeba włączyć w repozytorium:
**Settings → Pages → Build and deployment → Source: „GitHub Actions"**.

Workflow buduje wyłącznie z checkoutu, więc `db.sqlite` jest **commitowany**
(2,7 MB) — modułów źródłowych, z których go składa `make tekst`, na runnerze
nie ma.

Podgląd lokalny wersji statycznej: `make site && python3 -m http.server -d site 8001`.
