# Audio Anonymization

[![sl](https://img.shields.io/badge/lang-sl-blue.svg)](anonymization.sl.md)

Audio anonymization is the process of modifying audio recordings to remove or alter personally identifiable information, thereby protecting the privacy of the speakers. In the context of linguistic and speech analysis, this often involves replacing personal names, locations, dates, and other private information with neutral or unrecognizable sounds, such as beeps.

## Anonymization Process

To anonymize audio, the first step is to perform forced alignment between the audio recording and its transcription, allowing precise determination of the time intervals for spoken words. This can be achieved using the Montreal Forced Aligner (MFA), which generates **TextGrid** files with time stamps for each word and phone.

**Forced Alignment with MFA**

Before starting the anonymization process, audio files must be aligned with their transcriptions. The alignment process using MFA is performed with the following command:

```bash
mfa align </path/to/folder/with/wav/and/txt/files/> </path/to/pronunciation_dictionary.txt> </path/to/acoustic_model.zip> </path/to/aligned_output_files/>
```

This command generates **TextGrid** files with word time stamps, enabling precise anonymization of specific words. Detailed alignment instructions can be found [here](../README.md#Alignment).

**Audio File Anonymization**

Once the **TextGrid** file is prepared, you can anonymize the audio using the provided `anonymize_audio.py` script, which replaces the specified words with a beeping sound. The script is called with the following command:

```bash
python anonymize_audio.py <input.wav> <input.TextGrid> <output.wav> [word1 word2 word3 ...]
```

The script accepts the following parameters:

- **`input.wav`**: The original audio file.
- **`input.TextGrid`**: The aligned transcription in **TextGrid** format.
- **`output.wav`**: The path to the output anonymized audio file.
- **Optional**: A list of words to anonymize.

The script operates in two modes:

- **Automatic detection of personal data**: If no list of words for anonymization is provided, the script uses the [spaCy](https://spacy.io/) library to automatically detect words containing personal data, such as names, places, and other private information.
- **Manual specification of words for anonymization**: The user can manually specify a list of words to anonymize, providing greater control over the process. Words can be provided as additional input parameters.

The script then scans the **TextGrid** file, finds the time intervals corresponding to the words to be anonymized, and replaces them with a beeping sound in the output audio file.