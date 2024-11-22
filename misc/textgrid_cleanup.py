import argparse
import os
from textgrid import TextGrid

def transform_textgrid(input_file, output_file):
    # Preberi TextGrid datoteko
    tg = TextGrid.fromFile(input_file)

    # Poišči in pridobi vrstico "actualDM"
    actualDM_tier = None
    for tier in tg.tiers:
        if tier.name == "actualDM":
            # Kopiraj vrstico za kasnejšo uporabo in posodobi oznake
            actualDM_tier = tier
            for interval in actualDM_tier.intervals:
                if interval.mark == "af":
                    interval.mark = "POS"
            break

    # Če "actualDM" ne obstaja, sproži napako
    if not actualDM_tier:
        raise ValueError("Vrstica 'actualDM' ni prisotna v vhodni datoteki.")

    # Odstrani vrstico "discourse-marker"
    tg.tiers = [tier for tier in tg.tiers if tier.name != "discourse-marker"]

    # Dodaj spremenjeno vrstico "actualDM" kot novo 4. vrstico (indeks 3)
    tg.tiers.insert(3, actualDM_tier)

    # Izbriši vrstico z imenom "argument"
    tg.tiers = [tier for tier in tg.tiers if tier.name != "argument"]

    # Izbriši vrstico z imenom "actual-DM-classification"
    tg.tiers = [tier for tier in tg.tiers if tier.name != "actual-DM-classif"]

    # Izbriši vrstico z imenom "confidence level" (vedno zadnja vrstica)
    if tg.tiers and tg.tiers[-1].name == "confidence-level":
        tg.tiers.pop()

    # Odstrani zadnjo pojavitve "actualDM", če je podvojena
    actualDM_count = sum(1 for tier in tg.tiers if tier.name == "actualDM")
    if actualDM_count > 1:
        # Poiščemo indeks zadnje pojavitve in jo odstranimo
        for i in range(len(tg.tiers) - 1, -1, -1):
            if tg.tiers[i].name == "actualDM":
                tg.tiers.pop(i)
                break

    # Shrani transformirano TextGrid datoteko
    tg.write(output_file)

def transform_directory(input_dir, output_dir):
    # Preveri, če izhodni direktorij obstaja, sicer ga ustvari
    os.makedirs(output_dir, exist_ok=True)

    # Iteriraj čez vse datoteke v vhodnem direktoriju
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".textgrid"):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, filename)
            print(f"Processing: {input_file} -> {output_file}")
            try:
                transform_textgrid(input_file, output_file)
            except Exception as e:
                print(f"Error processing {input_file}: {e}")

def main():
    # Ustvari parser za argumente
    parser = argparse.ArgumentParser(description="Transformiraj TextGrid datoteko ali vse datoteke v direktoriju.")
    parser.add_argument("input_path", help="Pot do vhodne datoteke ali direktorija.")
    parser.add_argument("output_path", help="Pot do izhodne datoteke ali direktorija.")
    args = parser.parse_args()

    # Preveri, ali je vhodna pot datoteka ali direktorij
    if os.path.isfile(args.input_path):
        # Če gre za datoteko, transformiraj eno datoteko
        transform_textgrid(args.input_path, args.output_path)
    elif os.path.isdir(args.input_path):
        # Če gre za direktorij, transformiraj vse TextGrid datoteke v direktoriju
        transform_directory(args.input_path, args.output_path)
    else:
        print("Napaka: Vhodna pot ni veljavna datoteka ali direktorij.")

if __name__ == "__main__":
    main()
