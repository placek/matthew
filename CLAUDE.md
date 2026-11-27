# Egzegeza Ewangelii według św. Mateusza

Baza SQLite z pełną egzegezą perykopa po perykopie. Docelowo: książka
i przeszukiwalna baza analizy wersetów. Język pracy i wszystkich treści:
**polski**.

Repozytorium postawiono na wzór `../john` wedle `NOWA_KSIEGA.md`. Schemat,
narzędzia i przeglądarka są przeniesione bez zmian merytorycznych; różnice
dotyczą księgi, nie kształtu pracy.

## Zasada naczelna

Ten projekt to **warsztat teologiczny, nie generator tekstu**. Każda
perykopa dostaje osiem warstw analizy (I–VIII) i katenę Ojców. Objętość
nie jest celem — celem jest gęstość: każde zdanie ma nieść filologię,
kontekst albo teologię. Jeśli akapit da się skreślić bez straty, skreśl.

## Struktura repozytorium

```
data/*.json                   # ŹRÓDŁO PRAWDY treści egzegetycznej
data/schema.sql               # schemat bazy (warstwy 1–8)
data/egzegeza_mateusza.sqlite # baza (produkt make build; regenerowalna od zera)
data/REVIEW_LOG.md            # dziennik recenzji naukowej, wiersz na plik
db.sqlite                     # ŹRÓDŁO PRAWDY tekstu (greka, polski, Wulgata, aparat)
tools/egzegeza_mateusza_build.py  # budowa bazy egzegezy z data/*.json
tools/db_tekst_build.py       # budowa db.sqlite z modułów ../na (make tekst)
tools/export_pericope.py      # baza -> Markdown (pojedyncza perykopa albo 'all')
tools/export_typst.py         # baza -> Typst -> PDF
tools/export_site.py          # baza -> site/ (statyczna wersja dla GitHub Pages)
browser/app.py + browser/index.html   # przeglądarka webowa (localhost:8008)
Makefile                      # build, serve, export, site, typst, pdf, tekst, clean
README.md                     # dokumentacja techniczna i delimitacja 63 perykop
SKILL.md                      # procedura dodania perykopy (skill „perykopa")
NOWA_KSIEGA.md                # jak postawić takie repozytorium dla innej księgi
humanizer.md                  # standard redakcyjny: usuwanie wzorców AI
```

Dane **nie mieszkają w kodzie**. Perykopę dopisuje się jako wpis w tablicy
`pericopes` pliku `data/*.json`; `tools/egzegeza_mateusza_build.py` to sam
mechanizm budowy i nie zawiera treści.

## Przepływ pracy przy dodawaniu perykopy

```bash
make build                                            # 1. budowa bazy od zera z data/*.json
python3 tools/export_pericope.py 1 /tmp/kontrola.md   # 2. kontrola jednej perykopy
make export                                           # 3. regeneracja całości
```

Walidatora nie ma — `validate.py` nie istnieje. Siatką bezpieczeństwa jest
`make build`: rozjazd etykiet bloków kończy się `KeyError`, a `CHECK`
w schemacie odrzuca wartości poza słownikami. Dodatkowo warto sprawdzić
konwencje grepem: półpauzę w zakresach i polskie cudzysłowy (skrypty
w `SKILL.md`).

Baza jest **zawsze** budowana od zera. Nigdy nie edytuj
`data/egzegeza_mateusza.sqlite` ręcznie — jedynym źródłem prawdy są
`data/*.json`. Jeśli `make build` przechodzi, commituj.

Szczegółowa procedura dodania nowej perykopy: `SKILL.md` w korzeniu
repozytorium. Przeczytaj ją **zanim** zaczniesz pisać jakiekolwiek dane.

## Stan prac

Maszyneria stoi, treści nie ma. `data/` zawiera `schema.sql` i szkielet
`wprowadzenie.json` (tytuł, motto, pusta lista sekcji); `PHASES`
w `tools/egzegeza_mateusza_build.py` jest pustą listą, `make build` przechodzi
i daje bazę z zerami. Źródło tekstu `db.sqlite` jest kompletne: 18 346 słów
interlinii, 1068 wersetów greckich w 28 rozdziałach, 1071 wersetów Wulgaty,
1425 not aparatu.

Kolejność robót wedle `NOWA_KSIEGA.md`: delimitacja → Wprowadzenie →
pierwsza perykopa jako wzorzec → reszta → przekroje → recenzja przy źródłach.
Delimitacja (63 perykopy) jest **propozycją w `README.md`** i czeka na
zatwierdzenie; Wprowadzenia i żadnej perykopy jeszcze nie ma.

