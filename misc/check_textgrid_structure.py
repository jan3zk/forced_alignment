import os
import argparse
from textgrid import TextGrid

def get_tier_structure(file_path):
    """
    Vrne seznam imen vrstic (tiers) iz TextGrid datoteke.
    """
    tg = TextGrid.fromFile(file_path)
    return [tier.name for tier in tg.tiers]

def compare_structures(reference, current):
    """
    Primerja dve strukturi in vrne opis razlik.
    """
    differences = []
    # Preveri manjkajoče vrstice
    for tier in reference:
        if tier not in current:
            differences.append(f"Manjka vrstica: {tier}")
    # Preveri presežne vrstice
    for tier in current:
        if tier not in reference:
            differences.append(f"Dodatna vrstica: {tier}")
    # Preveri neskladja v vrstnem redu
    if reference != current:
        differences.append("Neskladen vrstni red vrstic")
    return differences

def check_textgrid_structure(directory):
    """
    Preveri, ali imajo vse TextGrid datoteke v direktoriju enako strukturo.
    """
    structures = {}
    mismatched_files = {}

    # Poišči vse TextGrid datoteke v direktoriju
    for filename in os.listdir(directory):
        if filename.lower().endswith(".textgrid"):
            file_path = os.path.join(directory, filename)

            try:
                # Pridobi strukturo trenutne datoteke
                tier_structure = get_tier_structure(file_path)

                # Shrani strukturo in preveri skladnost
                if not structures:
                    # Prva datoteka, nastavimo referenčno strukturo
                    structures = {"reference": tier_structure, "files": [filename]}
                else:
                    if tier_structure != structures["reference"]:
                        mismatched_files[filename] = compare_structures(
                            structures["reference"], tier_structure
                        )
                    else:
                        structures["files"].append(filename)

            except Exception as e:
                print(f"Napaka pri obdelavi {file_path}: {e}")

    # Rezultati
    print("\n--- Preverjanje strukture TextGrid datotek ---")
    if mismatched_files:
        print("Datoteke z neskladno strukturo:")
        for file, differences in mismatched_files.items():
            print(f"  - {file}")
            for diff in differences:
                print(f"    -> {diff}")
    else:
        print("Vse TextGrid datoteke imajo enako strukturo.")
    
    print("\nReferenčna struktura:")
    for i, tier in enumerate(structures.get("reference", [])):
        print(f"  {i + 1}. {tier}")
    
    return mismatched_files

def main():
    # Ustvari parser za argumente
    parser = argparse.ArgumentParser(description="Preveri strukturo TextGrid datotek v direktoriju.")
    parser.add_argument("directory", help="Pot do direktorija z TextGrid datotekami.")
    args = parser.parse_args()

    # Preveri, če je podana pot veljaven direktorij
    if not os.path.isdir(args.directory):
        print(f"Napaka: '{args.directory}' ni veljaven direktorij.")
        return

    # Preveri strukturo TextGrid datotek v direktoriju
    check_textgrid_structure(args.directory)

if __name__ == "__main__":
    main()
