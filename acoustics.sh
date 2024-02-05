#!/bin/bash
set -e

# Call example:
# ./acoustics.sh data/iriss_processed/TextGrid_final/ data/iriss/ data/iriss_processed/csv

# Assign paths
textgrid_dir=$1 #./data/gos_processed/Artur-J/TextGrid_final
wav_dir=$2      #/storage/rsdo/korpus/GOS2.0/Artur-WAV
csv_dir=$3      #./data/gos_processed/Artur-J/csv

counter=0
for textgrid_file in $textgrid_dir/*.TextGrid; do
    counter=$((counter + 1))
    if [ $counter -ge 1 ]; then
        base_name=$(basename $textgrid_file)
        wav_file=$wav_dir/${base_name/.TextGrid/.wav}
        csv_file=$csv_dir/${base_name/.TextGrid/.csv}
        echo -e "\nFiles ($counter):"
        echo wav_file=\"$wav_file\"
        echo textgrid_file=\"$textgrid_file\"
        echo csv_file=\"$csv_file\"
        echo -e "Performing acoustic measurements ..."
        python acoustic_measurements.py $textgrid_file $wav_file $csv_file
        #break
    fi
done
