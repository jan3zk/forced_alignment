# Slovene Speech Alignment with Montreal Forced Aligner

This repository provides instructions for aligning Slovene speech using the Montreal Forced Aligner (MFA). Follow the steps below to set up the environment and align your speech corpus.

## Installation

1. Create a virtual environment and install MFA by running the following commands:

```bash
conda create -n aligner -c conda-forge montreal-forced-aligner
conda activate aligner
mfa -help
```

2. The next steps assume that your speech corpus is located at `~/mfa_data/corpus` and the pronunciation dictionary is at `~/mfa_data/dictionary.txt`. Adjust the paths accordingly based on your setup. [MFA documentation](https://montreal-forced-aligner.readthedocs.io/en/latest/user_guide/dictionary.html).

## Validation

Before aligning the data, you can validate whether your dataset is in the proper format for MFA. Run the following command:

```bash
mfa validate ~/mfa_data/corpus ~/mfa_data/dictionary.txt --clean
```

## Acoustic Model Training

To train the acoustic model and export it to a zip file, use the following command:

```bash
mfa train ~/mfa_data/corpus ~/mfa_data/lexicon_all.txt ~/mfa_data/acoustic_model.zip
```

Alternatively, a pretrained model and the pronunciation dictionary can be downloaded from [here](https://unilj-my.sharepoint.com/:f:/g/personal/janezkrfe_fe1_uni-lj_si/EpYgD7Y3PrlFgtIwSH7nkJoByWgpE2beKOpoP4R_NnkobQ?e=JcTKVM). If using the pretrained model, skip the training step.

You can save the acoustic model stored in zip file for later convenience by running:

```bash
mfa model save acoustic ~/mfa_data/acoustic_model.zip
```

## Acoustic Model Inspection

To inspect the acoustic model, run the following command:

```bash
mfa model inspect acoustic acoustic_model
```

## Alignment

Finally, you can align your input data using a pronunciation dictionary and the trained acoustic model by running:

```bash
mfa align /path/to/input/wavs/and/txt/ ~/mfa_data/dictionary.txt acoustic_model /path/to/aligned/outputs/
```

Make sure to replace `/path/to/input/wavs/and/txt/` with the actual path to your input data, and `/path/to/aligned/outputs/` with the desired location for the aligned output files.

For more details and advanced usage, please refer to the official documentation of Montreal Forced Aligner.