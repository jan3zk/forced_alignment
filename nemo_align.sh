#!/bin/bash
set -e

# Call examples:
# ./nemo_align.sh /storage/rsdo/korpus/GOS2.0/Artur-WAV/Artur-N-G5033-P600031-avd.wav data/nemo/Artur-N data/Gos.TEI.2.1/Artur-N/Artur-N-G5033-P600031.xml 30
# ./nemo_align.sh /storage/rsdo/korpus/GOS2.0/Artur-WAV/Artur-N data/gos_processed/Artur-N data/Gos.TEI.2.1/Artur-N 30
# ./nemo_align.sh /storage/rsdo/korpus/MEZZANINE/GosVL/wav/ data/gos_processed/GosVL data/Gos.TEI.2.1/GosVL 30
# ./nemo_align.sh /storage/rsdo/korpus/MEZZANINE/iriss/ data/iriss_processed /storage/rsdo/korpus/MEZZANINE/iriss 30
# ./nemo_align.sh /storage/rsdo/korpus/MEZZANINE/SST/ data/SST_processed /storage/rsdo/korpus/MEZZANINE/SST 30

# Assign paths
wav_dir=$1 #directory or wav filepath
out_dir=$2 #output directory
xml_dir=$3 #directory or xml filepath
duration=$4 #duration of fragments that are passed to forced alignment process

cd $(dirname "$0")

mkdir -p $out_dir/nemo_input

# Check if wav_dir is a file or directory
if [ -d "$wav_dir" ]; then
    wav_files=(${wav_dir}/*.wav)
else
    wav_files=($wav_dir)
fi

counter=0
# Iterate over all WAV files in the directory or process the single file provided
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
        rm -f $out_dir/nemo_input/*.txt
        rm -f $out_dir/nemo_input/*.wav
        rm -f $out_dir/nemo_input/*.json
        python fragmentize_trs_wav.py "$xml_file" "$wav_file" "$out_dir/nemo_input" "$duration"
        
        echo -e "\nCreating NeMo manifest file ..."
        python nemo_manifest.py "$out_dir/nemo_input/*.wav" "$out_dir/nemo_input" "$out_dir/nemo_input" 
        
        echo -e "\nPerforming NeMo forced alignment ..."
        rm -f $out_dir/nemo_output/*.json
        rm -rf $out_dir/nemo_output/ctm/
        python nemo_align.py ~/repos/NeMo/ data/v2.0/conformer_ctc_bpe.nemo $out_dir/nemo_input/ $out_dir/nemo_output/
        
        echo -e "\nConverting *.ctm to *.TextGrid ..."
        python ctm2textgrid.py "$out_dir/nemo_output/ctm/words/*.ctm" "$out_dir/nemo_output/ctm/words" 

        if [ "$duration" != "Inf" ]; then
            echo -e "\nCombining partial TextGrids ..."
            ./compensate_timing.sh "$out_dir/nemo_output/ctm/words" "$out_dir/nemo_output/ctm/words"
            mkdir -p "$out_dir/TextGrid"
            python combine_textgrid.py "$out_dir/nemo_output/ctm/words" "$textgrid_file"
        else
            echo -e "\nCopying TextGrid file for Inf duration ..."
            mkdir -p "$(dirname "$textgrid_file_out")"
            cp "$out_dir/nemo_output/$(basename "$textgrid_file")" "$textgrid_file"
        fi
    fi
done