`status`: `szkic` → `w_opracowaniu` → `ukonczona` → `do_rewizji`.
Perykopy pisane przez Claude'a dostają **`w_opracowaniu`** — nigdy
`ukonczona`. Status `ukonczona` nadaje wyłącznie Paweł po weryfikacji
przy źródłach.

## Konwencje treści

**Języki obce.** Każde wyrażenie greckie, łacińskie, hebrajskie i aramejskie
dostaje polskie tłumaczenie w nawiasie bezpośrednio po nim — zawsze, także
przy powtórzeniach w tej samej perykopie i w odpowiedziach w czacie.
Kolejność jest wiążąca: najpierw wyrażenie obce, potem tłumaczenie:

> βασιλεία τῶν οὐρανῶν (królestwo niebios) · *lex talionis* (prawo odwetu) ·
> malkut szamajim (królowanie niebios) · korban (dar ofiarny)

**Tekst grecki.** Nestle-Aland. Przekład polski jest **roboczy, własny,
celowo dosłowny** — nie cytuj Biblii Tysiąclecia, Paulistów ani Warszawskiej.
Przekład międzywierszowy w `db.sqlite` (Popowski-Wojciechowski) jest
materiałem pomocniczym do interlinii, nie przekładem do przepisywania
w `verses.items` ani w `blocks[*].transl`.

Nie inwestuj w sekcję „Nota warsztatowa": `browser/index.html`
i `export_typst.py` ją filtrują, więc nie widać jej ani w przeglądarce, ani
w PDF — wchodzi tylko do eksportu Markdown.

**Typografia.** Polskie cudzysłowy `„…"`, gdzie znak zamykający jest
**zwykłym ASCII `"`**, nie `”`. Półpauza w zakresach: `w. 6–8`, `Mt 5,1–12`.
Em-pauza `—` dla wtrąceń. Kursywa Markdown dla terminów łacińskich.

**Ton.** Rzeczowy, gęsty, bez egzaltacji i bez kaznodziejstwa. Zdania
oznajmujące, bez zwracania się do czytelnika w drugiej osobie. Wolno być
pięknym w puencie, nie wolno być rozwlekłym w wywodzie. Dopóki nie ma
pierwszej perykopy Mateusza, miarą gęstości i tonu jest Prolog z `../john`
(`python3 ../john/tools/export_pericope.py 1 /tmp/wzor.md`).

## Uczciwość warsztatowa — WAŻNE

Treści patrystyczne piszesz **z pamięci**, nie z lektury źródeł. To znaczy:

1. Parafrazuj myśl Ojca, nie udawaj cytatu. Cytat dosłowny tylko wtedy,
   gdy jesteś pewien brzmienia.
2. *Locus* (miejsce w dziele) podawaj wedle standardowej numeracji, ale
   traktuj jako **wskazówkę do weryfikacji**, nie jako pewnik.
3. W podsumowaniu pracy **zawsze** przypomnij, że loci i szczegóły
   wymagają sprawdzenia przy źródłach (Źródła Myśli Teologicznej, PSP,
   Migne) przed publikacją.
4. Nie wymyślaj dzieł ani numerów homilii, których nie kojarzysz.
   Lepiej podać samego autora bez locus niż zmyślić sygnaturę.

Ta zasada obowiązuje tak samo przy datach soborów, wariantach rękopisów
i szczegółach liturgicznych.

## Pułapki techniczne (sprawdzone boleśnie)

**Cudzysłowy w Pythonie.** Polski cudzysłów `„…"` wewnątrz łańcucha
w podwójnych cudzysłowach wysadza parser, bo znak zamykający `"` kończy
łańcuch. Dane są w JSON-ie, gdzie problem nie występuje, ale pułapka
wraca w **każdym skrypcie** dotykającym treści — wysadziła parser podczas
pisania `tools/db_tekst_build.py` w tym repozytorium. Treści z `„…"` pisz
w potrójnych apostrofach, a przy dłuższych blokach podawaj je skryptowi
przez plik (shellowy heredoc `<<'EOF'`), nie literałem:

```python
("κόσμος", "kosmos", "rzeczownik", '''świat — „ludzkość odwrócona od Boga"'''),
```

**`sed` i znak `#`.** Nie używaj `#` jako separatora `sed`, gdy wzorzec albo
zamiennik sam zawiera `#` — polecenie podmieni wtedy wcięcia w całym pliku
i uszkodzi skrypt. Do podmian w kodzie i treści używaj Pythona, nie `sed`.

