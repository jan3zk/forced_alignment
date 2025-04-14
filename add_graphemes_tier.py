import sys
import os
from textgrid import TextGrid, IntervalTier, Interval
from collections import defaultdict
import re

def initialize_phoneme_grapheme_map():
    """Initialize a mapping between phonemes and potential graphemes in Slovene"""
    # Core mappings based on Slovene phonology
    # Each phoneme maps to one or more possible graphemes
    pg_map = {
        # Vowels
        "a": ["a"],
        "\"a": ["a"],
        "\"a:": ["a"],
        "e": ["e"],
        "\"e": ["e"],
        "\"e:": ["e"],
        "E": ["e"],
        "\"E": ["e"],
        "\"E:": ["e"],
        "@": ["e", ""],  # Schwa can be 'e' or silent
        "\"@": ["e", ""],
        "i": ["i"],
        "\"i": ["i"],
        "\"i:": ["i"],
        "I": ["i"],
        "o": ["o"],
        "\"o": ["o"],
        "\"o:": ["o"],
        "O": ["o"],
        "\"O": ["o"],
        "\"O:": ["o"],
        "u": ["u"],
        "\"u": ["u"],
        "\"u:": ["u"],
        
        # Consonants
        "p": ["p"],
        "p_n": ["p"],
        "p_f": ["p"],
        "b": ["b"],
        "b_n": ["b"],
        "b_f": ["b"],
        "t": ["t"],
        "t_l": ["t"],
        "t_n": ["t"],
        "d": ["d"],
        "d_l": ["d"],
        "d_n": ["d"],
        "k": ["k"],
        "g": ["g"],
        "f": ["f"],
        "F": ["f"],
        "v": ["v"],
        "w": ["v", "l"],  # 'w' can map to 'v' or word-final 'l'
        "W": ["v"],
        "U": ["v"],
        "s": ["s", "z"],  # 's' can map to 's' or 'z' depending on context
        "z": ["z"],
        "S": ["š"],
        "Z": ["ž"],
        "x": ["h"],
        "G": ["h"],
        "h": ["h"],
        "ts": ["c"],
        "tS": ["č"],
        "m": ["m"],
        "n": ["n"],
        "n'": ["nj"],
        "N": ["n"],
        "l": ["l"],
        "l'": ["lj"],
        "r": ["r"],
        "j": ["j"],
        
        # Special contexts
        "spn": [""],  # Special non-speech
    }
    return pg_map

