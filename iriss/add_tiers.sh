#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 input_textgrid_dir data_dir output_textgrid_dir"
    exit 1
fi

# Assign input and output directories from script arguments
input_dir="$1"
data_dir="$2"
output_dir="$3"

for textgrid_file in "$input_dir"/*.TextGrid; do
    # Output file path
    textgrid_file_out="$output_dir/$(basename "$textgrid_file")"

    # Standard transcription
    std_trs_file_name=$(basename "$textgrid_file")
    std_trs_file_name="${std_trs_file_name/-avd.TextGrid/-std.trs}"
    std_trs_file="$data_dir/$std_trs_file_name"

    # WAV file
    wav_file="${std_trs_file/-std.trs/-avd.wav}"

    # Conversational transcription
    pog_trs_file="${std_trs_file/-std/-pog}"

    # TEI transcription
    xml_file="${std_trs_file/-std.trs/.xml}"

    echo ""
    echo textgrid_file=\"$textgrid_file\"
    echo textgrid_file_out=\"$textgrid_file_out\"
    echo std_trs_file=\"$std_trs_file\"
    echo pog_trs_file=\"$pog_trs_file\"
    echo xml_file=\"$xml_file\"
    echo wav_file=\"$wav_file\"

    # Add new tiers
    python ../add_cnvrstl-syllables_tier.py $textgrid_file $std_trs_file $textgrid_file_out
    python ../add_speaker-ID_tier.py $textgrid_file_out $xml_file $textgrid_file_out
    python ../add_standardized-trs_tier.py $std_trs_file $textgrid_file_out $textgrid_file_out
    python ../add_conversational-trs_tier.py $pog_trs_file $textgrid_file_out $textgrid_file_out
    python ../add_cnvrstl-wrd-sgmnt_tier.py $pog_trs_file $textgrid_file_out $textgrid_file_out
    python ../add_discourse-marker_tier.py $textgrid_file_out $textgrid_file_out ../data/discourse_markers.txt
    python ../add_pitch-reset_tier.py $wav_file $textgrid_file_out $textgrid_file_out 40 average-neighboring
    python ../add_intensity-reset_tier.py $wav_file $textgrid_file_out $textgrid_file_out 8 near
    python ../add_speech-rate-reduction_tier.py $wav_file $textgrid_file_out $textgrid_file_out 1.5 near
    python ../add_pause_tier.py $textgrid_file_out $textgrid_file_out
    python ../add_speaker-change_tier.py $textgrid_file_out $textgrid_file_out
    python ../add_word-ID_tier.py $textgrid_file_out $xml_file $textgrid_file_out
done
