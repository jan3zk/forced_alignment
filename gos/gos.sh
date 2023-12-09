#!/bin/bash
set -e

# Assign paths
gos_dir=/storage/rsdo/korpus/GOS2.0
folder=Artur-P
out_dir=../data/gos_processed
lexicon=/storage/$USER/mfa_data/lexicon_all.txt
xml_dir=../data/Gos.TEI.2.1/$folder

cd $(dirname "$0")

mkdir -p $out_dir/$folder/mfa_input

counter=0
# Iterate over all WAV files in the GOS directory and perform forced alignment
for wav_file in $gos_dir/Artur-WAV/$folder*.wav; do
    counter=$((counter + 1))
    if [ $counter -ge 2 ]; then
        # Set file names
        echo -e "\nFiles ($counter):"
        base_name=$(basename $wav_file)
        xml_file=$xml_dir/${base_name/-avd.wav/.xml}
        textgrid_file=$out_dir/$folder/TextGrid/${base_name/.wav/.TextGrid}
        textgrid_file_out=$out_dir/$folder/TextGrid_final/${base_name/.wav/.TextGrid}
        echo wav_file=\"$wav_file\"
        echo xml_file=\"$xml_file\"
        echo textgrid_file=\"$textgrid_file\"
        echo textgrid_file_out=\"$textgrid_file_out\"
        
        echo -e "\nPerforming MFA forced alignmet ..."
        rm -f $out_dir/$folder/mfa_input/*.txt
        rm -f $out_dir/$folder/mfa_input/*.wav
        python ../fragmentize_trs_wav.py $xml_file $wav_file $out_dir/$folder/mfa_input 60 || continue
        rm -f $out_dir/$folder/mfa_output/*.TextGrid
        mfa align --clean $out_dir/$folder/mfa_input $lexicon acoustic_model $out_dir/$folder/mfa_output --beam 300 --retry_beam 400
            
        echo -e "\nCombining partial TextGrids ..."
        ./compensate_timing.sh $out_dir/$folder/mfa_output $out_dir/$folder/mfa_output
        mkdir -p $out_dir/$folder/TextGrid
        python ../combine_textgrid.py $out_dir/$folder/mfa_output $textgrid_file
        
        echo -e "\nAdding new tiers ..."
        mkdir -p $out_dir/$folder/TextGrid_final
        python ../add_cnvrstl-syllables_tier.py $textgrid_file $xml_file $textgrid_file_out
        python ../add_speaker-ID_tier.py $textgrid_file_out $xml_file $textgrid_file_out
        python ../add_standardized-trs_tier.py $xml_file $textgrid_file_out $textgrid_file_out
        python ../add_conversational-trs_tier.py $xml_file $textgrid_file_out $textgrid_file_out
        python ../add_cnvrstl-wrd-sgmnt_tier.py $xml_file $textgrid_file_out $textgrid_file_out
        python ../add_discourse-marker_tier.py $textgrid_file_out $textgrid_file_out ../data/discourse_markers.txt
        python ../add_pitch-reset_tier.py $wav_file $textgrid_file_out $textgrid_file_out 40 average-neighboring    
        python ../add_intensity-reset_tier.py $wav_file $textgrid_file_out $textgrid_file_out 8 near
        python ../add_speech-rate-reduction_tier.py $wav_file $textgrid_file_out $textgrid_file_out 1.5 near
        python ../add_pause_tier.py $textgrid_file_out $textgrid_file_out
        python ../add_speaker-change_tier.py $textgrid_file_out $textgrid_file_out
        python ../add_word-ID_tier.py $textgrid_file_out $xml_file $textgrid_file_out
        #break
    fi
done
