import json
import os
import glob
import sys
from transcript_from_tei import transcript_from_tei

def create_nemo_manifest(wav_file, xml_file, manifest_file):
    text = transcript_from_tei(xml_file, True)
    data = {"audio_filepath": wav_file, "text": text}

    with open(manifest_file, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)

if __name__ == "__main__":
    # Call example:
    # python nemo_manifest.py "/storage/rsdo/korpus/GOS2.0/Artur-WAV/Artur-J*.wav" "./data/Gos.TEI.2.1/Artur-J/" "./data/nemo/input/Artur-J/"
    if len(sys.argv) != 4:
        print("Usage: python nemo_manifest.py <wav_directory> <xml_directory> <manifest_directory>")
        sys.exit(1)

    wav_directory = sys.argv[1]
    xml_directory = sys.argv[2]
    manifest_directory = sys.argv[3]

    # Create manifest for each WAV file in the directory
    for wav_file in glob.glob(wav_directory):
        #base_name = os.path.basename(wav_file).replace(".wav", "")[:-4] #additional "-avd" in name
        base_name = os.path.basename(wav_file).replace(".wav", "") #without additional "-avd" in name
        xml_file = os.path.join(xml_directory, base_name + ".xml")
        manifest_file = os.path.join(manifest_directory, base_name + ".json")

        if os.path.exists(xml_file):
            create_nemo_manifest(wav_file, xml_file, manifest_file)
            print(f"Manifest created for {wav_file}")
        else:
            print(f"XML file not found for {wav_file}")
