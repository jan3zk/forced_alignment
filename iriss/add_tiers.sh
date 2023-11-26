#!/bin/bash

# Check if two arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 input_textgrid_dir transcription_dir output_textgrid_dir"
    exit 1
fi

# Assign input and output directories from script arguments
input_dir="$1"
trs_dir="$2"
output_dir="$3"

for textgrid_file in "$input_dir"/*.TextGrid; do
	# Output file path
    textgrid_file_out="$output_dir/$(basename "$textgrid_file")"

    # Standard transcription
    std_trs_file_name=$(basename "$textgrid_file")
    std_trs_file_name="${std_trs_file_name/-avd.TextGrid/-std.trs}"
    std_trs_file="$trs_dir/$std_trs_file_name"

    # Conversational transcription
    pog_trs_file="${std_trs_file/-std/-pog}"

    # TEI transcription
    xml_file="${std_trs_file/-std.trs/.xml}"

    echo ""
    echo $textgrid_file
    echo $textgrid_file_out
    echo $std_trs_file
    echo $xml_file
    echo ""

	# Add new tiers
	python ../additional_tiers/add_cnvrstl-syllables_tier.py $textgrid_file $std_trs_file $textgrid_file_out
	python ../additional_tiers/add_speaker-ID_tier.py $textgrid_file_out $xml_file $textgrid_file_out
	python ../additional_tiers/add_standardized-trs_tier.py $std_trs_file $textgrid_file_out $textgrid_file_out
	python ../additional_tiers/add_conversational-trs_tier.py $pog_trs_file $textgrid_file_out $textgrid_file_out
	python ../additional_tiers/add_cnvrstl-wrd-sgmnt_tier.py $pog_trs_file $textgrid_file_out $textgrid_file_out
	#python ../additional_tiers/add_discourse-marker_tier.py ./tmp_5.TextGrid ./tmp_6.TextGrid ../discourse_markers.txt
	#python ../additional_tiers/add_pitch-reset_tier.py ./mfa_input/Iriss-J-Gvecg-P500016-avd.wav ./tmp_6.TextGrid ./tmp_7.TextGrid 40 average-neighboring
	#python ../additional_tiers/add_intensity-reset_tier.py ./mfa_input/Iriss-J-Gvecg-P500016-avd.wav ./tmp_7.TextGrid ./tmp_8.TextGrid 8 near
	#python ../additional_tiers/add_speech-rate-reduction_tier.py ./mfa_input/Iriss-J-Gvecg-P500016-avd.wav ./tmp_8.TextGrid ./tmp_9.TextGrid 1.5 near
	#python ../additional_tiers/add_pause_tier.py ./tmp_9.TextGrid ./tmp_10.TextGrid
	#python ../additional_tiers/add_speaker-change_tier.py ./tmp_10.TextGrid ./tmp_11.TextGrid
	#python ../additional_tiers/add_word-ID_tier.py ./tmp_11.TextGrid ../iriss/Iriss-J-Gvecg-P500016.xml ./tmp_12.TextGrid
done


#../data/iriss_processed/TextGrid_final//Iriss-N-G5035-P600034-avd.TextGrid

#python ../additional_tiers/add_cnvrstl-syllables_tier.py ../data/iriss_processed/TextGrid/Iriss-P-G7036-P701111-avd.TextGrid ../data/iriss/Iriss-P-G7036-P701111-std.trs ../data/iriss_processed/TextGrid_final//Iriss-P-G7036-P701111-avd.TextGrid


#../data/iriss/Iriss-P-G7036-P701111-std.trs
#../data/iriss_processed/TextGrid_final//Iriss-P-G7036-P701111-avd.TextGrid


textgrid_file="../data/iriss_processed/TextGrid/Iriss-J-Gvecg-P500042-avd.TextGrid"
textgrid_file_out="../data/iriss_processed/TextGrid_final/Iriss-J-Gvecg-P500042-avd.TextGrid"
std_trs_file="../data/iriss/Iriss-J-Gvecg-P500042-std.trs"
pog_trs_file="../data/iriss/Iriss-J-Gvecg-P500042-pog.trs"
xml_file="../data/iriss/Iriss-J-Gvecg-P500042.xml"
python ../additional_tiers/add_cnvrstl-wrd-sgmnt_tier.py ../data/iriss/Iriss-J-Gvecg-P500042-pog.trs ../data/iriss_processed/TextGrid_final/Iriss-J-Gvecg-P500042-avd.TextGrid ../data/iriss_processed/TextGrid_final/Iriss-J-Gvecg-P500042-avd.TextGrid