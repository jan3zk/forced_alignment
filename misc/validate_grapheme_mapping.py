import sys
import os
from textgrid import TextGrid
import difflib
from collections import defaultdict

def validate_grapheme_mapping(input_textgrid, verbose=False):
    """
    Validates the phoneme-to-grapheme mapping by checking if the mapped graphemes 
    can reconstruct the original word.
    
    Args:
        input_textgrid (str): Path to input TextGrid file with 'graphemes' tier
        verbose (bool): If True, prints detailed matching information
        
    Returns:
        dict: Statistics and results of the validation
    """
    try:
        tg = TextGrid.fromFile(input_textgrid)
    except Exception as e:
        print(f"Error loading TextGrid file: {e}")
        return None
    
    # Find required tiers
    word_tier = None
    grapheme_tier = None
    phone_tier = None
    
    for tier in tg.tiers:
        if tier.name in ["words", "strd-wrd-sgmnt"]:
            word_tier = tier
        elif tier.name == "graphemes":
            grapheme_tier = tier
        elif tier.name == "phones":
            phone_tier = tier
    
    if not word_tier or not grapheme_tier or not phone_tier:
        print("Error: Required tiers not found in TextGrid")
        return None
    
    total_words = 0
    exact_matches = 0
    close_matches = 0  # Words with a similarity > 0.8 but not exact match
    failed_matches = 0
    
    match_examples = []
    fail_examples = []
    
    # Process each word
    for word_interval in word_tier:
        original_word = word_interval.mark.strip().lower()
        
        # Skip empty intervals
        if not original_word:
            continue
        
        total_words += 1
        
        # Find all grapheme intervals within this word's time span
        word_graphemes = []
        for grapheme_interval in grapheme_tier:
            # Check if the grapheme interval is within the word interval
            if (grapheme_interval.minTime >= word_interval.minTime and 
                grapheme_interval.maxTime <= word_interval.maxTime):
                if grapheme_interval.mark:  # Only include non-empty graphemes
                    word_graphemes.append(grapheme_interval.mark)
        
        # Find all phone intervals within this word's time span
        word_phones = []
        for phone_interval in phone_tier:
            # Check if the phone interval is within the word interval
            if (phone_interval.minTime >= word_interval.minTime and 
                phone_interval.maxTime <= word_interval.maxTime):
                if phone_interval.mark:  # Only include non-empty phones
                    word_phones.append(phone_interval.mark)
        
        # Reconstruct the word from graphemes
        reconstructed_word = ''.join(word_graphemes).lower()
        # Combine phones into a string
        phones_string = ' '.join(word_phones)
        
        # Calculate similarity ratio
        similarity = difflib.SequenceMatcher(None, original_word, reconstructed_word).ratio()
        
        # Check for exact match
        if reconstructed_word == original_word:
            exact_matches += 1
            if len(match_examples) < 5:
                match_examples.append((original_word, phones_string, reconstructed_word))
        # Check for close match
        elif similarity >1.0:
            close_matches += 1
            if len(match_examples) < 100:
                match_examples.append((original_word, phones_string, reconstructed_word, similarity))
        # Failed match
        else:
            failed_matches += 1
            #if len(fail_examples) < 100:
            fail_examples.append((original_word, phones_string, reconstructed_word, similarity))
        
        if verbose:
            print(f"Word: '{original_word}' → Phones: '{phones_string}' → Reconstructed: '{reconstructed_word}' (Similarity: {similarity:.2f})")
    
    # Calculate success rates
    exact_match_rate = exact_matches / total_words if total_words > 0 else 0
    overall_success_rate = (exact_matches + close_matches) / total_words if total_words > 0 else 0
    
    # Prepare results
    results = {
        "total_words": total_words,
        "exact_matches": exact_matches,
        "close_matches": close_matches,
        "failed_matches": failed_matches,
        "exact_match_rate": exact_match_rate,
        "overall_success_rate": overall_success_rate,
        "match_examples": match_examples,
        "fail_examples": fail_examples
    }
    
    return results

def print_results(results):
    """Print validation results in a readable format"""
    if not results:
        return
    
    print("\n--- Phoneme-to-Grapheme Mapping Validation Results ---")
    print(f"Total words analyzed: {results['total_words']}")
    print(f"Exact matches: {results['exact_matches']} ({results['exact_match_rate']:.2%})")
    print(f"Close matches: {results['close_matches']} ({results['close_matches']/results['total_words']:.2%})")
    print(f"Failed matches: {results['failed_matches']} ({results['failed_matches']/results['total_words']:.2%})")
    print(f"Overall success rate: {results['overall_success_rate']:.2%}")
    
    #if results['match_examples']:
    #    print("\nSuccessful mapping examples:")
    #    for example in results['match_examples']:
    #        if len(example) == 3:
    #            print(f"  '{example[0]}' → '{example[1]}' → '{example[2]}' (Exact match)")
    #        else:
    #            print(f"  '{example[0]}' → '{example[1]}' → '{example[2]}' (Similarity: {example[3]:.2f})")
    
    if results['fail_examples']:
        print("\nFailed mapping examples:")
        for example in results['fail_examples']:
            print(f"  '{example[0]}' → '{example[1]}' → '{example[2]}' (Similarity: {example[3]:.2f})")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Usage: python validate_grapheme_mapping.py [input.TextGrid] [--verbose]")
        sys.exit(1)
    
    input_textgrid = sys.argv[1]
    verbose = "--verbose" in sys.argv
    
    results = validate_grapheme_mapping(input_textgrid, verbose)
    print_results(results)

if __name__ == "__main__":
    main()