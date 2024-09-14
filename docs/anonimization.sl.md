# Anonimizacija zvočnih posnetkov

[![en](https://img.shields.io/badge/lang-en-blue.svg)](anonimization.md)

Anonimizacija zvočnih posnetkov je postopek, kjer zvočne posnetke prilagodimo tako, da se odstrani ali spremeni osebno prepoznavne informacije, kar omogoča varovanje zasebnosti govorcev. V kontekstu jezikovnih in govornih analiz se to pogosto nanaša na zamenjavo osebnih imen, krajev, datumov in drugih zasebnih informacij z nevtralnimi ali neprepoznavnimi zvoki, kot je piskanje.

## Postopek anonimizacije

Za izvedbo anonimizacije je najprej potrebno izvesti prisilno poravnavo med zvočnim posnetkom in njegovo transkripcijo, kar omogoča natančno določitev časovnih intervalov izgovorjenih besed. To lahko dosežemo z uporabo orodja Montreal Forced Aligner (MFA), ki ustvari TextGrid datoteke s časovnimi oznakami za vsako besedo ali fonem.

**Vsiljena poravnava z MFA**

Preden začnemo z anonimizacijo, moramo zvočne datoteke poravnati z njihovimi transkripcijami. Postopek poravnave z uporabo MFA poteka s sledečim ukazom:

```bash
mfa align </pot/do/mape/z/datotekami/wav/in/txt/> </pot/do/slovarja_izgovorjav.txt> </pot/do/akustičnega_modela.zip> </pot/do/poravnanih_izhodnih_datotek/>
```

Ta ukaz ustvari datoteke TextGrid, ki vsebujejo časovne oznake besed, kar omogoča natančno anonimizacijo določenih besed. Podrobnejša navodila za poravnavo najdete v poglavju [Poravnava](README.md#Poravnava)


**Anonimizacija zvočne datoteke**

Ko imamo TextGrid datoteko, lahko izvedemo anonimizacijo z uporabo priložene skripte `anonymize_audio.py`, ki besede, določene za anonimizacijo, nadomesti z zvokom piskanja. Skripto se kliče z naslednjim ukazom:
```bash
python anonymize_audio.py <input.wav> <input.TextGrid> <output.wav> [word1 word2 word3 ...]
```
Skripta prejme naslednje vhodne parametre:
- **`input.wav`**: Izhodiščna zvočna datoteka.
- **`input.TextGrid`**: Poravnana transkripcija v obliki TextGrid.
- **`output.wav`**: Pot do izhodne anonimizirane zvočne datoteke.
- **Opcijsko**: Seznam besed, ki jih želimo anonimizirati.

Skripta deluje v dveh načinih:
- **Samodejna detekcija osebnih podatkov**: Če seznam besed za anonimizacijo ni podan, skripta uporabi knjižnico [spaCy](https://spacy.io/) za samodejno določitev besed z osebnimi podatki, kot so imena, kraji in drugi zasebni podatki.
- **Ročna specifikacija besed za anonimizacijo**: Uporabnik lahko ročno določi seznam besed za anonimizacijo, kar omogoča boljši nadzor nad postopkom. Besede se lahko vnesejo kot dodatni vhodni parametri.

Skripta nato pregleda TextGrid datoteko in najde časovne intervale, ki ustrezajo besedam za anonimizacijo, ter jih zamenja z zvokom piskanja v izhodni zvočni datoteki.