**Etykiety bloków muszą się zgadzać znak w znak.** `patristic`, `refs`
z kotwicą `unit` i `theme_links` z kotwicą `block` odwołują się do etykiet
z listy `blocks` — łącznie z półpauzą (`w. 6–8`, nie `w. 6-8`). Rozjazd =
`KeyError` przy budowie, i to jedyne miejsce, gdzie build łapie błąd danych
za ciebie.

**Kolejność `PHASES` wyznacza identyfikatory wierszy.** Nowy plik perykopy
dopisuj **na końcu** listy w `tools/egzegeza_mateusza_build.py`, nigdy
w środku — wstawienie w środek przenumerowuje wszystko za nim.

**Nie edytuj `data/egzegeza_mateusza.sqlite`.** Zmiany wprowadzasz
w `data/*.json` i przebudowujesz bazę przez `make build`.

**Zapis plików danych.** `json.dumps(obj, ensure_ascii=False, indent=1)` —
dokładnie to formatowanie, inaczej diff obejmie cały plik zamiast
zmienionego łańcucha.

**`.gitignore` ignoruje `*.md` i ma białą listę.** Nowy plik Markdown, który
ma być śledzony, trzeba do niej dopisać. W repozytorium Jana ta reguła raz
połknęła `CLAUDE.md` i `SKILL.md`, a `humanizer.md` przetrwał tam tylko
dlatego, że był śledzony, zanim regułę wprowadzono — tutaj trzeba go było
dopisać do białej listy wprost.

**Morfologia to MorphGNT, w obu księgach ten sam zapis.** `db.sqlite` niesie
kody dziesięcioznakowe (`v-3pai-s--`), nanoszone przez
`tools/morphgnt_import.py` z edycji SBLGNT MorphGNT. Moduły w `../na/db/` mają
kody Robinsona (`V-PAI-3S`) i build je nadpisuje — **nie przeliczaj** jednego
zapisu na drugi, bo Robinson nie odróżnia medium od strony biernej
w imiesłowach perfecti i konwersja dopisywałaby rozróżnienia, których w źródle
nie ma. 58 słów (0,32%) zostaje bez kodu: to miejsca, w których tekst NA różni
się od SBLGNT, więc kod byłby wymysłem. Nie uzupełniaj ich ręcznie.

**Mt 17 i Wulgata.** Wulgata klementyńska dzieli ten rozdział inaczej niż
tekst krytyczny; `tools/db_tekst_build.py` przecina łaciński w. 14 przed
*dicens:* i przesuwa resztę rozdziału. Jeśli kiedyś podmienisz moduł
Wulgaty, sprawdź to miejsce — poza Mt 17 numeracje się pokrywają.

**Liturgia mieszka w prozie.** Recepcja liturgiczna jest podsekcją sekcji
VII, nie osobną tabelą — `liturgical_use` usunięto ze schematu w Janie
w październiku 2026, bo dwie warstwy rozjechały się i zaczęły sobie
przeczyć. Nie przywracaj tabeli; sigla lekcjonarza i ryty wplataj w akapit.

**FTS5.** `remove_diacritics` działa tylko dla łaciny. Greki, hebrajskiego
i polskiego „ł" szukaj w pełnym zapisie: `MATCH 'βασιλεία'`,
`MATCH 'światłość'`. Indeksowane są `analysis_unit`, `section`,
`commentary_block` i `lexeme`.

## Słowniki (wartości dozwolone przez CHECK)

- `section_type`: filologia, kontekst, teologia, autor_ludzki, autor_bozy,
  odniesienia, patrystyka, recepcja, zakonczenie, nota, inne
- `relation` (odniesienia): cytat, aluzja, typologia, paralela, kontrast,
  rozwiniecie, tlo, por
- `tradition` (dzieła): patrystyka, scholastyka, magisterium, wspolczesna,
  judaizm, filozofia_antyczna, inna
- `status`: szkic, w_opracowaniu, ukonczona, do_rewizji
- `lang` (terminy semickie): hbr, aram

## Ojcowie przy Mateuszu

Sięgaj najpierw po tych, którzy **realnie komentowali tę księgę** — zestaw
jest inny niż u Jana, gdzie całą Ewangelię przeszli Chryzostom i Augustyn.
Komentarze ciągłe do Mateusza zostawili:

