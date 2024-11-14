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

## Analiza sovpadanja diskurznih označevalcev

Skripta [`discourse_marker_overlap.py`](../discourse_marker_overlap.py) analizira sovpadanje diskurznih označevalcev z mejami prozodičnih enot v datotekah TextGrid. Obdeluje datoteke, ki vsebujejo označene govorne podatke, kjer so diskurzni označevalci in prozodične enote označeni v ločenih vrsticah.

### Funkcionalnosti

Skripta izvaja tri vrste analiz:
1. Sovpadanja med oznakami "af" iz vrstice "actualDM" in mejami prozodičnih enot
2. Sovpadanja med oznakami skupin diskurznih označevalcev (TI, TQ, TR, I, C) in mejami prozodičnih enot
3. Sovpadanja med oznakami podskupin diskurznih označevalcev in mejami prozodičnih enot

### Zahteve za vhodne podatke

Skripta pričakuje datoteke TextGrid z naslednjimi vrsticami:
- "PU": Vsebuje označbe mej prozodičnih enot
- "actualDM": Vsebuje označbe diskurznih označevalcev z oznako "af"
- "actual-DM-classif": Vsebuje klasifikacije diskurznih označevalcev v formatu X-YY, kjer je:
  - X[X] glavna skupina (TI, TQ, TR, I, C, ...)
  - YY podskupina (npr. MC, MO, PI, RI, RR, itd.)

### Uporaba

```bash
python discourse_marker_overlap.py <pot_do_datoteke_ali_mape_textgrid>
```

Skripta lahko obdela:
- Posamezno datoteko TextGrid
- Mapo z več datotekami TextGrid (z uporabo nadomestnih znakov)

Primeri:
```bash
# Obdelava posamezne datoteke
python discourse_marker_overlap.py pot/do/datoteke.TextGrid

# Obdelava vseh datotek TextGrid v mapi
python discourse_marker_overlap.py "pot/do/mape/*.TextGrid"
```

### Izpis rezultatov

Skripta prikaže podrobno statistiko za vsako obdelano datoteko in skupne rezultate za vse datoteke:

1. Sovpadanja oznak "af":
   - Število in odstotek oznak "af", ki sovpadajo z mejami prozodičnih enot

2. Sovpadanja skupin:
   - Število in odstotek sovpadanj za vsako glavno skupino (TI, TQ, TR, I, C, ...)

3. Sovpadanja podskupin:
   - Število in odstotek sovpadanj za vsako podskupino

Rezultati so prikazani v formatu: `X/Y (Z%)`, kjer je:
- X število sovpadanj
- Y skupno število pojavitev
- Z odstotek sovpadanj
```
