# Trim silence in WAV files for better MFA alignment
./trim_silence.sh ../data/iriss/ ../data/iriss_processed/
cd ../data/iriss_processed
mkdir mfa_input
mkdir trim_vals
mv *.wav mfa_input/
mv *txt trim_vals/

# Copy standard transcriptions for MFA align
./parse_std_trs.sh ../data/iriss/ ../data/iriss_processed/mfa_input/

# MFA alignment
mfa align --clean ~/repos/forced_alignment/data/iriss_processed/mfa_input/ /storage/janezk/mfa_data/lexicon_all.txt acoustic_model ~/repos/forced_alignment/data/iriss_processed/mfa_output/

# If some of the files are not aligned by the above command copy them to tmp dir and perform the alignment again by manual fragmentation of problematic files 
mkdir -p tmp
for file in $(comm -23 <(ls mfa_input | sed 's/\.[^.]*$//' | sort -u) <(ls mfa_output | sed 's/\.[^.]*$//' | sort -u)); do
    cp "mfa_input/${file}.wav" "tmp/${file}.wav" 2>/dev/null
    cp "mfa_input/${file}.txt" "tmp/${file}.txt" 2>/dev/null
done
mfa align --clean ~/repos/forced_alignment/data/iriss_processed/tmp/ /storage/janezk/mfa_data/lexicon_all.txt acoustic_model ~/repos/forced_alignment/data/iriss_processed/mfa_output/

# Compensate trimming in the output TextGrid
./compensate_timing.sh ../data/iriss_processed/mfa_output/ ../data/iriss/ ../data/iriss_processed/TextGrid

# Add tiers to TextGrid file
./add_tiers.sh ../data/iriss_processed/TextGrid ../data/iriss ../data/iriss_processed/TextGrid_final