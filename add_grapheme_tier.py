import sys
import os
from textgrid import TextGrid, IntervalTier, Interval
import difflib
from collections import defaultdict

def initialize_phoneme_grapheme_map():
    """Initialize a mapping between phonemes and potential graphemes in Slovene"""
    # Core mappings based on Slovene phonology
    # Each phoneme can map to multiple possible graphemes
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
        "@": ["e"],
        "\"@": ["e"],
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
        "w": ["v"],
        "W": ["v"],
        "U": ["v"],
        "s": ["s"],
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
        # Special combinations
        "v@": ["v"],  # Syllabic v
        "r@": ["r"],  # Syllabic r
        "@r": ["r"],  # Alternative syllabic r
        "l@": ["l"],  # Syllabic l
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

def merge_phoneme_sequences(phonemes):
    """Merge phoneme sequences based on known patterns"""
    merged_phonemes = []
    i = 0
    
    while i < len(phonemes):
        # Handle common special cases
        if i < len(phonemes) - 1 and phonemes[i] == "v" and phonemes[i+1] == "@":
            merged_phonemes.append("v@")
            i += 2
        elif i < len(phonemes) - 1 and phonemes[i] == "r" and phonemes[i+1] == "@":
            merged_phonemes.append("r@")
            i += 2
        elif i < len(phonemes) - 1 and phonemes[i] == "@" and phonemes[i+1] == "r":
            merged_phonemes.append("@r")
            i += 2
        elif i < len(phonemes) - 1 and phonemes[i] == "l" and phonemes[i+1] == "@":
            merged_phonemes.append("l@")
            i += 2
        else:
            merged_phonemes.append(phonemes[i])
            i += 1
    
    return merged_phonemes

def align_phonemes_to_graphemes(word, phonemes, pg_map, pron_dict=None):
    """
    Align phonemes to graphemes using a combination of dictionary lookup and rule-based mapping.
    
    Args:
        word (str): The word in orthographic form
        phonemes (list): List of phonemes
        pg_map (dict): Phoneme-to-grapheme mapping dictionary
        pron_dict (dict): Pronunciation dictionary
        
    Returns:
        list: List of tuples (phoneme, corresponding_grapheme)
    """
    word = word.lower()
    
    # Merge phoneme sequences that should be treated as a unit
    merged_phonemes = merge_phoneme_sequences(phonemes)
    
    # Check if we have this word in our pronunciation dictionary
    if pron_dict and word in pron_dict:
        dict_phonemes = pron_dict[word]
        # Merge dictionary phonemes too
        merged_dict_phonemes = merge_phoneme_sequences(dict_phonemes)
        # If the phoneme counts match exactly, we can use the dictionary pronunciation
        if len(merged_dict_phonemes) == len(merged_phonemes):
            return align_using_dictionary(word, merged_phonemes, merged_dict_phonemes, pg_map)
    
    # Fall back to sequence alignment approach
    return align_sequences(word, merged_phonemes, pg_map)

def align_using_dictionary(word, phonemes, dict_phonemes, pg_map):
    """
    Align phonemes to graphemes using dictionary pronunciation as a guide
    """
    # Create character alignment table based on dictionary pronunciation
    chars = list(word)
    char_index = 0
    mappings = []

    # For each phoneme in the dictionary pronunciation
    for i, dict_phoneme in enumerate(dict_phonemes):
        # Skip any phones that couldn't be aligned (this is a rough heuristic)
        if i >= len(phonemes):
            continue
            
        actual_phoneme = phonemes[i]
        
        # Find possible graphemes for this phoneme
        possible_graphemes = pg_map.get(dict_phoneme, [dict_phoneme])
        
        # Try to find the corresponding grapheme in the word
        grapheme = ""
        for possible in possible_graphemes:
            # Make sure we don't go out of bounds
            if char_index < len(chars):
                # Simple case: direct match
                if chars[char_index] == possible:
                    grapheme = chars[char_index]
                    char_index += 1
                    break
                # Handle digraphs
                elif char_index + len(possible) <= len(chars) and ''.join(chars[char_index:char_index+len(possible)]) == possible:
                    grapheme = possible
                    char_index += len(possible)
                    break
                # If no match, just use the current character
                else:
                    grapheme = chars[char_index] if char_index < len(chars) else ""
                    char_index += 1
        
        mappings.append((actual_phoneme, grapheme))
    
    return mappings

