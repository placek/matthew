# Egzegeza Ewangelii Mateusza — build & serve
#
#   make            # zbuduj bazę (jeśli brak) i uruchom serwer
#   make build      # (prze)buduj bazę SQLite od zera z data/*.json
#   make serve      # uruchom serwer webowy (browser/: index.html + API)
#   make export     # wyeksportuj wszystkie perykopy do Markdown
#   make export PID=9 [OUT=blogoslawienstwa.md]   # jedną perykopę
#   make site       # statyczna wersja przeglądarki (site/) — np. GitHub Pages
#   make typst      # reprezentacja Typst (egzegeza.typ)
#   make pdf        # złóż PDF (egzegeza.pdf) — wymaga typst
#   make clean      # usuń wygenerowaną bazę, site/ i eksport Typst
#   make tekst      # (prze)buduj db.sqlite — źródło tekstu (greka/polski/Wulgata/aparat)
#
# Układ repozytorium:
#   data/     — źródła: schema.sql + *.json (oraz generowana baza)
#   tools/    — narzędzia: egzegeza_mateusza_build.py, export_pericope.py
#   browser/  — przeglądarka: app.py (backend) + index.html
#   db.sqlite — źródło tekstu Ewangelii (make tekst), osobne od egzegezy
#
# Wymaga tylko python3 (biblioteka standardowa) — patrz shell.nix.

PYTHON ?= python3
TYPST  ?= typst
DB      = data/egzegeza_mateusza.sqlite
TYP     = egzegeza.typ
PDF     = egzegeza.pdf
SOURCES = tools/egzegeza_mateusza_build.py data/schema.sql \
          data/wprowadzenie.json data/rodowod.json data/narodzenie.json \
          data/magowie.json data/egipt.json data/chrzciciel.json \
          data/chrzest.json data/kuszenie.json
BUILD   = tools/egzegeza_mateusza_build.py
APP     = browser/app.py
EXPORT  = tools/export_pericope.py
PORT    ?= 8008
PID     ?= all
OUT     ?=

.PHONY: all serve build rebuild export site typst pdf tekst clean

## zbuduj bazę (jeśli brak) i wystaw stronę z backendem
all: serve

## uruchom serwer — serwuje index.html oraz /api/* na http://localhost:$(PORT)
serve: $(DB)
	PORT=$(PORT) $(PYTHON) $(APP)

## zbuduj bazę SQLite tylko gdy brak lub gdy zmieniły się źródła
$(DB): $(SOURCES)
	$(PYTHON) $(BUILD)

## wymuś przebudowę bazy od zera
build: $(SOURCES)
	$(PYTHON) $(BUILD)

rebuild: clean build

## eksport perykopy do Markdown; PID=all (domyślnie) lub numer, OUT=plik.md (opcjonalnie)
export: $(DB)
	$(PYTHON) $(EXPORT) $(PID) $(OUT)

## statyczna wersja przeglądarki: site/ (index.html + api/*.json) — hosting bez Pythona
site: $(DB)
	$(PYTHON) tools/export_site.py

## reprezentacja Typst: egzegeza.typ (perykopy + motywy)
typst: $(TYP)

$(TYP): $(DB) tools/export_typst.py
	$(PYTHON) tools/export_typst.py

## złóż PDF z reprezentacji Typst (wymaga typst — patrz shell.nix)
pdf: $(PDF)

$(PDF): $(TYP) newathu.ttf rgreek.ttf
	$(TYPST) compile --font-path . $(TYP) $(PDF)

## (prze)buduj db.sqlite — tekst grecki, polski, Wulgata i aparat krytyczny
tekst:
	$(PYTHON) tools/db_tekst_build.py

## usuń wygenerowaną bazę, stronę statyczną i eksport Typst
clean:
	rm -f $(DB) egzegeza.typ egzegeza.pdf
	rm -f egzegeza_mateusz1.md pericope_*.md
	rm -rf site
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
