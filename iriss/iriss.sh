#!/bin/bash

cd "$(dirname "$0")"

# Trim silence in WAV files for better MFA alignment
./trim_silence.sh ../data/iriss ../data/iriss_processed/mfa_input

# Copy standard transcriptions from trs to txt for MFA align
./parse_std_trs.sh ../data/iriss ../data/iriss_processed/mfa_input

# MFA alignment
mfa align --clean ~/repos/forced_alignment/data/iriss_processed/mfa_input /storage/$USER/mfa_data/lexicon_all.txt acoustic_model ~/repos/forced_alignment/data/iriss_processed/mfa_output

# If some of the files are not aligned by the above command (mfa align returns an error), copy them to tmp dir and perform the alignment again by manual exclusion of problematic parts
cd ../data/iriss_processed
mkdir -p tmp
for file in $(comm -23 <(ls mfa_input | sed 's/\.[^.]*$//' | sort -u) <(ls mfa_output | sed 's/\.[^.]*$//' | sort -u)); do
    cp "mfa_input/${file}.wav" "tmp/${file}.wav" 2>/dev/null
    cp "mfa_input/${file}.txt" "tmp/${file}.txt" 2>/dev/null
done
cd "$(dirname "$0")"
# Retry alignments using higher beam sizes
mfa align --clean ~/repos/forced_alignment/data/iriss_processed/tmp /storage/$USER/mfa_data/lexicon_all.txt acoustic_model ~/repos/forced_alignment/data/iriss_processed/mfa_output --beam 300 --retry_beam 400

# Compensate trimming in the output TextGrid
./compensate_timing.sh ../data/iriss_processed/mfa_output ../data/iriss ../data/iriss_processed/TextGrid

# Add tiers to TextGrid file
./add_tiers.sh ../data/iriss_processed/TextGrid ../data/iriss ../data/iriss_processed/TextGrid_final