# Audio Anonymization

[![sl](https://img.shields.io/badge/lang-sl-blue.svg)](anonymization.sl.md)

Audio anonymization is the process of modifying audio recordings to remove or alter personally identifiable information, thereby protecting the privacy of the speakers. In the context of linguistic and speech analysis, this often involves replacing personal names, locations, dates, and other private information with neutral or unrecognizable sounds, such as beeps.

## Anonymization Methods

The script supports two distinct methods of audio anonymization:

### 1. TextGrid-based Anonymization
This method uses word-level alignment between audio and transcription, suitable for systematic anonymization of specific words or automatically detected personal information.

### 2. TRS-based Anonymization
This method uses manual annotations in Transcriber AG format (.trs files), suitable for selective anonymization of specific speech segments that contain sensitive information.

## TextGrid-based Anonymization Process

### Prerequisites
Before starting the TextGrid-based anonymization, you need:
1. Audio recording (.wav format)
2. Corresponding transcription (.txt format)
3. Montreal Forced Aligner (MFA) installed
4. Pronunciation dictionary
5. Acoustic model

### Step 1: Forced Alignment with MFA

Audio files must be aligned with their transcriptions using the Montreal Forced Aligner. The alignment process generates TextGrid files with precise time stamps for each word:

```bash
mfa align </path/to/folder/with/wav/and/txt/files/> </path/to/pronunciation_dictionary.txt> </path/to/acoustic_model.zip> </path/to/aligned_output_files/>
```

This process creates TextGrid files containing:
- Word-level segmentation
- Time stamps for each word
- Phone-level alignments

Detailed alignment instructions can be found [here](../README.md#Alignment).

### Step 2: Audio Anonymization with TextGrid

The TextGrid mode of the anonymizer can be run in two ways:

#### Automatic Name Detection
```bash
python audio_anonymizer.py textgrid input.wav input.TextGrid output.wav
```
This mode:
- Uses spaCy's Slovenian transformer model for named entity recognition
- Automatically detects personal names, organizations, and locations
- Anonymizes all detected entities
- Provides a report of identified and anonymized content

#### Manual Word Specification
```bash
python audio_anonymizer.py textgrid input.wav input.TextGrid output.wav --keywords word1 "word2*" word3
```
This mode allows:
- Explicit specification of words to anonymize
- Wildcard matching using * (e.g., [* matches all text in square brackets)
- Case-insensitive matching
- Combination of multiple keywords

## TRS-based Anonymization Process

### Prerequisites
- Audio recording (.wav format)
- Corresponding TRS file with manual annotations
- Background tags marking sensitive content

### Running TRS Anonymization
```bash
python audio_anonymizer.py trs input.wav input.trs output.wav
```

The TRS mode looks for specially marked segments in the transcription:
```xml
<Background time="start_time" type="shh" level="high"/>
[sensitive content]
<Background time="end_time" level="off"/>
```

## Technical Details

### Beep Generation
Both anonymization methods use sophisticated beep generation that:
- Matches the volume of surrounding speech
- Applies fade in/out effects for smoother transitions
- Maintains the duration of the original speech segment

### Volume Matching
The anonymizer ensures natural-sounding output by:
- Analyzing the volume of surrounding speech
- Adjusting beep volume to match
- Applying a slight reduction factor for comfort

### Quality Control
For best results:
1. Always verify the quality of forced alignment before anonymization
2. Check the automatically detected entities when using automatic mode
3. Listen to the anonymized output to ensure all sensitive content is properly handled
4. Keep backups of original files

## Usage Examples

### Example 1: Automatic Name Detection
```bash
python audio_anonymizer.py textgrid recording.wav transcript.TextGrid anonymized.wav
```
Output:
```
Identified keywords containing personal information: ['Janez', 'Novak', 'Ljubljana']
Anonymizing part from 1.23s to 1.89s: Janez
Anonymizing part from 2.45s to 3.12s: Novak
...
```

### Example 2: Manual Word List with Wildcards
```bash
python audio_anonymizer.py textgrid recording.wav transcript.TextGrid anonymized.wav --keywords "Jan*" "Nov*" "Ljubljana"
```
Output:
```
Anonymizing part from 1.23s to 1.89s: Janez
Anonymizing part from 2.45s to 3.12s: Novak
...
```

### Example 3: TRS Mode
```bash
python audio_anonymizer.py trs recording.wav transcript.trs anonymized.wav
```
Output:
```
Found 3 background intervals to anonymize:
  1230ms - 1890ms (duration: 660ms)
  Text to anonymize: [ime in priimek]
...
```
