#!/bin/bash
set -e

# Call examples:
# ./align.sh /storage/rsdo/korpus/GOS2.0/Artur-WAV/Artur-N ./data/gos_processed/Artur-N /storage/janezk/mfa_data/lexicon_all.txt ./data/Gos.TEI.2.1/Artur-N 30
# ./align.sh /storage/rsdo/korpus/GosVL/wav/ ./data/gos_processed/GosVL /storage/janezk/mfa_data/lexicon_all.txt ./data/Gos.TEI.2.1/GosVL 30

# Assign paths
wav_dir=$1
out_dir=$2
lexicon=$3
xml_dir=$4
duration=$5

cd $(dirname "$0")

mkdir -p $out_dir/mfa_input

counter=0
# Iterate over all WAV files in the GOS directory and perform forced alignment
for wav_file in ${wav_dir}*.wav; do
    counter=$((counter + 1))
    if [ $counter -ge 1 ]; then
        # Set file names
        echo -e "\nFiles ($counter):"
        base_name=$(basename $wav_file)
        xml_file=$xml_dir/${base_name/.wav/.xml}
        xml_file=${xml_file/-avd.xml/.xml}
        textgrid_file=$out_dir/TextGrid/${base_name/.wav/.TextGrid}
        textgrid_file_out=$out_dir/TextGrid_final/${base_name/.wav/.TextGrid}
        echo wav_file=\"$wav_file\"
        echo xml_file=\"$xml_file\"
        echo textgrid_file=\"$textgrid_file\"
        echo textgrid_file_out=\"$textgrid_file_out\"

        echo -e "\nPerforming MFA forced alignmet ..."
        rm -f $out_dir/mfa_input/*.txt
        rm -f $out_dir/mfa_input/*.wav
        python fragmentize_trs_wav.py $xml_file $wav_file $out_dir/mfa_input $duration #|| continue
        rm -f $out_dir/mfa_output/*.TextGrid
        mfa align --clean $out_dir/mfa_input $lexicon acoustic_model $out_dir/mfa_output --beam 300 --retry_beam 3000

        if [ "$duration" != "Inf" ]; then
            echo -e "\nCombining partial TextGrids ..."
            ./compensate_timing.sh $out_dir/mfa_output $out_dir/mfa_output
            mkdir -p $out_dir/TextGrid
            python combine_textgrid.py $out_dir/mfa_output $textgrid_file #|| continue
        else
            echo -e "\nCopying TextGrid file for Inf duration ..."
            mkdir -p $(dirname "$textgrid_file_out")
            cp $out_dir/mfa_output/$(basename "$textgrid_file") $textgrid_file
        fi

        echo -e "\nAdding new tiers ..."
        mkdir -p $out_dir/TextGrid_final
        python add_cnvrstl-syllables_tier.py $textgrid_file $xml_file $textgrid_file_out #|| continue
        python add_speaker-ID_tier.py $textgrid_file_out $xml_file $textgrid_file_out #|| continue
        python add_standardized-trs_tier.py $xml_file $textgrid_file_out $textgrid_file_out #|| continue
        python add_conversational-trs_tier.py $xml_file $textgrid_file_out $textgrid_file_out #|| continue
        python add_cnvrstl-wrd-sgmnt_tier.py $xml_file $textgrid_file_out $textgrid_file_out #|| continue
        python add_discourse-marker_tier.py $textgrid_file_out $textgrid_file_out ./data/discourse_markers.txt #|| continue
        python add_pitch-reset_tier.py $wav_file $textgrid_file_out $textgrid_file_out 40 average-neighboring     #|| continue
        python add_intensity-reset_tier.py $wav_file $textgrid_file_out $textgrid_file_out 8 near #|| continue
        python add_speech-rate-reduction_tier.py $wav_file $textgrid_file_out $textgrid_file_out 1.5 near #|| continue
        python add_pause_tier.py $textgrid_file_out $textgrid_file_out #|| continue
        python add_speaker-change_tier.py $textgrid_file_out $textgrid_file_out #|| continue
        python add_word-ID_tier.py $textgrid_file_out $xml_file $textgrid_file_out #|| continue
        break
    fi
done
