#!/bin/bash
set -e

# Call examples:
# ./align.sh "/storage/rsdo/korpus/GOS2.0/Artur-WAV/Artur-N*.wav" data/gos_processed/Artur-N /storage/janezk/mfa_data/lexicon_all.txt ./data/acoustic_model_optilex.zip ./data/OPTILEX_v3_g2p.zip data/Gos.TEI.2.1/Artur-N 30
# ./align.sh "/storage/rsdo/korpus/GOS2.0/Artur-WAV/Artur-N-G5033-P600031-avd.wav" data/gos_processed/Artur-N /storage/janezk/mfa_data/lexicon_all.txt ./data/acoustic_model_optilex.zip ./data/OPTILEX_v3_g2p.zip data/Gos.TEI.2.1/Artur-N 30
# ./align.sh "/storage/rsdo/korpus/MEZZANINE/GosVL/wav/*.wav" data/gos_processed/GosVL /storage/janezk/mfa_data/lexicon_all.txt ./data/acoustic_model_optilex.zip ./data/OPTILEX_v3_g2p.zip data/Gos.TEI.2.1/GosVL 30
# ./align.sh "/storage/rsdo/korpus/MEZZANINE/iriss/*.wav" data/iriss_processed /storage/janezk/mfa_data/lexicon_all.txt ./data/acoustic_model_optilex.zip ./data/OPTILEX_v3_g2p.zip /storage/rsdo/korpus/MEZZANINE/iriss 30
# ./align.sh "/storage/rsdo/korpus/MEZZANINE/SST/*.wav" data/SST_processed /storage/janezk/mfa_data/lexicon_all.txt ./data/acoustic_model_optilex.zip ./data/OPTILEX_v3_g2p.zip /storage/rsdo/korpus/MEZZANINE/SST 30

# Assign paths
wav_dir=$1 #directory or wav filepath
out_dir=$2 #output directory
lexicon=$3 #path to pronunciation dictionary
acoustic_model=${4:-./data/acoustic_model_optilex.zip} #path to MFA acoustic model
g2p_model=${5:-./data/OPTILEX_v3_g2p.zip} #path to G2P model
xml_dir=$6 #directory or xml filepath
duration=$7 #duration of fragments that are passed to forced alignment process or Inf for whole audio
enable_tiers=${8:-true} #whether to add additional tiers, default is 'true'

cd $(dirname "$0")

mkdir -p $out_dir/mfa_input

# Check if wav_dir is a file or directory
if [[ -d "$wav_dir" ]]; then
    wav_files=(${wav_dir}/*.wav)
else
    wav_files=($wav_dir)
fi

counter=0
# Iterate over all WAV files in the directory or process the single file
for wav_file in "${wav_files[@]}"; do
    counter=$((counter + 1))
    if [ $counter -ge 1 ]; then
        # Set file names
        echo -e "\nFiles ($counter):"
        base_name=$(basename "$wav_file")

        # Check if xml_dir is a directory or a file
        if [ -d "$xml_dir" ]; then
            xml_file=$xml_dir/${base_name/.wav/.xml}
            xml_file=${xml_file/-avd.xml/.xml}
        else
            xml_file=$xml_dir
        fi

        textgrid_file=$out_dir/TextGrid/${base_name/.wav/.TextGrid}
        textgrid_file_out=$out_dir/TextGrid_final/${base_name/.wav/.TextGrid}
        echo wav_file=\"$wav_file\"
        echo xml_file=\"$xml_file\"
        echo textgrid_file=\"$textgrid_file\"
        echo textgrid_file_out=\"$textgrid_file_out\"

        echo -e "\nPerforming temporal fragmentation ..."
        rm -f $out_dir/mfa_input/*.txt
        rm -f $out_dir/mfa_input/*.wav
        python fragmentize_trs_wav.py "$xml_file" "$wav_file" "$out_dir/mfa_input" "$duration"

        echo -e "\nPerforming MFA forced alignment ..."
        rm -f $out_dir/mfa_output/*.TextGrid
        mfa align \
            --clean \
            --single_speaker \
            "$out_dir/mfa_input" \
            "$lexicon" \
            "$acoustic_model" \
            "$out_dir/mfa_output" \
            --beam 300 \
            --retry_beam 3000 \
            --g2p_model_path "$g2p_model" \
            --num_jobs 1

        if [ "$duration" != "Inf" ]; then
            echo -e "\nCombining partial TextGrids ..."
            ./compensate_timing.sh "$out_dir/mfa_output" "$out_dir/mfa_output"
            mkdir -p "$out_dir/TextGrid"
            python combine_textgrid.py "$out_dir/mfa_output" "$textgrid_file"
        else
            echo -e "\nCopying TextGrid file for Inf duration ..."
            mkdir -p "$(dirname "$textgrid_file_out")"
            cp "$out_dir/mfa_output/$(basename "$textgrid_file")" "$textgrid_file"
        fi

        if [[ "$enable_tiers" != false ]]; then
            echo -e "\nAdding new tiers ..."
            mkdir -p "$out_dir/TextGrid_final"
            python add_cnvrstl-syllables_tier.py "$textgrid_file" "$xml_file" "$textgrid_file_out"
            python add_speaker-ID_tier.py "$textgrid_file_out" "$xml_file" "$textgrid_file_out"
            python add_standardized-trs_tier.py "$xml_file" "$textgrid_file_out" "$textgrid_file_out"
            python add_conversational-trs_tier.py "$xml_file" "$textgrid_file_out" "$textgrid_file_out"
            python add_cnvrstl-wrd-sgmnt_tier.py "$xml_file" "$textgrid_file_out" "$textgrid_file_out"
            python add_discourse-marker_tier.py "$textgrid_file_out" "$textgrid_file_out" ./data/discourse_markers.txt
            python add_pitch-reset_tier.py "$wav_file" "$textgrid_file_out" "$textgrid_file_out" 40 average-neighboring
            python add_intensity-reset_tier.py "$wav_file" "$textgrid_file_out" "$textgrid_file_out" 8 near
            python add_speech-rate-reduction_tier.py "$wav_file" "$textgrid_file_out" "$textgrid_file_out" 1.5 near
            python add_pause_tier.py "$textgrid_file_out" "$textgrid_file_out"
            python add_speaker-change_tier.py "$textgrid_file_out" "$textgrid_file_out"
            python add_word-ID_tier.py "$textgrid_file_out" "$xml_file" "$textgrid_file_out"
            #break
        fi
    fi
done