def get_pronunciation_dict(dict_path):
    """Load a pronunciation dictionary from file"""
    pron_dict = {}
    try:
        with open(dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    word = parts[0].lower()
                    phonemes = parts[1:]
                    pron_dict[word] = phonemes
    except FileNotFoundError:
        print(f"Warning: Dictionary file {dict_path} not found. Using default mappings only.")
    return pron_dict

def align_phonemes_to_graphemes(word, phonemes):
    """
    Align phonemes to graphemes with improved Slovenian-specific mappings.
    
    Args:
        word (str): The original word
        phonemes (list): List of phoneme strings
    
    Returns:
        list: List of grapheme strings aligned with phonemes
    """
    if not word or not phonemes:
        return [""] * len(phonemes)
    
    word = word.lower()
    pg_map = initialize_phoneme_grapheme_map()
    result = [""] * len(phonemes)
    
    # Special case handling for single-character words
    if len(word) == 1:
        if word == "v" and len(phonemes) == 1:
            return ["v"]  # Always map single "v" to "v", not "u"
        elif word == "d" and len(phonemes) == 1:
            return ["d"]  # Always map single "d" to "d", not "t"
    
    # Step 1: First pass - handle basic mappings
    for i, phoneme in enumerate(phonemes):
        # Skip special cases for now
        if phoneme == "spn":
            result[i] = ""
            continue
        
        # Get possible graphemes for this phoneme
        possible_graphemes = pg_map.get(phoneme, [phoneme])
        
        # Handle specific phoneme cases
        if phoneme == "Z":
            # Z should always map to ž
            result[i] = "ž"
        elif phoneme == "@":
            # Add special case for words with "l@j" sequence - schwa is silent here
            if i > 0 and i < len(phonemes) - 1:
                if phonemes[i-1] == "l" and phonemes[i+1] == "j":
                    result[i] = ""
                    continue
                
                # Special case for "r@l" sequence - schwa is often silent
                if phonemes[i-1] == "r" and phonemes[i+1] == "l":
                    result[i] = ""
                    continue
                
                # Check if between consonants (likely to be silent)
                prev_is_consonant = phonemes[i-1] not in "aeiouAEIOU@"
                next_is_consonant = phonemes[i+1] not in "aeiouAEIOU@"
                
                if prev_is_consonant and next_is_consonant and phonemes[i+1] == "r":
                    # Special case for @r sequence - schwa is usually silent
                    result[i] = ""
                elif "e" in word:
                    # If 'e' is in the word, map schwa to 'e' UNLESS it's in a known silent context
                    if (i+1 < len(phonemes) and (phonemes[i+1] == "n" or phonemes[i+1] == "l")):
                        # Check if this is part of words like "liberalne" where @ before n should be silent
                        result[i] = ""
                    else:
                        result[i] = "e"
                else:
                    # Otherwise, schwa is likely silent
                    result[i] = ""
            else:
                # At beginning or end, default to 'e' if in word
                if "e" in word:
                    result[i] = "e"
                else:
                    result[i] = ""
        else:
            # For all other phonemes, use the first (most common) grapheme
            if possible_graphemes:
                result[i] = possible_graphemes[0]
            else:
                # Fallback - use the phoneme itself
                result[i] = phoneme
    
    # Step 2: Second pass - apply Slovenian-specific rules
    
    # A. Handle 'w' at the end of words that should map to 'l'
    for i in range(len(phonemes)):
        if phonemes[i] == "w" and i == len(phonemes) - 1:  # Last phoneme
            # Check if word ends with 'l' - common pattern in Slovenian past tense
            if word.endswith('l'):
                result[i] = "l"
            # Check endings like -il, -el, -al which are common verb forms
            elif word.endswith('il') or word.endswith('el') or word.endswith('al') or word.endswith('ul'):
                result[i] = "l"
    
    # B. Handle 's' that should be 'z' in certain contexts
    for i in range(len(phonemes)):
        if phonemes[i] == "s":
            # Words like "iz", "jaz" where 's' should be 'z'
            if word == "iz" or word == "jaz":
                result[i] = "z"
            # 'is' at the beginning of words like "izhaja", "iskati"
            elif i == 1 and i < len(phonemes) - 1 and phonemes[0] == "i":
                # Check if original word starts with "iz" not "is"
                if word.startswith("iz"):
                    result[i] = "z"
            # Check for 'raz' prefix
            elif i > 0 and i < len(phonemes) - 1 and "".join(phonemes[i-1:i+2]) == "ras":
                if word.startswith("raz"):
                    result[i] = "z"
    
    # C. Handle 'ts' sequences (always 'c' in Slovenian)
    for i in range(len(phonemes)):
        if phonemes[i] == "ts":
            result[i] = "c"
    
    # D. Handle 'g' vs 'k' (phonetic differences in words like "kdo")
    for i in range(len(phonemes)):
        if phonemes[i] == "g" and word.startswith("k"):
            if i == 0:  # First phoneme
                result[i] = "k"
    
    # E. Handle "obs" vs "ops" sequences
    for i in range(len(phonemes) - 2):
        if "".join(phonemes[i:i+3]) == "Ops" and word.startswith("obs"):
            result[i] = "o"
            result[i+1] = "b"
            result[i+2] = "s"
    
    # F. Handle 'p' at the end of words that should be 'b'
    for i in range(len(phonemes)):
        if phonemes[i] == "p" and i == len(phonemes) - 1:  # Last phoneme
            if word.endswith('b'):
                result[i] = "b"
    
    # G. Handle 'w' at the beginning of words (often maps to 'v')
    for i in range(len(phonemes)):
        if phonemes[i] == "w" and i == 0:  # First phoneme
            if word.startswith('v'):
                result[i] = "v"
    
    # H. Handle common Slovenian prefixes
    prefixes = {
        "vz": ["w", "s"],  # vzpon → 'w s' should be 'vz'
        "iz": ["i", "s"],  # izhaja → 'i s' should be 'iz'
        "raz": ["r", "a", "s"],  # razprava → 'r a s' should be 'raz'
        "obs": ["O", "p", "s"],  # obstaja → 'O p s' should be 'obs'
    }
    
    for prefix, phoneme_pattern in prefixes.items():
        if word.startswith(prefix) and len(phonemes) >= len(phoneme_pattern):
            prefix_match = True
            for i, p in enumerate(phoneme_pattern):
                if i >= len(phonemes) or phonemes[i] != p:
                    prefix_match = False
                    break
            
            if prefix_match:
                # Map the prefix phonemes to the correct orthography
                for i, char in enumerate(prefix):
                    if i < len(result):
                        result[i] = char
    
    # I. Apply generic rule for @ before 'l', 'j', or 'n' in specific patterns
    # This covers the examples and similar words
    for i in range(len(phonemes) - 1):
        if phonemes[i] == "@" and i > 0:
            if (phonemes[i+1] == "j" or phonemes[i+1] == "l" or phonemes[i+1] == "n"):
                # Make schwa silent in these contexts
                result[i] = ""
    
    return result

def add_phoneme_grapheme_mapping_tier(input_textgrid, output_textgrid, dict_path=None):
    """
    Add a tier showing graphemes mapping to a TextGrid file
    with improved Slovenian-specific mappings
    """
    # Load the pronunciation dictionary if provided
    pron_dict = get_pronunciation_dict(dict_path) if dict_path else None
    
    # Load the TextGrid
    try:
        tg = TextGrid.fromFile(input_textgrid)
    except Exception as e:
        print(f"Error loading TextGrid file: {e}")
        return False
    
    # Get necessary tiers
    phone_tier = None
    phone_tier_index = None
    word_tier = None
    
    # Look for phone and word tiers
    for i, tier in enumerate(tg.tiers):
        if tier.name == "phones":
            phone_tier = tier
            phone_tier_index = i
        elif tier.name in ["words", "strd-wrd-sgmnt"]:
            word_tier = tier
    
    if not phone_tier or not word_tier:
        print("Error: Required tiers 'phones' and 'words'/'strd-wrd-sgmnt' not found in TextGrid")
        return False
    
    # Create a new tier for graphemes
    mapping_tier = IntervalTier(name="graphemes", 
                               minTime=phone_tier.minTime, 
                               maxTime=phone_tier.maxTime)
    
    # Dictionary to track failed mappings for analysis
    failed_mappings = []
    
    # Process each word
    for word_interval in word_tier:
        word = word_interval.mark.strip()
        if not word:  # Skip empty intervals
            continue
        
        # Find all phonemes in this word's time range
        word_phonemes = []
        for phone_interval in phone_tier:
            # Check if the phone is within or overlaps with the word
            if (phone_interval.minTime >= word_interval.minTime and 
                phone_interval.maxTime <= word_interval.maxTime):
                word_phonemes.append(phone_interval)
        
        # Skip if no phonemes found for this word
        if not word_phonemes:
            continue
        
        # Get phoneme texts
        phoneme_texts = [p.mark for p in word_phonemes]
        
        # Align phonemes to graphemes with improved Slovenian-specific rules
        graphemes = align_phonemes_to_graphemes(word, phoneme_texts)
        
        # Add intervals to the new tier while preserving time alignment
        for i, phone_interval in enumerate(word_phonemes):
            if i < len(graphemes):
                mapping_tier.addInterval(
                    Interval(phone_interval.minTime, phone_interval.maxTime, graphemes[i])
                )
        
        # Check mapping quality for reporting
        reconstructed = ''.join(graphemes)
        if reconstructed.lower() != word.lower():
            phonetic = ' '.join(phoneme_texts)
            failed_mappings.append(f"  '{word}' → '{phonetic}' → '{reconstructed}'")
    
    # Add the new tier right after the phones tier
    tg.tiers.insert(phone_tier_index + 1, mapping_tier)
    
    # Save the modified TextGrid
    try:
        tg.write(output_textgrid)
        print(f"Graphemes tier added. TextGrid saved to {output_textgrid}")
        
        # Print failed mappings report if any
        if failed_mappings:
            print("\nFailed mapping examples:")
            for mapping in failed_mappings:
                print(mapping)
        return True
    except Exception as e:
        print(f"Error saving TextGrid file: {e}")
        return False

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 3:
        print("Usage: python add_phoneme_grapheme_mapping_tier.py [input.TextGrid] [output.TextGrid] [dictionary.txt]")
        sys.exit(1)
    
    input_textgrid = sys.argv[1]
    output_textgrid = sys.argv[2]
    dict_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    success = add_phoneme_grapheme_mapping_tier(input_textgrid, output_textgrid, dict_path)
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()