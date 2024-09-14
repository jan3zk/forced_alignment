# Analiza prekrivanja z ročno označenimi prozodičnimi enotami

[![en](https://img.shields.io/badge/lang-en-blue.svg)](overlap_analysis.md)

Analiza prekrivanja med ročno označenimi prozodičnimi enotami (PU) in avtomatsko zaznanimi prozodičnimi parametri je ključnega pomena za preverjanje natančnosti in konsistence algoritmov za samodejno obdelavo govora. Prozodične enote so zvočne enote, ki izražajo značilnosti govora, kot so višina tona, intenzivnost, hitrost govora, premori in spremembe govorcev. V tej razširjeni analizi bomo podrobneje raziskali metode za ovrednotenje ujemanj med temi parametri in ročnimi oznakami.

## Prekrivanje prosodičnih parametrov

Skripta [`prosodic_param_overlap.py`](../prosodic_param_overlap.py) je namenjena analizi prekrivanja intervalov med ročno označenimi prozodičnimi enotami (PU) in parametri, kot so:

- **"pitch-reset"** (ponastavitev višine tona),
- **"intensity-reset"** (ponastavitev glasnosti),
- **"speech-rate-reduction"** (zmanjšanje hitrosti govora),
- **"pause"** (premori v govoru),
- **"speaker-change"** (sprememba govorca).

**Postopek analize:**

Skripta primerja intervale v vrstici "PU" z ustreznimi samodejno zaznanimi intervali v zgoraj navedenih vrsticah. Za vsako primerjavo izračuna delež (v absolutni in relativni obliki), kjer je samodejno zaznani parameter sovpadal z ročno označenimi mejami. Skripta opcijsko shrani rezultate v datoteko CSV, ki vključuje podrobnosti o stopnji prekrivanja in neprekrivanja za vsak parameter.

**Ukaz za zagon analize:**

```bash
python prosodic_param_overlap.py </path/to/*.TextGrid> [results.csv]
```

Kjer je `</path/to/*.TextGrid>` pot do datotek TextGrid, ki jih želimo analizirati, opcijski argument `[results.csv]` pa omogoča shranjevanje rezultatov analize v datoteko CSV.

## Analiza prekrivanja diskurznih označevalcev

Skripta [`discourse_marker_overlap.py`](../discourse_marker_overlap.py) je namenjena analizi prekrivanja med ročno označenimi prozodičnimi enotami (vrstica "PU") in diskurznimi označevalci (DO), kot so premori v govoru, poudarki, spremembe govorcev in drugi govorni pojavi, ki jih zaznamujejo DO.

**Postopek analize:**

Skripta primerja intervale DO z ročno določenimi mejami prozodičnih enot (vrstica "PU") in izračuna kazalnike prekrivanja za vsak edinstven DO. Relativni in absolutni deleži ujemanj so podani tako za samodejno določene DO (vrstica "discourse-marker") kot tudi za ročno potrjene DO (vrstica "actualDM"). 

**Ukaz za zagon analize:**

```bash
python discourse_marker_overlap.py </pot/do/datotek/*.TextGrid>
```
