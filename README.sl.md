# Poravnava posnetkov slovenskega govora in transkripcij z uporabo knjižnice Montreal Forced Aligner

[![en](https://img.shields.io/badge/lang-en-red.svg)](README.md)

Ta repozitorij vsebuje navodila za poravnavo zvočnimih datotek in njihovih transkripcij pri čemer se zanašamo na uporabo knjižnice Montreal Forced Aligner (MFA). Spodaj opisani koraki omogočajo poravnavo govornega korpusa.

## Namestitev

1. Ustvarite virtualno okolje in namestite program MFA tako, da zaženete naslednje ukaze:

```bash
conda create -n aligner -c conda-forge montreal-forced-aligner
conda activate aligner
mfa -help
```

2. V naslednjih korakih predpostavljamo, da se govorni korpus nahaja na naslovu `~/mfa_data/corpus`. Poti ustrezno prilagodite glede na svoje nastavitve. Govorni korpus mora biti v obliki, kot je razloženo v [dokumentaciji MFA](https://montreal-forced-aligner.readthedocs.io/en/latest/user_guide/dictionary.html).

## Validacija korpusa

Pred poravnavo lahko preverite, ali je korpus v ustrezni obliki za MFA, kar storite z naslednjim ukazom:

```bash
mfa validate ~/mfa_data/corpus ~/mfa_data/dictionary.txt --clean
```

## Učenje akustičnega modela

Učenje akustičnega modela se lahko izvede z ukazom

```bash
mfa train ~/mfa_data/corpus ~/mfa_data/dictionary.txt ~/mfa_data/acoustic_model.zip
```

Druga možnost je prenos [predhodno naučenega modela](https://unilj-my.sharepoint.com/:u:/g/personal/janezkrfe_fe1_uni-lj_si/EYhQtHlcbplGl66DnktMTRYB_1zU_nYqbjNIUVNk3F_quw). V tem primeru zgornji uzaz za učenje modela ni potreben.

## Poravnava

Poravnava vhodnih datotek se vrši s pomočjo naučenega akustičnega modela in slovarja izgovarjav z ukazom

```bash
mfa align /path/to/input/wavs/and/txt/ ~/mfa_data/dictionary.txt acoustic_model /path/to/aligned/outputs/
```

pri čemer slovar izgovorja lahko prenesete [tukaj](https://unilj-my.sharepoint.com/:t:/g/personal/janezkrfe_fe1_uni-lj_si/EWsrSJEG8fxIkmPL5w6G2KMB-dVH4RodUxD3V4Rzy4GLOQ). Poskrbite, da boste `/path/to/input/wavs/and/txt/` nadomestili z dejansko potjo do vhodnih podatkov, `/path/to/aligned/outputs/` pa z želeno lokacijo za poravnane izhodne datoteke. Zgornji ukaz bo izpisal datoteko TextGrid s poravnavo na ravni besed in fonemov za vsak vhodni par datotek WAV/TXT.

## Razširitev datotek TextGrid z dodatnimi nivoji

Knjižnica MFA zagotavlja poravnavo na ravni besed in fonemov. Poravnava na ravni zlogov se lahko izvrši z uporabo funkcije [add_cnvrstl-syllables_tier.py](add_cnvrstl-syllables_tier.py) preko ukaza:

```bash
python add_cnvrstl-syllables_tier.py /path/to/input.TextGrid /path/to/input.trs /path/to/output.TextGrid
```
ki doda novo vrstco s časovnimi intervali na nivoju zlogov v izhodno datoteko TextGrid. Na podoben način je mogoče dodati tudi naslednje vrstice:

* [add_speaker-ID_tier.py](add_speaker-ID_tier.py): Skripta razčleni intervale govorcev iz datoteke XML (TEI) in jih kot novo vrstico "speaker-ID" doda v izhodno datoteko TextGrid.
* [add_standardized-trs_tier.py](add_standardized-trs_tier.py): Skripta uskladi transkripcijo v standardizirani obliki  z intervali govorcev v datoteki TextGrid tako, da združi besede znotraj intervala vsakega govorca, in nato doda ta zapis kot vrstico z imenom "standardized-trs" v izhodno datoteko TextGrid.
* [add_conversational-trs_tier.py](add_conversational-trs_tier.py): Skripta uskladi transkripcijo v pogovorni obliki z intervali govorcev v datoteki TextGrid, pri čemer združi besede znotraj vsakega intervala govorcev, nato pa ta zapis doda kot novo vrstico v izhodno datoteko TextGrid.
*  [add_cnvrstl-wrd-sgmnt_tier.py](add_cnvrstl-wrd-sgmnt_tier.py): Skripta uskladi vhodno transkripcijo v pogovori obliki z besednimi intervali v vrstici "strd-wrd-sgmnt", tako da besede iz transkripcije ujema z ustreznimi časovnimi intervali, nato pa to poravnano transkripcijo doda kot novo vrstico v izhodno datoteko TextGrid. Število besed v vhodni transkripciji mora biti enako številu besed v vrstici "strd-wrd-sgmnt", da skripta deluje kot je predvideno.
* [add_discourse-marker_tier.py](add_discourse-marker_tier.py): Skripta doda v izhodno datoteko TextGrid vrstico z oznakam kje se nahajajo diskurzni označevalci.
* [add_pitch-reset_tier.py](add_pitch-reset_tier.py): Skripta vsebuje dve metodi za odkrivanje ponastavitev tonske višine: metodo "average-neighboring", ki primerja povprečno višino tona zloga s povprečjem njegovih sosedov in označuje pomembne razlike kot ponastavitve višine tona, ter metodo "intrasyllabic", ki preučuje spremembe višine tona znotraj enega zloga in prepozna ponastavitev višine tona, če razlika presega 4 poltone.
* [add_intensity-reset_tier.py](add_intensity-reset_tier.py): Skripta uporablja dve metodi za odkrivanje ponastavitev glasnosti. Metoda "near" primerja povprečno intenziteto zloga s povprečjem njegovih dveh najbližjih sosedov, pri čemer pomembne razlike označi kot ponastavitve glasnosti. Nasprotno pa metoda "extended" primerja povprečno intenziteto zloga s povprečjem njegovih štirih najbližjih sosedov in označi pomembne razlike kot ponastavitev glasnosti.
* [add_speech-rate-reduction_tier.py](add_speech-rate-reduction_tier.py): Skripta vključuje dve metodi za zaznavanje zmanjšanja hitrosti govora. Metoda "near" primerja dolžino zloga s povprečno dolžino njegovih neposrednih sosedov, medtem ko metoda "extended" uporablja povprečno dolžino štirih najbližjih sosedov. Skripta nato označi zloge, ki so bistveno daljši od tega povprečja, kot je določeno z argumentom prag_zmanjšanja.
* [add_pause_tier.py](add_pause_tier.py): Skripta poišče dele govornega posnetku brez prisotnosti govora in doda novo vrstico v izhodno datoteko TextGrid, kjer so intervali premorov označeni z labelo "POS".
* [add_speaker-change_tier.py](add_speaker-change_tier.py): Skripta doda vrstico z označenimi spremembami govorcev na nivoju zlogovnih intervalov, pri čemer te spremembe označi s "POS", kadar se sprememba pojav oziroma "NEG" v nasprotnem primeru.
* [add_word-ID_tier.py](add_word-ID_tier.py): Skripta izlušči identifikatorje besed iz vhodnega XML in jih shrani v novo vrstico v izhodni datoteki TextGrid.

Tukaj je prevod v slovenščino:

## Akustične Meritve

Skripta [acoustic_measurements.py](acoustic_measurements.py) izračuna različne akustične meritve iz danih datotek TextGrid in WAV, kot so trajanje fonemov, akustične lastnosti povezane z višino tona, formante, glasnost, VOT (čas do začetka zvenečnosti), COG (težišče) in sorodne oznake. Izračunane vrednosti se nato shranijo v datoteko CSV za nadaljnjo analizo in obdelavo.

**Uporaba:**

```bash
python acoustic_measurements.py [input.TextGrid] [input.wav] [output.csv]
```

**Vhod:**

* `input.TextGrid`: TextGrid datoteka, ki vsebuje meje fonemov in druge oznake
* `input.wav`: Pripadajoča zvočna datoteka
* `output.csv`: Izhodna datoteka CSV za shranjevanje akustičnih meritev

**Izhod:**

Izhodna datoteka CSV vsebuje naslednje stolpce za posamezen fonem:

* `Phone`: Oznaka fonema
* `Duration`: Trajanje fonema (v sekundah)
* `AvgPitch`: Povprečna višina tona fonema (v Hz)
* `PitchTrend`: Trend višine tona fonema (naraščajoč, padajoč ali mešan)
* `F1Formant`: Frekvenca prvega formanta (v Hz)
* `F2Formant`: Frekvenca drugega formanta (v Hz)
* `F3Formant`: Frekvenca tretjega formanta (v Hz)
* `F4Formant`: Frekvenca četrtega formanta (v Hz)
* `Intensity`: Povprečna intenzivnost fonema (v dB)
* `VOT`: Čas do začetka zvenečnosti (v sekundah)
* `COG`: Težišče fonema (v Hz)
* `PreviousPhone`: Fonem pred trenutnim fonemom
* `NextPhone`: Fonem za trenutnim fonemom
* `Word`: Beseda, ki vsebuje trenutni fonem
* `Sentence`: Stavek, ki vsebuje trenutni fonem
* `AudioID`: ID zvočne datoteke
* `SpeakerID`: ID govorca

## Paketna obdelava posnetkov

**Vsiljena poravnava večjega števila posnetkov**

Skripta [align.sh](align.sh) je zasnovana za avtomatizacijo procesa izvajanja prisilne poravnave večjega števila posnetkov in njihovih transkripcij. Skripta iterira skozi datoteke WAV v določeni mapi in izvede več operacij, vključno s vsiljeno poravnavo preko kratkih časovnih intervalov vhodnih parov datotek posnetek/transkripcija, ter dodajanjem zgoraj opisanih vrstic v izhodne datoteke TextGrid za namene kasnejše akustične analize. Skripto zaženete z naslednjim ukazom:

```bash
./align.sh [wav_dir] [out_dir] [lexicon] [xml_dir] [duration]
```

Skripta sprejme naslednje vhodne argumente:

* `[wav_dir]`: Pot do mape, ki vsebuje datoteke WAV.
* `[out_dir]`: Pot do mape, kjer bodo shranjene izhodne datoteke in vmesne datoteke.
* `[lexicon]`: Pot do slovarja, ki se uporablja za prisilno poravnavo z MFA.
* `[xml_dir]`: Pot do mape, ki vsebuje datoteke XML, tj. transkripcije v formatu TEI.
* `[duration]`: Število, ki določa dolžino avdio segmentov v sekundah nad katerimi se naknadno vrši vsiljena poravnava z MFA.Vrednost "Inf" pomeni, da segmentacija ne bo izvedena.

**Akustične meritve na večjem številu posnetkov**

Skripta [acoustics.sh](acoustics.sh) je zasnovana za izračun akustičnih meritev na večjem številu zvočnih datotek. Kot vhodne argumente sprejme tri direktorije: prvi vsebuje datoteke TextGrid, drugi datoteke WAV in tretji izhodne datoteke CSV. Skripta iterira preko vsake TextGrid datoteke v dani mapi, poišče pripadajočo datoteko WAV, izvede akustične meritve z uporabo skripte [acoustic_measurements.py](acoustic_measurements.py) in izpiše rezultate v formatu CSV. Zažene se jo z ukazom

```bash
./acoustics.sh [textgrid_dir] [wav_dir] [csv_dir]
```

Tukaj je prevod v slovenščino:

## Podatkovni korpusi

**GOS baza podatkov ([korpus GOvorjene Slovenščine](https://viri.cjvt.si/gos/System/About))**

* Govorni korpus Gos 2.1 (transkripcije): [https://www.clarin.si/repository/xmlui/handle/11356/1863](https://www.clarin.si/repository/xmlui/handle/11356/1863)
* Govorni korpus Gos VideoLectures 4.0 (avdio): [https://www.clarin.si/repository/xmlui/handle/11356/1222](https://www.clarin.si/repository/xmlui/handle/11356/1222)
* Baza podatkov za ASR ARTUR 1.0 (avdio): [https://www.clarin.si/repository/xmlui/handle/11356/1776](https://www.clarin.si/repository/xmlui/handle/11356/1776)
* Podkorpusi IRISS, SST in SPOG: [https://nl.ijs.si/nikola/mezzanine/](https://nl.ijs.si/nikola/mezzanine/)

Tukaj je prevod v slovenščino:

## Ovrednotenje natančnosti vsiljene poravnave

Natančnost vsiljene poravnave je mogoče oceniti z uporabo skripte [aligner_eval.py](aligner_eval.py), ki medsebojno primerja besedne intervale ujemajočih datotek iz dveh vhodnih direktorijev in poda kazalce ujemanja kot so povprečna razlika in delež mej znotraj treh tolerančnih območij (10ms, 50ms in 100ms):

```bash
python aligner_eval.py <textgrid_or_xml_dir> <textgrid_or_ctm_dir>
```

Tukaj je prevod v slovenščino:

### Alternativna metoda za primerjavo natančnosti poravnave z MFA: NeMo Forced Aligner

Za namestitev NeMo sledite [navodilom](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/tools/nemo_forced_aligner.html).

Vnaprej naučen model je na voljo na: [https://www.clarin.si/repository/xmlui/handle/11356/1737](https://www.clarin.si/repository/xmlui/handle/11356/1737).

Prisilno poravnavo z NeMo lahko izvedete z naslednjimi ukazi:

```bash
python nemo_manifest.py <wav_dir> <xml_dir> <manifest_dir>
python nemo_align.py <nemo_dir> <model_path> <manifest_dir> <output_dir>
```

Ali pa uporabite skripto [nemo_align.sh](nemo_align.sh) za izvedbo poravnave na krajših avdio odsekih. Za pretvorbo NeMo *.ctm datotek v *.TextGrid datoteke uporabite naslednji ukaz:

```bash
python ctm2textgrid.py <input.ctm> <output.TextGrid>
```

Tukaj je prevod v slovenščino:

## Primeri uporabe

### Anonimizacija zvočnih posnetkov

Ta razdelek ponuja praktičen primer, kako anonimizirati zvočne posnetke z uporabo prisilne poravnave. Tehnika vključuje nadomestitev izgovorjenih besed z osebnimi podatki s piskajočim zvokom.

Za začetek postopka anonimizacije poskrbite, da imate zvočno datoteko v formatu WAV in ustrezno transkripcijo v datoteki TXT. Prisilno poravnavo lahko izvedete z naslednjim ukazom, ki ustvari datoteko TextGrid, ki vsebuje časovne intervale besed v transkripciji:

```bash
mfa align /directory/containing/input/wavs/and/txt/ ~/mfa_data/dictionary.txt path/to/acoustic_model.zip /path/to/output/dir/
```

Z uporabo datoteke TextGrid, pridobljene z zgornjim ukazom, je mogoče anonimizirati zvok z

```bash
python anonymize_audio.py input.wav input.TextGrid output.wav
```

Ta ukaz zamenja določene besede z zvokom piskanja v izhodni WAV datoteki. Skripta [anonymize_audio.py](anonymize_audio.py) lahko prejme seznam besed za anonimizacijo kot vhodni argument. Če tega seznama ne podamo, privzeto uporabi [spaCy knjižnico](https://spacy.io/) za samodejno zaznavanje besed z osebnimi podatki.

Zvezek [anonymization_example.ipynb](anonymization_example.ipynb) analizira vpliv predhodno anonimiziranih transkripcij na natančnost procesa vsiljene poravnave.

### Analiza prekrivanja z ročno označenimi prozodičnimi enotami

Skripta [prosodic_unit_overlap.py](prosodic_unit_overlap.py) izračuna razmerje prekrivanja intervalov med vrstico "PU", ki vsebuje ročno označene prozodične enote, in samodejno izračunanimi intervali v vrsticah "pitch-reset", "intensity-reset", "speech-rate-reduction", "pause" in "speaker-change". Za analizo posamezne datoteke in prikaz rezultatov v konzoli uporabite:

```bash
python prosodic_unit_overlap.py <path/to/file.TextGrid>
```

Za obdelavo vseh datotek TextGrid v direktoriju in shranjevanje rezultatov v CSV datoteko:

```bash
python prosodic_unit_overlap.py <path/to/*.TextGrid> [results.csv]
```