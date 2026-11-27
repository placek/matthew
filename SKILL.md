---
name: perykopa
description: Dodanie nowej perykopy do bazy egzegezy Ewangelii Mateusza — pełna procedura, struktura danych i kryteria jakości. Użyj zawsze, gdy zadanie brzmi „dodaj perykopę", „opracuj Mt x,y-z", „kontynuuj egzegezę" albo dotyczy edycji istniejącej perykopy w data/*.json.
---

# Dodanie perykopy

## Zanim napiszesz pierwsze słowo

1. Przeczytaj `CLAUDE.md` (konwencje, uczciwość warsztatowa, pułapki)
   oraz `humanizer.md` — standard redakcyjny obowiązuje od pierwszego zdania,
   a nie dopiero przy korekcie.
2. Obejrzyj wzorzec. Dopóki Mateusz nie ma pierwszej domkniętej perykopy,
   miarą gęstości i tonu jest Prolog z repozytorium Jana:
   `python3 ../john/tools/export_pericope.py 1 /tmp/wzor.md`. Druga miara,
   krótsza: perykopa 7 (Kana). Gdy powstanie pierwsza perykopa Mateusza,
   ona przejmuje tę rolę i to jej trzeba dorównać.
3. Sprawdź, co już jest: `python3 -c "import sqlite3;
   [print(*r) for r in sqlite3.connect('data/egzegeza_mateusza.sqlite').execute('SELECT siglum,title,status FROM v_spis_perykop')]"`
4. Weź zakres perykopy **z tabeli delimitacji w `README.md`** — podział całej
   Ewangelii zapadł raz, przed pisaniem treści, i nie ustala się go osobno
   przy każdej perykopie. Jeśli uważasz, że granica jest zła, zgłoś to,
   zamiast przesuwać ją po cichu: zmiana pociąga odniesienia i klamry.

Uwaga o stanie prac: w repozytorium nie ma jeszcze żadnej perykopy ani
Wprowadzenia. Pierwsza perykopa jest więc zarazem ustaleniem wzorca dla
sześćdziesięciu dwóch następnych — nie zaczynaj masowej produkcji przed jej
domknięciem. Jeśli zadanie dotyczy innej księgi Pisma, kształt pracy zostaje
ten sam, ale repozytorium stawia się wedle `NOWA_KSIEGA.md`.

## Krok 1: gdzie mieszkają dane

Nie dotyka się kodu — dopisuje się dane. Perykopa jest wpisem w tablicy
`pericopes` jednego z plików `data/*.json`. Albo dołączasz ją do pliku
tematycznie bliskiego, albo tworzysz nowy plik (nazwa pliku stoi w tabeli
delimitacji) i dopisujesz go **na końcu** listy `PHASES`
w `tools/egzegeza_mateusza_build.py` oraz do `SOURCES` w `Makefile`.
Kolejność `PHASES` wyznacza identyfikatory wierszy, więc nigdy nie wstawiaj
pliku w środek listy.

Plik danych ma słownictwo współdzielone i listę perykop:

```jsonc
{
 "books":     [["Oz", "Księga Ozeasza", "ST", 28]],     // tylko NOWE księgi
 "verses":    {"chapter": 2, "items": [[15, "greka NA", "przekład roboczy"]]},
 "lexemes":   [["πληρόω", "pleroo", "czasownik", "wypełniać — dopełniać miary"]],
 "semitic":   [],                                       // terminy hbr/aram
 "lexeme_semitic": [], "occurrences": [], "works": [],
 "themes":    [["formuły wypełnienia", "opis motywu"]],  // tylko NOWE
 "pericopes": [ /* bundle, patrz Krok 2 */ ]
}
```

Przy pierwszej perykopie `books` musi zawierać samego Mateusza:
`["Mt", "Ewangelia według św. Mateusza", "NT", 47]`. Pozycje już istniejące
pomija `INSERT OR IGNORE` — nie dubluj leksemów i motywów. Sprawdź przed
dopisaniem: `SELECT lemma FROM lexeme` i `SELECT name FROM theme`.