def align_sequences(word, phonemes, pg_map):
    """
    Align phonemes to graphemes using sequence alignment techniques
    when dictionary lookup fails
    """
    chars = list(word)
    
    # Initialize mapping list
    mappings = []
    
    # Use a greedy approach: assign each phoneme to the next available grapheme
    char_index = 0
    for phoneme in phonemes:
        possible_graphemes = pg_map.get(phoneme, [phoneme])
        
        # Try to find a match in the remaining word
        best_match = ""
        best_match_len = 0
        
        for possible in possible_graphemes:
            if char_index < len(chars):
                # Check if the current character matches the start of this possible grapheme
                if possible.startswith(chars[char_index]):
                    if len(possible) > best_match_len:
                        best_match = possible
                        best_match_len = len(possible)
        
        # If we found a match, use it
        if best_match:
            mappings.append((phoneme, best_match))
            char_index += len(best_match)
        # Otherwise, assign the next character if available
        elif char_index < len(chars):
            mappings.append((phoneme, chars[char_index]))
            char_index += 1
        # If we've run out of characters, use empty string
        else:
            mappings.append((phoneme, ""))
    
    # If we have leftover characters, distribute them to the last phoneme
    if char_index < len(chars):
        phoneme, grapheme = mappings[-1]
        mappings[-1] = (phoneme, grapheme + ''.join(chars[char_index:]))
    
    return mappings

def add_phoneme_grapheme_mapping_tier(input_textgrid, output_textgrid, dict_path=None):
    """
    Add a tier showing graphemes mapping to a TextGrid file
    
    Args:
        input_textgrid (str): Path to input TextGrid file
        output_textgrid (str): Path to output TextGrid file
        dict_path (str): Path to pronunciation dictionary file
    """
    # Initialize the phoneme-to-grapheme mapping
    pg_map = initialize_phoneme_grapheme_map()
    
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
        
        # Align phonemes to graphemes
        mapping = align_phonemes_to_graphemes(word, phoneme_texts, pg_map, pron_dict)
        
        # Create intervals for merged phoneme sequences
        i = 0
        while i < len(word_phonemes):
            phone_text = word_phonemes[i].mark
            
            # Handle merged phoneme sequences
            if i < len(word_phonemes) - 1 and phone_text == "v" and word_phonemes[i+1].mark == "@":
                # Create a single interval for "v@" -> "v"
                start_time = word_phonemes[i].minTime
                end_time = word_phonemes[i+1].maxTime
                grapheme = pg_map.get("v@", ["v"])[0]
                mapping_tier.addInterval(Interval(start_time, end_time, grapheme))
                i += 2
            elif i < len(word_phonemes) - 1 and phone_text == "r" and word_phonemes[i+1].mark == "@":
                # Create a single interval for "r@" -> "r"
                start_time = word_phonemes[i].minTime
                end_time = word_phonemes[i+1].maxTime
                grapheme = pg_map.get("r@", ["r"])[0]
                mapping_tier.addInterval(Interval(start_time, end_time, grapheme))
                i += 2
            elif i < len(word_phonemes) - 1 and phone_text == "@" and word_phonemes[i+1].mark == "r":
                # Create a single interval for "@r" -> "r"
                start_time = word_phonemes[i].minTime
                end_time = word_phonemes[i+1].maxTime
                grapheme = pg_map.get("@r", ["r"])[0]
                mapping_tier.addInterval(Interval(start_time, end_time, grapheme))
                i += 2
            elif i < len(word_phonemes) - 1 and phone_text == "l" and word_phonemes[i+1].mark == "@":
                # Create a single interval for "l@" -> "l"
                start_time = word_phonemes[i].minTime
                end_time = word_phonemes[i+1].maxTime
                grapheme = pg_map.get("l@", ["l"])[0]
                mapping_tier.addInterval(Interval(start_time, end_time, grapheme))
                i += 2
            else:
                # Regular single phoneme mapping
                if i < len(mapping):
                    grapheme = mapping[i][1]
                    mapping_tier.addInterval(
                        Interval(word_phonemes[i].minTime, word_phonemes[i].maxTime, grapheme)
                    )
                i += 1
    
    # Add the new tier right after the phones tier
    tg.tiers.insert(phone_tier_index + 1, mapping_tier)
    
    # Save the modified TextGrid
    try:
        tg.write(output_textgrid)
        print(f"Graphemes tier added. TextGrid saved to {output_textgrid}")
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