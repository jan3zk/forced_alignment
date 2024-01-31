# Slovene Speech Alignment with Montreal Forced Aligner

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

Alternatively, a pretrained model and the pronunciation dictionary can be downloaded from [here](https://unilj-my.sharepoint.com/:f:/g/personal/janezkrfe_fe1_uni-lj_si/EpYgD7Y3PrlFgtIwSH7nkJoByWgpE2beKOpoP4R_NnkobQ?e=JcTKVM). If using the pretrained model, skip the training step.

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

## Enhancing TextGrid files with additional tiers

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

**Example:**

The following command will calculate acoustic measurements for the phonemes in `input.TextGrid` and save the results to `output.csv`:
```bash
python acoustic_measurements.py input.TextGrid input.wav output.csv
```

## Batch processing

The script [acoustics.sh](acoustics.sh) is designed to facilitate the processing of audio files for acoustic measurements. It takes three directory paths as input arguments: one for TextGrid files, one for WAV files, and one for output CSV files. The script iterates over each TextGrid file in the specified directory, locates its corresponding WAV file, performs acoustic measurements using a Python script [acoustic_measurements.py](acoustic_measurements.py), and outputs the results in CSV format. It can be called as follows:
```bash
./acoustics.sh [textgrid_dir] [wav_dir] [csv_dir]
```

### Processing IRISS database

See script [iriss.sh](iriss/iriss.sh).

### Processing GOS database

See script [gos.sh](gos/gos.sh).

