import argparse
import os
import sys

def check_tiers_in_textgrid(file_path, tiers_to_check):
    """
    Checks if the specified tiers are present in the TextGrid file.

    :param file_path: Path to the TextGrid file.
    :param tiers_to_check: List of tier names to check.
    :return: Dictionary with tier names as keys and boolean values indicating their presence.
    """
    # Read the TextGrid file
    with open(file_path, 'r') as file:
        textgrid_content = file.read()

    # Dictionary to store the presence of tiers
    tiers_presence = {tier: False for tier in tiers_to_check}

    # Check for each tier in the file
    for tier in tiers_to_check:
        if tier in textgrid_content:
            tiers_presence[tier] = True

    return tiers_presence

def process_directory(directory, tiers_to_check):
    """
    Process all TextGrid files in the given directory.

    :param directory: Directory containing TextGrid files.
    :param tiers_to_check: List of tiers to check.
    :return: True if all tiers are present in all files, False otherwise.
    """
    all_tiers_present = True
    for filename in os.listdir(directory):
        if filename.endswith('.TextGrid'):
            file_path = os.path.join(directory, filename)
            print(f"\nChecking file: {filename}")
            tiers_presence = check_tiers_in_textgrid(file_path, tiers_to_check)
            for tier, is_present in tiers_presence.items():
                if not is_present:
                    print(f"Error: Tier '{tier}' not present in {filename}")
                    all_tiers_present = False
    return all_tiers_present

def main():
    # The script is designed to check for the presence of specified tiers in TextGrid files.

    # Call example:
    # python check_tiers.py data/iriss_processed/TextGrid_final/ speaker-ID standardized-trs strd-wrd-sgmnt discourse-marker conversational-trs word-ID cnvrstl-wrd-sgmnt cnvrstl-syllables phones pitch-reset intensity-reset speech-rate-reduction pause speaker-change

    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Check for specified tiers in a TextGrid file or all TextGrid files in a directory.')
    parser.add_argument('path', type=str, help='Path to the TextGrid file or directory.')
    parser.add_argument('tiers', nargs='+', help='List of tiers to check.')

    # Parse arguments
    args = parser.parse_args()

    all_tiers_present = True

    # Check if the path is a file or a directory
    if os.path.isfile(args.path):
        # Single file
        print(f"\nChecking file: {args.path}")
        tiers_presence = check_tiers_in_textgrid(args.path, args.tiers)
        for tier, is_present in tiers_presence.items():
            if not is_present:
                print(f"Error: Tier '{tier}' not present in {args.path}")
                all_tiers_present = False
    elif os.path.isdir(args.path):
        # Directory
        all_tiers_present = process_directory(args.path, args.tiers)
    else:
        print("The specified path is neither a file nor a directory.")
        sys.exit(1)

    if not all_tiers_present:
        sys.exit(1)

if __name__ == '__main__':
    main()
