# Anonimizacija zvočnih posnetkov

[![en](https://img.shields.io/badge/lang-en-blue.svg)](anonymization.md)

Anonimizacija zvočnih posnetkov je postopek spreminjanja zvočnih posnetkov z namenom odstranitve ali spremembe osebnih podatkov, s čimer se zaščiti zasebnost govorcev. V kontekstu jezikoslovne in govorne analize to pogosto vključuje zamenjavo osebnih imen, lokacij, datumov in drugih zasebnih informacij z nevtralnimi ali neprepoznavnimi zvoki, kot so piski.

## Metode anonimizacije

Skripta podpira dve različni metodi anonimizacije zvočnih posnetkov:

### 1. Anonimizacija na podlagi TextGrid
Ta metoda uporablja poravnavo na ravni besed med zvokom in transkripcijo, primerna je za sistematično anonimizacijo določenih besed ali samodejno zaznanih osebnih podatkov.

### 2. Anonimizacija na podlagi TRS
Ta metoda uporablja ročne označbe v formatu Transcriber AG (.trs datoteke), primerna je za selektivno anonimizacijo specifičnih govornih segmentov, ki vsebujejo občutljive informacije.

## Postopek anonimizacije s TextGrid

### Predpogoji
Pred začetkom anonimizacije s TextGrid potrebujete:
1. Zvočni posnetek (format .wav)
2. Pripadajočo transkripcijo (format .txt)
3. Nameščen Montreal Forced Aligner (MFA)
4. Izgovorni slovar
5. Akustični model

### Korak 1: Prisilna poravnava z MFA

Zvočne datoteke morajo biti poravnane s transkripcijami z uporabo Montreal Forced Aligner. Postopek poravnave ustvari TextGrid datoteke s časovnimi žigi za vsako besedo:

```bash
mfa align </pot/do/mape/z/wav/in/txt/datotekami/> </pot/do/izgovorni_slovar.txt> </pot/do/akusticni_model.zip> </pot/do/poravnanih_datotek/>
```

Ta postopek ustvari TextGrid datoteke, ki vsebujejo:
- Segmentacijo na ravni besed
- Časovne žige za vsako besedo
- Poravnave na ravni fonemov

Podrobna navodila za poravnavo najdete [tukaj](../README.md#Alignment).

### Korak 2: Anonimizacija zvoka s TextGrid

Način TextGrid lahko uporabljate na dva načina:

#### Samodejno zaznavanje imen
```bash
python audio_anonymizer.py textgrid vhod.wav vhod.TextGrid izhod.wav
```
Ta način:
- Uporablja spaCy-jev slovenski transformer model za prepoznavanje imenskih entitet
- Samodejno zazna osebna imena, organizacije in lokacije
- Anonimizira vse zaznane entitete
- Zagotovi poročilo o identificirani in anonimizirani vsebini

#### Ročna določitev besed
```bash
python audio_anonymizer.py textgrid vhod.wav vhod.TextGrid izhod.wav --keywords beseda1 "beseda2*" beseda3
```
Ta način omogoča:
- Eksplicitno določanje besed za anonimizacijo
- Uporabo nadomestnih znakov * (npr., [* se ujema z vsem besedilom v oglatih oklepajih)
- Neobčutljivost na velike/male črke
- Kombinacijo več ključnih besed

## Postopek anonimizacije s TRS

### Predpogoji
- Zvočni posnetek (format .wav)
- Pripadajoča TRS datoteka z ročnimi označbami
- Oznake Background, ki označujejo občutljivo vsebino

### Zagon TRS anonimizacije
```bash
python audio_anonymizer.py trs vhod.wav vhod.trs izhod.wav
```

TRS način išče posebej označene segmente v transkripciji:
```xml
<Background time="začetni_čas" type="shh" level="high"/>
[občutljiva vsebina]
<Background time="končni_čas" level="off"/>
```

## Tehnične podrobnosti

### Generiranje piska
Obe metodi anonimizacije uporabljata napredno generiranje piskov, ki:
- Ujame glasnost okoliškega govora
- Uporabi postopno naraščanje/pojemanje za gladkejše prehode
- Ohrani trajanje izvirnega govornega segmenta

### Ujemanje glasnosti
Anonimizator zagotavlja naravno zveneč izhod z:
- Analizo glasnosti okoliškega govora
- Prilagoditvijo glasnosti piska
- Uporabo rahlega faktorja zmanjšanja za udobje

### Nadzor kakovosti
Za najboljše rezultate:
1. Vedno preverite kakovost prisilne poravnave pred anonimizacijo
2. Preverite samodejno zaznane entitete pri uporabi samodejnega načina
3. Poslušajte anonimizirani izhod, da zagotovite pravilno obdelavo vse občutljive vsebine
4. Ohranite varnostne kopije izvirnih datotek

## Primeri uporabe

### Primer 1: Samodejno zaznavanje imen
```bash
python audio_anonymizer.py textgrid posnetek.wav transkripcija.TextGrid anonimizirano.wav
```
Izhod:
```
Zaznane ključne besede z osebnimi podatki: ['Janez', 'Novak', 'Ljubljana']
Anonimizacija dela od 1.23s do 1.89s: Janez
Anonimizacija dela od 2.45s do 3.12s: Novak
...
```

### Primer 2: Ročni seznam besed z nadomestnimi znaki
```bash
python audio_anonymizer.py textgrid posnetek.wav transkripcija.TextGrid anonimizirano.wav --keywords "Jan*" "Nov*" "Ljubljana"
```
Izhod:
```
Anonimizacija dela od 1.23s do 1.89s: Janez
Anonimizacija dela od 2.45s do 3.12s: Novak
...
```

### Primer 3: TRS način
```bash
python audio_anonymizer.py trs posnetek.wav transkripcija.trs anonimizirano.wav
```
Izhod:
```
Najdeni 3 intervali za anonimizacijo:
  1230ms - 1890ms (trajanje: 660ms)
  Besedilo za anonimizacijo: [ime in priimek]
...
```