## Krok 2: bundle perykopy

Klucze obowiązkowe: `pericope`, `intro`, `blocks`, `sections`, `refs`,
`patristic`, `textual`, `theme_links`. Opcjonalne: `struktura`
(renderowana jako podsekcja „Struktura całości" sekcji I), `section_viii`
(wstrzeliwana przed dwie ostatnie sekcje), `citations`, `revision_note`.

```jsonc
{
 "pericope": {"cs": 5, "vs": 1, "ce": 5, "ve": 16,
              "title": "Błogosławieństwa, sól i światło",
              "motto": "Beati pauperes spiritu (Szczęśliwi biedni duchem)",
              "status": "w_opracowaniu", "position": 9},

 "intro": "Akapit wprowadzający do sekcji I — umiejscowienie perykopy w kompozycji księgi i zapowiedź osi interpretacyjnej.",

 "blocks": [                      // sekcja I: tekst + analiza filologiczna
  {"cs": 5, "vs": 1, "ce": 5, "ve": 2,
   "label": "w. 1–2",
   "greek": "pełny tekst grecki bloku",
   "transl": "pełny przekład roboczy bloku",
   "units": [                     // [fraza grecka, tłumaczenie, akapit analizy]
    ["ἀνέβη εἰς τὸ ὄρος", "wszedł na górę",
     "Analiza: gramatyka, semantyka, tło semickie, powiązania wewnątrz Ewangelii. Jeden akapit = jedna myśl."]
   ]}
 ],

 // sekcje II–VIII + zakończenie + nota, ZAWSZE w tej kolejności i bez
 // numerów rzymskich w tytule (numery dokłada renderer):
 "sections": [
  {"type": "kontekst",     "title": "Kontekst historyczny, językowy, kulturowy i religijny",
   "body": "…", "children": []},
  {"type": "teologia",     "title": "Obserwacje teologiczne i filozoficzne w duchu tomistycznym",
   "body": "…", "children": []},
  {"type": "autor_ludzki", "title": "Autor ludzki: kim jest i co chce przekazać",
   "body": "…", "children": []},
  {"type": "autor_bozy",   "title": "Autor Boży: co Duch Święty chce przekazać",
   "body": "…", "children": []},
  {"type": "odniesienia",  "title": "Sieć odniesień biblijnych",
   "body": "…", "children": []},
  {"type": "recepcja",     "title": "Znaczenie w historii i liturgii Kościoła",
   "body": null,
   "children": [["Historia dogmatu", "…"], ["Liturgia", "…"]]},   // patrz niżej
  {"type": "patrystyka",   "title": "Komentarze Ojców Kościoła (catena patrum)",
   "body": "Jedno zdanie zapowiadające głosy kateny.", "children": []},
  {"type": "zakonczenie",  "title": "Zakończenie: intencja całości",
   "body": "…", "children": []},
  {"type": "nota",         "title": "Nota warsztatowa", "body": "…", "children": []}
 ],

 // [kotwica, księga, rozdz_od, w_od, rozdz_do, w_do, etykieta, relacja, uwaga]
 // kotwica: ["pericope"] | ["section", tytuł] | ["unit", etykieta_bloku, indeks]
 "refs": [
  [["pericope"], "Iz", 61, 1, 61, 3, "Iz 61,1–3", "aluzja", "ubodzy, pocieszenie płaczących"],
  [["unit", "w. 1–2", 0], "Wj", 19, 3, 19, 3, "Wj 19,3", "typologia", "Mojżesz wstępuje na górę — figura i wypełnienie"]
 ],

 // [etykieta_bloku, autor, tytuł_dzieła, locus, treść]
 "patristic": [
  ["w. 1–2", "św. Jan Chryzostom", "Homiliae in Matthaeum", "Hom. in Mt. 15",
   "Parafraza myśli Ojca — nie udawany cytat."]
 ],

 // [autor, locus, kotwica, uwaga, tytuł_dzieła]
 "citations": [
  ["św. Tomasz z Akwinu", "Super Mt., cap. V", ["section", "Obserwacje teologiczne i filozoficzne w duchu tomistycznym"],
   "Wykład błogosławieństw jako darów Ducha.", "Super Evangelium S. Matthaei lectura"]
 ],

 // [nr_wersetu, lemat, typ_problemu, świadkowie, ocena]  (albo 6 elem. z rozdziałem na początku)
 "textual": [[3, "πτωχοὶ τῷ πνεύματι", "wariant lekcji", "świadkowie wedle aparatu", "ocena"]],

 // [nazwa_motywu, kotwica]  — nazwa musi istnieć w bazie albo w "themes"
 "theme_links": [["królestwo niebios", ["block", "w. 3–12"]]],

 "revision_note": "Data i zakres rewizji — trafia do revision_log."
}
```

**Liturgia nie ma własnego klucza.** Tabelę `liturgical_use` usunięto ze
schematu w Janie w październiku 2026, bo rozjechała się z prozą i zaczęła jej
przeczyć. Recepcja liturgiczna jest **podsekcją sekcji VII** (`recepcja`):
ryty, sigla lekcjonarza, loci Godziny czytań i obrzędy wplatasz w akapit, nie
w wiersze tabeli. Przy obu tradycjach — rzymskiej i bizantyjskiej — pisz
osobno.

## Zapis greki i typografia

**Grekę pisz w formie złożonej (NFC).** Przydech ani akcent nie mogą stać
osobno przed literą. Kolumna grecka sekcji „Tekst perykopy" idzie krojem
ligaturowym RGreekL (`tools/rgreekl.py`), a enkoder normalizuje wejście do NFD
i samodzielny znak rozkłada mu się na spację z markami, **bez litery bazowej**
— przydech i cyrkumfleks przepadają. Pisz `Ἦν` (U+1F2E), nie `῏Ην`
(U+1FCF + Η). Dotyczy to `verses.items[*][1]`, `blocks[*].greek`
i `units[*][0]`.

W samym tekście źródłowym (`db.sqlite`) takie miejsca są trzy — `῏Η`
(U+1FCF) w Mt 27,55 i 27,61 oraz `῞Ω` (U+1FDE) w Mt 25,14 —
i `browser/app.py` składa je w locie (`_zloz_marki`), więc nic nie jest
zepsute. W danych perykop nowych nie dokładaj. Samodzielne `᾽` (koronis)
i `᾿` (psili) jako znak elizji — `δ᾽`, `ἀλλ᾽` — są poprawne i zostają;
problemem jest wyłącznie znak stojący **przed literą**.

**Nawiasy edytorskie** (`[ ]`, `( )`) zostają w tekście, ale pamiętaj,
że font ligaturowy mapuje `( )` na przydechy, a `[ ]` na litery, więc werset
idzie do API w odcinkach i nawiasy lądują poza krojem ligaturowym. To
obsłużone w kodzie; nie obchodź tego, zmieniając dane.

**Cudzysłowy.** Otwierający to `„` (U+201E), zamykający to **zwykły ASCII `"`**
(U+0022) — nie `”`. Liczba otwierających i zamykających w pliku musi się
zgadzać; niedomknięty cudzysłów to błąd danych, którego build nie złapie.

**Pauzy.** Em-pauza `—` dla wtrąceń, półpauza `–` w zakresach. Dywizu ze
spacjami nie wprowadzaj. Jedyne dywizy między cyframi to daty ISO w notach
rewizji.

**Przytoczenia są nienaruszalne.** Fragment w `„…"` dłuższy niż kilka słów to
przytoczony werset, formuła liturgiczna albo zdanie Ojca. Przepisuj go co do
słowa, razem z wielkością liter — zmiana `„na trzeci dzień…"` na
`„Na trzeci dzień…"` przy przebudowie zdania jest już przekłamaniem źródła.

**Zapis plików danych.** `json.dumps(obj, ensure_ascii=False, indent=1)` —
dokładnie to formatowanie, inaczej diff obejmie cały plik zamiast zmienionego
łańcucha.

## Krok 3: budowa i kontrola

```bash
make build                                               # baza od zera z data/*.json
python3 tools/export_pericope.py <id> /tmp/kontrola.md   # obejrzyj swoją perykopę
make export                                              # regeneracja egzegeza_mateusz1.md
```

Walidatora nie ma. Build łapie jedno: rozjazd etykiet bloków kończy się
`KeyError` (`patristic`, `refs` z kotwicą `unit`, `theme_links` z kotwicą
`block` muszą cytować `label` **znak w znak**, z półpauzą). Resztę sprawdź
grepem — półpauza w zakresach:

```bash
python3 -c "
import json,glob,re
for f in glob.glob('data/*.json'):
    t = open(f, encoding='utf-8').read()
    for m in re.finditer(r'(?<=\d)-(?=\d)', t):
        print(f, repr(t[m.start()-18:m.end()+10]))" | grep -v '20[0-9][0-9]-'
```

Sprawdź też zapis greki i cudzysłowy. W surowym JSON-ie cudzysłów zamykający
stoi jako `\"`, więc liczy się jego, nie goły znak:

```bash
python3 - <<'PY'
import glob, re
for f in sorted(glob.glob('data/*.json')):
    t = open(f, encoding='utf-8').read()
    for m in re.finditer(r'[\u1FBD\u1FBF\u1FCF\u1FDE](?=[^\W\d_])', t):
        print('greka niezlozona:', f, repr(t[m.start()-20:m.end()+12]))
    otw, zam = t.count('\u201e'), t.count(r'\"')
    if otw != zam:
        print('cudzyslowy niezbilansowane:', f, otw, '->', zam)
    for z, n in (('\u201d', 'obcy cudzyslow \u201d'), ('\u2019', 'obcy apostrof \u2019')):
        if z in t:
            print(n + ':', f)
PY
```

Grekę i przekład roboczy warto skolacjonować z tekstem źródłowym — on jest
w repozytorium i nie trzeba go zgadywać:

```bash
python3 - <<'PY'
import sqlite3
c = sqlite3.connect('file:db.sqlite?mode=ro', uri=True)
for ch, v in [(5, 3)]:
    gr = ' '.join(r[0] for r in c.execute(
        'SELECT text FROM words WHERE chapter=? AND verse=? ORDER BY position', (ch, v)))
    pl = ' '.join(r[0] for r in c.execute(
        'SELECT translation FROM words WHERE chapter=? AND verse=? ORDER BY position', (ch, v)))
    la = c.execute('SELECT text FROM latin_verses WHERE chapter=? AND verse=?', (ch, v)).fetchone()
    print(f'Mt {ch},{v}\n  GR {gr}\n  PL {pl}\n  LA {la[0] if la else "—"}')
PY
```

Znaki aparatu (`°`, `⸀`, `⸂`, `⸆`…) w `words.text` są częścią tekstu
źródłowego. W `blocks[*].greek` i `verses.items` przepisuj tekst **bez nich**,
chyba że świadomie chcesz je pokazać — przeglądarka i tak podświetla je
w interlinii, a noty aparatu bierze z tabeli `commentaries`.

## Kryteria jakości — sprawdź przed commitem

**Sekcja I.** Każdy blok ma grekę i przekład roboczy. Jednostki analizy
pokrywają frazy niosące ciężar teologiczny — nie każde słowo, lecz każde
ważne. Analiza mówi o gramatyce (czasy, tryby, rodzajniki, przypadki),
semantyce i tle semickim, nie tylko o „przesłaniu". Przy formułach
wypełnienia zawsze sprawdź, za którym tekstem idzie cytat: LXX, hebrajskim,
czy żadnym ze znanych.

**Sekcja II.** Konkret historyczny: realia, zwyczaje, archeologia, judaizm
Drugiej Świątyni, targumy, Qumran, literatura rabiniczna. U Mateusza ta
warstwa waży więcej niż u pozostałych synoptyków i nie wolno jej zbyć
ogólnikami o „ówczesnych czasach".

**Sekcja III.** Realna metafizyka Tomasza, nie pobożne uwagi z łacińską
wstawką: akt i możność, istota i istnienie, przyczynowość, uczestnictwo,
łaska i natura. Terminy łacińskie zawsze z tłumaczeniem.

**Sekcja IV** pyta o zamysł literacki i redakcyjny: kompozycja, klamry,
miejsce perykopy w jednej z pięciu mów albo w narracji między nimi, polemika
ze środowiskiem faryzejskim po 70 r. Gdzie redakcja Mateusza wobec Marka jest
widoczna i coś znaczy teologicznie, powiedz to — ale nie przy każdej
perykopie i nigdy jako popis źródłoznawstwa.

**Sekcja V** o sens dla Kościoła i czytelnika dzisiaj — bez kaznodziejstwa,
bez drugiej osoby liczby mnogiej.

**Sekcja VI.** Minimum 6–8 odniesień, każde z określoną relacją i uwagą
wyjaśniającą, na czym polega związek. Typologia wymaga wskazania figury
i wypełnienia.

**Sekcja VII.** Historia dogmatu (jeśli perykopa ważyła w sporach),
lekcjonarz, ikonografia, duchowość. Konkretne daty i nazwy. Podsekcja
liturgiczna jest jedynym miejscem recepcji liturgicznej w całej bazie, więc
musi nieść konkret: ryt, okazję i siglum lekcjonarza, a przy obu tradycjach
— rzymską i bizantyjską osobno. Gdzie Wschód czyta perykopę inaczej niż
Zachód, powiedz to wprost; gdzie związek ze świętem jest kalendarzowy albo
kaznodziejski, a nie lekcjonarzowy, też to powiedz — przemilczenie tej
różnicy było źródłem jedynego błędu faktograficznego, jaki baza Jana miała
w liturgii.

**Katena.** 3–4 głosy, każdy z innym akcentem — nie trzy warianty tej samej
myśli. Przypisz do bloku, którego realnie dotyczy. Przy Mateuszu pierwszym
wyborem jest Chryzostom (dziewięćdziesiąt homilii przez całą Ewangelię), dalej
Hieronim, Hilary i Orygenes; pełna lista z pułapkami atrybucji stoi
w `CLAUDE.md`. Nie przypisuj *Opus imperfectum in Matthaeum* Chryzostomowi
ani komentarza do Mateusza z PL 92 Bedzie — żadne z nich nie jest ich dziełem.

**Aparat.** Noty tekstualne tylko tam, gdzie aparat notuje realny problem.
Nie wymyślaj wariantów — świadków sprawdź w tabeli `commentaries`:

```bash
python3 -c "
import sqlite3
c = sqlite3.connect('file:db.sqlite?mode=ro', uri=True)
for r in c.execute('''SELECT verse_from, marker, substr(text,1,200) FROM commentaries
                      WHERE chapter_from=5 AND verse_from BETWEEN 1 AND 16'''):
    print(r)"
```

## Standard redakcyjny: wzorce pisania AI

Procedura stoi w `humanizer.md`; tu jest to, co wyszło z przebiegu po całej
Ewangelii Jana i czego nie widać, pisząc jedną perykopę.

**Najgroźniejszy jest szablon powtórzony między perykopami.** W Janie sekcję
zamykającą **22 perykop** otwierało to samo zdanie („Jeśli zebrać wszystko
w jedno zdanie:"). Pojedynczo brzmi nieszkodliwie, w książce jest to główna
oznaka maszyny. Jeśli łapiesz się na stałym otwarciu sekcji, zmień je. Przy
Mateuszu ryzyko jest większe niż przy Janie, bo perykop jest sześćdziesiąt
trzy, a mowy mają powtarzalną budowę — nie pozwól, by powtarzalność tekstu
przeszła w powtarzalność komentarza.

**Ten sam aforyzm nie może stać w trzech sekcjach.** W Kanie jedna puenta
wracała w sekcji IV, VII i VIII w trzech wariantach. Zostaw jedno
wystąpienie, w sekcji, do której należy.

**Nie zapowiadaj, że przejdziesz do sedna — przejdź.** Wypadają: „Warto
zauważyć, że…" i dwukropki zapowiadające własną kategorię („Epistemologia
sceny jest precyzyjna:"). Zdanie, które mówi tylko „to, co teraz powiem, jest
ważne", nie wnosi faktu.

**Antytezę „nie X, lecz Y" zostaw tam, gdzie koryguje błędne przekonanie.**
Jako rozstrzygnięcie merytoryczne jest w porządku; jako rytm w każdym
akapicie — nie.

**Powtórzenie wersetu kluczowego jest zamierzone.** Werset niosący perykopę,
wracający w intro, strukturze i zakończeniu, to klamra, nie wzorzec AI. Nie
ruszaj przytoczeń Pisma przy redakcji stylu.

Przy redakcji po fakcie chroń bezwzględnie: wyrażenia w pismach niełacińskich,
przytoczenia w `„…"` dłuższe niż kilka słów, kursywę (łacina i tytuły dzieł)
oraz sigla i liczby. Tekst po redakcji ma być **krótszy**, nie dłuższy.

## Czego nie robić

- Nie zmieniaj schematu bazy bez wyraźnej potrzeby — jeśli nowa warstwa
  danych nie mieści się w istniejących tabelach, najpierw zapytaj.
- Nie nadawaj statusu `ukonczona`.
- Nie przesuwaj granic perykopy wobec tabeli delimitacji w `README.md` bez
  zgłoszenia tego człowiekowi.
- Nie wstawiaj nowego pliku w środek listy `PHASES` — tylko na koniec.
- Nie inwestuj w sekcję „Nota warsztatowa": przeglądarka i PDF ją filtrują,
  wchodzi tylko do eksportu Markdown.
- Nie edytuj `data/egzegeza_mateusza.sqlite` ani `db.sqlite` — pierwsza
  powstaje z `data/*.json` przez `make build`, druga z modułów `../na` przez
  `make tekst`.
- Nie przeliczaj kodów Robinsona z `../na/db/` na MorphGNT i nie uzupełniaj
  ręcznie 58 słów, które zostają bez kodu — tam tekst NA różni się od SBLGNT.
- Nie przywracaj tabeli `liturgical_use` ani klucza `liturgy` w bundle'u.
- Nie dubluj leksemów ani motywów, które już są w bazie — sprawdź
  `SELECT lemma FROM lexeme` i `SELECT name FROM theme` przed dopisaniem.
- Nie parafrazuj polskich przekładów objętych prawem autorskim; przekład
  międzywierszowy z `db.sqlite` jest materiałem pomocniczym, nie tekstem do
  przepisywania.
- Nie dokładaj greki z samodzielnym przydechem przed literą (`῏Ην`) — enkoder
  ligatur gubi literę bazową. Pisz formę złożoną (`Ἦν`).
- Nie otwieraj sekcji zamykającej stałą formułą i nie powtarzaj tej samej
  puenty w kilku sekcjach.
- Nie puszczaj lokalnego modelu po korpusie „dla poprawy stylu". Próbowano
  tego na Janie w październiku 2026: przebieg spłaszczał autorską dykcję,
  rozdymał tekst o 6%, podnosił liczbę oznak AI i w leksemach **wymyślał
  grekę**. Narzędzie zostało usunięte z repozytorium.

## Na koniec

W podsumowaniu podaj: co powstało (liczby: bloki, jednostki, odniesienia,
katena), oś interpretacyjną perykopy, nowe motywy i leksemy — oraz
przypomnienie o weryfikacji loci patrystycznych przy źródłach.
