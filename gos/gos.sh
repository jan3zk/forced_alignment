#!/bin/bash

cd "$(dirname "$0")"

# Copy transcriptions from XML(TEI) to TXT for MFA align
./parse_tei.sh ../data/Gos.TEI.2.1/Artur-J ../data/gos_processed/Artur-J/mfa_input

# Copy WAVs to mfa_input
#rsync -avhz --progress --stats --include='Artur-J*.wav' --exclude='*' /storage/rsdo/korpus/GOS2.0/Artur-WAV/ ../data/gos_processed/Artur-J/mfa_input/
# Alternatively create only links to source WAV files at the mfa_input
for file in /storage/rsdo/korpus/GOS2.0/Artur-WAV/Artur-J*.wav; do
  ln -s "$file" ../data/gos_processed/Artur-J/mfa_input/
done

# MFA alignment
mfa align --clean ~/repos/forced_alignment/data/gos_processed/Artur-J/mfa_input /storage/janezk/mfa_data/lexicon_all.txt acoustic_model ~/repos/forced_alignment/data/gos_processed/Artur-J/mfa_output

# If some of the files are not aligned by the above command copy them to tmp dir and perform the alignment again by manual exclusion of problematic parts
cd ../data/iriss_processed
mkdir -p tmp
for file in $(comm -23 <(ls mfa_input | sed 's/\.[^.]*$//' | sort -u) <(ls mfa_output | sed 's/\.[^.]*$//' | sort -u)); do
    cp "mfa_input/${file}.wav" "tmp/${file}.wav" 2>/dev/null
    cp "mfa_input/${file}.txt" "tmp/${file}.txt" 2>/dev/null
done
cd "$(dirname "$0")"
# Retry alignments with a higher beam size
mfa align --clean ~/repos/forced_alignment/data/iriss_processed/tmp /storage/janezk/mfa_data/lexicon_all.txt acoustic_model ~/repos/forced_alignment/data/iriss_processed/mfa_output --beam 300 --retry_beam 400

# Compensate trimming in the output TextGrid
./compensate_timing.sh ../data/iriss_processed/mfa_output ../data/iriss ../data/iriss_processed/TextGrid

# Add tiers to TextGrid file
./add_tiers.sh ../data/iriss_processed/TextGrid ../data/iriss ../data/iriss_processed/TextGrid_final