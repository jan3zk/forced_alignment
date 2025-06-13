#!/usr/bin/env python3
"""
Convert pronunciation dictionary to Montreal Forced Aligner (MFA) format.
"""

import argparse
import sys
from pathlib import Path


def load_phone_set(phone_set_file):
    """Load the phone set from a text file."""
    with open(phone_set_file, 'r', encoding='utf-8') as f:
        phones = set(line.strip() for line in f if line.strip())
    return phones


def parse_pronunciation(pron_string, phone_set, strict=False):
    """
    Parse a pronunciation string into individual phones.
    Uses a greedy approach to match the longest possible phone first.
    
    Args:
        pron_string: The pronunciation string to parse
        phone_set: Set of valid phones
        strict: If True, return None when unrecognized characters are found
    
    Returns:
        List of phones, or None if strict=True and unrecognized characters found
    """
    phones = []
    i = 0
    has_errors = False
    
    # Convert phone_set to a sorted list (longest first) for better matching
    sorted_phones = sorted(phone_set, key=len, reverse=True)
    
    while i < len(pron_string):
        matched = False
        
        # Try each phone in order (longest first)
        for phone in sorted_phones:
            if pron_string[i:].startswith(phone):
                phones.append(phone)
                i += len(phone)
                matched = True
                break
        
        if not matched:
            has_errors = True
            # If no match found, skip this character
            print(f"Warning: Unrecognized character '{pron_string[i]}' at position {i} in pronunciation '{pron_string}'", file=sys.stderr)
            # Also show what comes next for context
            context = pron_string[max(0, i-2):min(len(pron_string), i+3)]
            print(f"  Context: ...{context}...", file=sys.stderr)
            
            if strict:
                return None
            
            i += 1
    
    return phones


def convert_dictionary(input_file, output_file, phone_set_file, debug=False, strict=False):
    """Convert the dictionary from the original format to MFA format."""
    # Load phone set
    phone_set = load_phone_set(phone_set_file)
    
    if debug:
        print(f"Loaded {len(phone_set)} phones from phone set file", file=sys.stderr)
        # Show phones with quotes and colons for debugging
        quote_phones = [p for p in phone_set if '"' in p or ':' in p]
        if quote_phones:
            print(f"Phones containing quotes or colons: {sorted(quote_phones)}", file=sys.stderr)
    
    skipped_count = 0
    processed_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            line = line.strip()
            if not line:
                continue
            
            # Split word and pronunciations
            parts = line.split('\t')
            if len(parts) != 2:
                print(f"Warning: Line {line_num} has unexpected format: {line}", file=sys.stderr)
                continue
            
            word = parts[0]
            pronunciations = parts[1]
            
            # Split multiple pronunciations by comma
            pron_variants = [p.strip() for p in pronunciations.split(',')]
            
            for pron in pron_variants:
                # Parse the pronunciation into individual phones
                phones = parse_pronunciation(pron, phone_set, strict)
                
                if phones:
                    # Write to output file
                    outfile.write(f"{word}\t{' '.join(phones)}\n")
                    processed_count += 1
                else:
                    if strict:
                        print(f"Skipped: word '{word}' with pronunciation '{pron}' due to unrecognized characters", file=sys.stderr)
                        skipped_count += 1
                    else:
                        print(f"Warning: No valid phones found for word '{word}' with pronunciation '{pron}'", file=sys.stderr)
    
    print(f"\nProcessed {processed_count} pronunciation entries", file=sys.stderr)
    if strict and skipped_count > 0:
        print(f"Skipped {skipped_count} entries due to unrecognized characters", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Convert pronunciation dictionary to Montreal Forced Aligner (MFA) format"
    )
    parser.add_argument(
        "input_dict",
        help="Input dictionary file"
    )
    parser.add_argument(
        "phone_set",
        help="Phone set file (text file with one phone per line)"
    )
    parser.add_argument(
        "output_dict",
        help="Output dictionary file in MFA format"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Skip entries with unrecognized characters (default: include partial matches)"
    )
    
    args = parser.parse_args()
    
    # Check if input files exist
    if not Path(args.input_dict).exists():
        print(f"Error: Input dictionary file '{args.input_dict}' not found", file=sys.stderr)
        sys.exit(1)
    
    if not Path(args.phone_set).exists():
        print(f"Error: Phone set file '{args.phone_set}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Convert the dictionary
    convert_dictionary(args.input_dict, args.output_dict, args.phone_set, args.debug, args.strict)
    print(f"Conversion complete. Output written to '{args.output_dict}'")


if __name__ == "__main__":
    main()
    