- **św. Jan Chryzostom** — *Homiliae in Matthaeum*, dziewięćdziesiąt homilii
  przez całą Ewangelię; pierwszy wybór przy niemal każdej perykopie
- **św. Hieronim** — *Commentariorum in Matthaeum libri IV*, zwięzły komentarz
  do całości
- **św. Hilary z Poitiers** — *Commentarius in Matthaeum*, najstarszy łaciński
  komentarz do całej księgi
- **Orygenes** — *Commentarium in Matthaeum*; po grecku zachowana część,
  resztę zna się z łacińskiej *Series veteris interpretationis*
- **św. Chromacjusz z Akwilei** — *Tractatus in Matthaeum*
- **św. Augustyn** — nie ma komentarza ciągłego, ale *De sermone Domini in
  monte* jest podstawowym tekstem do Mt 5–7, a *De consensu euangelistarum*
  do miejsc synoptycznie spornych
- **św. Tomasz z Akwinu** (scholastyka) — *Super Evangelium S. Matthaei
  lectura* oraz *Catena aurea*, która sama jest zbiorem kateny
- średniowiecze łacińskie: **Rabanus Maurus**, *Commentarius in Matthaeum*;
  **Paschazjusz Radbertus**, *Expositio in Matthaeum*
- komentarze współczesne: U. Luz, W. D. Davies i D. C. Allison, R. T. France,
  J. Nolland, D. A. Hagner; po polsku A. Paciorek (NKB NT I) i J. Homerski

**Dwie pułapki atrybucji, odpowiedniki pseudo-Bedy z bazy Jana:**

1. *Opus imperfectum in Matthaeum* (PG 56) chodzi pod imieniem Chryzostoma,
   ale jest dziełem anonimowym, łacińskim i o ariańskim zabarwieniu. Nie
   przypisuj go Chryzostomowi; jeśli korzystasz, nazwij je wprost.
2. *In Matthaei euangelium expositio* (PL 92) pod imieniem św. Bedy nie jest
   jego dziełem — ta sama lekcja, którą recenzje `adultera.json`,
   `niewidomy.json` i `poswiecenie.json` wyciągnęły w bazie Jana. Autentyczny
   materiał Bedy do Mateusza szukaj w *Homiliae euangelii*.

**Nie dokładaj Ojca tylko dla liczby głosów.** Jeśli perykopy nikt z Ojców
nie komentował osobno, powiedz to w nocie i oprzyj katenę na wzmiankach
rozproszonych, zamiast udawać komentarz, którego nie ma.

## Co jest Mateuszowe i powinno wracać w analizie

Nie jako szablon do powtarzania w każdej perykopie, lecz jako rzeczy, które
w tej księdze faktycznie niosą ciężar:

- **formuły wypełnienia** — ἵνα πληρωθῇ τὸ ῥηθὲν (aby wypełniło się
  powiedziane) i jej warianty; przy każdej sprawdź, czy cytat idzie za LXX,
  za tekstem hebrajskim, czy za wersją nieznaną z żadnego z nich
- **βασιλεία τῶν οὐρανῶν** (królestwo niebios) jako Mateuszowa omowa unikająca
  imienia Boga — i miejsca, gdzie mimo to stoi βασιλεία τοῦ θεοῦ
  (królestwo Boga)
- **pięć wielkich mów** domykanych formułą καὶ ἐγένετο ὅτε ἐτέλεσεν ὁ Ἰησοῦς
  (i stało się, gdy skończył Jezus): Mt 7,28; 11,1; 13,53; 19,1; 26,1
- **ἀπὸ τότε ἤρξατο ὁ Ἰησοῦς** (od tego czasu zaczął Jezus) w Mt 4,17 i 16,21
  — szew trzech części księgi, po którym idzie delimitacja
- **δικαιοσύνη** (sprawiedliwość) w znaczeniu Mateuszowym, nie Pawłowym
- **ὁ υἱὸς τοῦ Δαυίδ** (Syn Dawida) i cała chrystologia królewska rodowodu
- **Kościół** — ἐκκλησία stoi w Ewangeliach tylko u Mateusza (16,18; 18,17)
- **tło judaistyczne**: judaizm Drugiej Świątyni, polemika z faryzeizmem po
  70 r., targumy, Qumran, literatura rabiniczna — u Mateusza waży więcej niż
  u któregokolwiek z synoptyków
- **relacja do Marka i Q** tam, gdzie redakcja Mateusza jest widoczna i coś
  znaczy teologicznie; nie przy każdej perykopie
