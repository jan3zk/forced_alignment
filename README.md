# Slovene Speech and Transcription Alignment using Montreal Forced Aligner

This repository provides instructions for aligning transcriptions with corresponding audio files containing Slovene speech using the Montreal Forced Aligner (MFA). Follow the steps below to set up the environment and align your speech corpus.

## Installation

1. Create a virtual environment and install MFA by running the following commands:

```bash
conda create -n aligner -c conda-forge montreal-forced-aligner
conda activate aligner
mfa -help
```

2. The next steps assume that your speech corpus is located at `~/mfa_data/corpus` and the pronunciation dictionary is at `~/mfa_data/dictionary.txt`. Adjust the paths accordingly based on your setup. The speech corpus should be in the format as explained in the [MFA documentation](https://montreal-forced-aligner.readthedocs.io/en/latest/user_guide/dictionary.html).

## Validation

Before aligning the data, you can validate whether your dataset is in the proper format for MFA. Run the following command:

```bash
mfa validate ~/mfa_data/corpus ~/mfa_data/dictionary.txt --clean
```

## Acoustic Model Training

To train the acoustic model and export it to a zip file, use the following command:

```bash
mfa train ~/mfa_data/corpus ~/mfa_data/dictionary.txt ~/mfa_data/acoustic_model.zip
```

Alternatively, one can download a [pretrained model](https://unilj-my.sharepoint.com/:u:/g/personal/janezkrfe_fe1_uni-lj_si/EYhQtHlcbplGl66DnktMTRYB_1zU_nYqbjNIUVNk3F_quw) and the [pronunciation dictionary](https://unilj-my.sharepoint.com/:t:/g/personal/janezkrfe_fe1_uni-lj_si/EWsrSJEG8fxIkmPL5w6G2KMB-dVH4RodUxD3V4Rzy4GLOQ). If using the pretrained model, skip the training step.

You can save the acoustic model stored in zip file for later convenience by running:

```bash
mfa model save acoustic ~/mfa_data/acoustic_model.zip
```

To inspect the acoustic model, run the following command:

```bash
mfa model inspect acoustic acoustic_model
```

## Alignment

Finally, you can align your input data using a pronunciation dictionary and the trained acoustic model by running:

```bash
mfa align /path/to/input/wavs/and/txt/ ~/mfa_data/dictionary.txt acoustic_model /path/to/aligned/outputs/
```

Make sure to replace `/path/to/input/wavs/and/txt/` with the actual path to your input data, and `/path/to/aligned/outputs/` with the desired location for the aligned output files. The above command will output the TextGrid file with word and phoneme level alignments for each wav/txt input pair.

For more details and advanced usage, please refer to the official documentation of Montreal Forced Aligner.

## Enhancing TextGrid Files with Additional Tiers

The MFA delivers alignments at both the word and phoneme levels. To introduce a syllable level, [add_cnvrstl-syllables_tier.py](add_cnvrstl-syllables_tier.py) function can be utilized as follows:

```bash
python add_cnvrstl-syllables_tier.py /path/to/input.TextGrid /path/to/input.trs /path/to/output.TextGrid
```

Similary, other tiers can be added. A list of implemented tiers and their brief explanation:

* [add_speaker-ID_tier.py](add_speaker-ID_tier.py): The script parses speaker intervals from an XML (TEI) file and adds them as a new 'speaker-ID' tier to an existing TextGrid file, which is then saved to a specified output TextGrid file.
* [add_standardized-trs_tier.py](add_standardized-trs_tier.py): The script aligns a standardized text transcription with speaker intervals in a TextGrid file by concatenating words within each speaker's interval, and then adds this speaker-specific, aligned transcription as a new tier named 'standardized-trs' to the output TextGrid file.
* [add_conversational-trs_tier.py](add_conversational-trs_tier.py): The script aligns a conversational text transcription with speaker intervals in a TextGrid file, concatenating words within each speaker interval, and then adds this aligned speaker-specific transcription as a new tier to the output TextGrid file.
* [add_cnvrstl-wrd-sgmnt_tier.py](add_cnvrstl-wrd-sgmnt_tier.py): The script aligns the input conversational transcript with the word intervals from the 'strd-wrd-sgmnt' tier in a TextGrid file by matching words from the transcription to their corresponding time intervals and then adds this aligned data as a new tier to the output TextGrid file. The number of words in the input transcription should be the same as in 'strd-wrd-sgmnt' tier for the script to work as intended.
* [add_discourse-marker_tier.py](add_discourse-marker_tier.py): The script processes a TextGrid file to detect and label discourse markers in speech, based on a list loaded from an external file, and then adds these labeled intervals to a new tier in the output TextGrid file.
* [add_pitch-reset_tier.py](add_pitch-reset_tier.py): The script features two methods for detecting pitch resets: the "average-neighboring" method, which compares a syllable's mean pitch with the average of its neighbors and labels significant differences as pitch resets, and the "intrasyllabic" method, which examines pitch changes within a single syllable, identifying a pitch reset if the difference exceeds 4 semitones.
* [add_intensity-reset_tier.py](add_intensity-reset_tier.py): The script employs two methods to detect intensity resets. The "near" method compares a syllable's mean intensity with the average of its two closest neighbors, labeling significant differences as intensity resets. Conversely, the "extended" method contrasts a syllable's mean intensity with the average of its four closest neighbors, identifying significant differences as intensity resets.
* [add_speech-rate-reduction_tier.py](add_speech-rate-reduction_tier.py): The script includes two methods for detecting speech rate reduction. The "near" method compares the syllable length with the average length of its immediate neighbors, while the "extended" method uses the average length of the four closest neighbors. The script then labels syllables that are significantly longer than this average, as determined by the reduction_threshold argument.
* [add_pause_tier.py](add_pause_tier.py): The script identifies and labels pauses in speech by analyzing a TextGrid file, marking intervals as 'POS' for pauses (empty or whitespace-only intervals) in the 'strd-wrd-sgmnt' tier.
* [add_speaker-change_tier.py](add_speaker-change_tier.py): The script analyzes a TextGrid file to identify and label speaker changes within conversational syllable intervals, marking these changes as 'POS' when a change occurs or 'NEG' otherwise.
* [add_word-ID_tier.py](add_word-ID_tier.py): The script extracts and synchronizes word identifiers from the input XML, then adds these as a new tier to the output TextGrid file.

## Acoustic Measurements

The script [acoustic_measurements.py](acoustic_measurements.py) computes various acoustic measurements from a given TextGrid file and WAV audio file, extracting phoneme durations, pitch-related features, formants, intensity, VOT (Voice Onset Time), COG (Center of Gravity), and related annotations. The computed values are then stored in a CSV file for analysis and further processing.

**Usage:**

```bash
python acoustic_measurements.py [input.TextGrid] [input.wav] [output.csv]
```

**Input:**

* `input.TextGrid`: A TextGrid file containing phoneme boundaries and other annotations
* `input.wav`: The corresponding audio file
* `output.csv`: The output CSV file to save the acoustic measurements

**Output:**

The output CSV file will contain the following columns for each phoneme:

* `Phone`: The phoneme label
* `Duration`: The duration of the phoneme (seconds)
* `AvgPitch`: The average pitch of the phoneme (Hz)
* `PitchTrend`: The pitch trend of the phoneme (rising, falling, or mixed)
* `F1Formant`: The F1 formant frequency (Hz)
* `F2Formant`: The F2 formant frequency (Hz)
* `F3Formant`: The F3 formant frequency (Hz)
* `F4Formant`: The F4 formant frequency (Hz)
* `Intensity`: The average intensity of the phoneme (dB)
* `VOT`: The voice onset time (seconds)
* `COG`: The centroid of gravity of the phoneme (Hz)
* `PreviousPhone`: The phoneme preceding the current phoneme
* `NextPhone`: The phoneme following the current phoneme
* `Word`: The word containing the current phoneme
* `Sentence`: The sentence containing the current phoneme
* `AudioID`: The ID of the audio file
* `SpeakerID`: The ID of the speaker

## Batch Processing

**Processing forced alignments**

This Bash script [align.sh](align.sh) is designed to automate the process of performing forced alignment and adding multiple tiers to TextGrid files using a set of Python scripts. The script iterates through WAV files in a specified directory, performs multiple operations including forced alignment over short time intervals of input audio/trainscription pairs, and adding various tiers to the TextGrid files for detailed analysis. Execute the script using the following command:

```bash
./align.sh [wav_dir] [out_dir] [lexicon] [xml_dir] [duration]
```

The script accepts these input arguments:

* `[wav_dir]`: Path to the directory containing WAV files.
* `[out_dir]`: Path to the directory where output files and intermediate files will be stored.
* `[lexicon]`: Path to the lexicon file used for MFA forced alignment.
* `[xml_dir]`: Path to the directory containing XML files, i.e. transcriptions in TEI format.
* `[duration]`: A floating-point number that defines the length of the audio segments in seconds. These segments are created from the input audio and transcriptions prior to MFA forced alignment. The value 'Inf' implies no segmentation will be performed.

**Processing acoustic measurements**

The script [acoustics.sh](acoustics.sh) is designed to facilitate the processing of audio files for acoustic measurements. It takes three directory paths as input arguments: one for TextGrid files, one for WAV files, and one for output CSV files. The script iterates over each TextGrid file in the specified directory, locates its corresponding WAV file, performs acoustic measurements using a Python script [acoustic_measurements.py](acoustic_measurements.py), and outputs the results in CSV format. It can be called as follows:

```bash
./acoustics.sh [textgrid_dir] [wav_dir] [csv_dir]
```

## Databases

**GOS database ([korpus GOvorjene Slovenščine](https://viri.cjvt.si/gos/System/About))**

* Spoken corpus Gos 2.1 (transcriptions): [https://www.clarin.si/repository/xmlui/handle/11356/1863](https://www.clarin.si/repository/xmlui/handle/11356/1863)
* Spoken corpus Gos VideoLectures 4.0 (audio): [https://www.clarin.si/repository/xmlui/handle/11356/1222](https://www.clarin.si/repository/xmlui/handle/11356/1222)
* ASR database ARTUR 1.0 (audio): [https://www.clarin.si/repository/xmlui/handle/11356/1776](https://www.clarin.si/repository/xmlui/handle/11356/1776)
* IRISS, SST and SPOG subsets: [https://nl.ijs.si/nikola/mezzanine/](https://nl.ijs.si/nikola/mezzanine/)

## Performance Evaluation

The accuracy of forced alignment can be assessed using the [aligner_eval.py](aligner_eval.py) script. This script compares word intervals calculated by the alignment process against intervals found in XML(TEI) files from the GOS database:

```bash
python aligner_eval.py <xml_dir> <textgrid_or_ctm_dir>
```

### Alternative to MFA for performance comparison: NeMo Forced Aligner

To install NeMo, follow the [instructions](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/tools/nemo_forced_aligner.html).

Pretrained model available at: [https://www.clarin.si/repository/xmlui/handle/11356/1737](https://www.clarin.si/repository/xmlui/handle/11356/1737).

Forced alignment using NeMo can be performed by the following commands:

```bash
python nemo_manifest.py <wav_dir> <xml_dir> <manifest_dir>
python nemo_align.py <nemo_dir> <model_path> <manifest_dir> <output_dir>
```

Or use script [nemo_align.sh](nemo_align.sh) to perform alignment on shorter audio sections. To convert NeMo *.ctm files to *.TextGrid files use the following command

```bash
python ctm2textgrid.py <input.ctm> <output.TextGrid>
```

## Use Case Examples

### Audio anonymization

A practical example of using forced alignment for audio anonymization is available in [anonymization_example.ipynb](anonymization_example.ipynb). This notebook provides a detailed walkthrough on how to use forced alignment to compute the time intervals of each word in a transcription. It then demonstrates how to anonymize the corresponding audio by replacing the utterances of words containing personal information with a beep sound, using the script [anonymize_audio.py](anonymize_audio.py). The script can accept a list of words that need to be anonymized. Alternatively, if no words are provided, the script uses the [spaCy library](https://spacy.io/) to search for and identify words representing personal names.

### Overlap analysis with manually anotated prosodic units

The script [prosodic_unit_overlap.py](prosodic_unit_overlap.py) computes overlap ratios between the "PU" tier, which contains manually annotated prosodic units, and automatically computed tiers such as "pitch-reset", "intensity-reset", "speech-rate-reduction", "pause", and "speaker-change". To analyze a single file and display results in the console:
```bash
python prosodic_unit_overlap.py <path/to/file.TextGrid>
```
To process all .TextGrid files in a directory and save the results to a CSV file:
```bash
python prosodic_unit_overlap.py <path/to/*.TextGrid> [results.csv]
```