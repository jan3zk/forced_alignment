def is_syllable_accented(syllable):
    """Function to determine if syllable is accentuated"""
    # accented_graphemes = [u'ŕ', u'á', u'ä', u'é', u'ë', u'ě', u'í', u'î', u'ó', u'ô', u'ö', u'ú', u'ü']
    #accented_graphemes = [u'ŕ', u'á', u'à', u'é', u'è', u'ê', u'í', u'ì', u'ó', u'ô', u'ò', u'ú', u'ù']
    accented_graphemes = ["á", "à", "Á", "À", "è", "é", "ê", "É", "È", "Ê",
                "í",  "ì", "Ì", "Í", "ó", "ò", "ô",
                "Ó", "Ò", "Ô", "ù", "ú", "Ù", "Ú",
                "ŕ", "Ŕ"]
    for grapheme in syllable:
        if grapheme in accented_graphemes:
            return True
    return False


def is_vowel(list_of_characters_in_word, position, vowels):
    """Function to determine whether a character is a vowel grapheme or a syllabic R"""
    # Check if the character is a vowel
    if list_of_characters_in_word[position] in vowels:
        return True
    # Check if the character is a syllabic R
    if (list_of_characters_in_word[position] == u'r' or list_of_characters_in_word[position] == u'R') and (position - 1 < 0 or list_of_characters_in_word[position - 1] not in vowels) and (
                        position + 1 >= len(list_of_characters_in_word) or list_of_characters_in_word[position + 1] not in vowels):
        return True
    return False


def get_vowel_graphemes():
    """Returns a list of vowel graphemes. This includes the accented 'r' grapheme."""
    return ['à', 'á', 'é', 'è', 'ê', 'ì', 'í', 'î', 'ó', 'ô', 'ò', 'ú', 'a', 'e', 'i', 'o', 'u', 'ŕ',
            'Á', 'É', 'Í', 'Ó', 'Ú', 'Ŕ', 'À', 'È', 'Ì', 'Ò', 'Ù', 'Ê', 'Ô', 'A', 'E', 'I', 'O', 'U']



def get_sonorant_graphemes():
    """Returns a list of sonorant graphemes. """
    return ['m', 'n', 'v', 'l', 'r', 'j', 'M', 'N', 'V', 'L', 'R', 'J']


def get_voiced_obstruent_graphemes():
    """Returns a list of voiced obstruent graphemes."""
    return ['b', 'd', 'z', 'ž', 'g', 'B', 'D', 'Z', 'Ž', 'G']


def get_voiceless_obstruent_graphemes():
    """Returns a list of voiceless obstruent graphemes."""
    return ['p', 't', 's', 'š', 'č', 'k', 'f', 'h', 'c', 'P', 'T', 'S', 'Š', 'Č', 'K', 'F', 'H', 'C']


def get_consonant_graphemes():
    """Returns a list of all consonant graphemes."""
    return ['m', 'n', 'v', 'l', 'r', 'j', 'b', 'd', 'z', 'ž', 'g', 'p', 't', 's', 'š', 'č', 'k', 'f', 'h', 'c',
            'M', 'N', 'V', 'L', 'R', 'J', 'B', 'D', 'Z', 'Ž', 'G', 'P', 'T', 'S', 'Š', 'Č', 'K', 'F', 'H', 'C']


def split_consonant_graphemes_between_syllables(consonants):
    """A function that splits consonants between syllable 1 and syllable 2."""
    # GET LISTS OF GRAPHEMES BY CATEGORY
    sonorant_graphemes = get_sonorant_graphemes()
    voiced_obstruent_graphemes = get_voiced_obstruent_graphemes()
    voiceless_obstruent_graphemes = get_voiceless_obstruent_graphemes()

    # If there are no consonant graphemes, return empty lists for syllable 1 and syllable 2
    if len(consonants) == 0:
        return [''], ['']

    # If there's only one consonant grapheme, attach it to syllable 2
    elif len(consonants) == 1:
        return [''], consonants

    # If there are more consonant graphemes, perform the following:
    else:
        split_options = []
        for i in range(len(consonants)-1):
            current_consonant_grapheme = consonants[i]
            next_consonant_grapheme = consonants[i+1]

            if current_consonant_grapheme in ['-', '_']:
                split_options.append([i, -1])
            # If the consonants are the same (oDDaja)
            elif current_consonant_grapheme == next_consonant_grapheme:
                split_options.append([i, 0])
            # Combination of sonorant + obstruent grapheme (objeM-Ka, soN-Da)
            elif current_consonant_grapheme in sonorant_graphemes:
                if next_consonant_grapheme in voiced_obstruent_graphemes or next_consonant_grapheme in voiceless_obstruent_graphemes:
                    split_options.append([i, 2])
                # TODO - ADD SONORANT + SONORANT (orvejski? Narvik - narviški?)
                elif next_consonant_grapheme in sonorant_graphemes:
                    split_options.append([i, 2])
            # Combination of two voiced obstruents (oD-Ganjati) or a voiced and a voiceless obstruent grapheme (oD-Kleniti)
            elif current_consonant_grapheme in voiced_obstruent_graphemes:
                if next_consonant_grapheme in voiced_obstruent_graphemes:
                    split_options.append([i, 1])
                elif next_consonant_grapheme in voiceless_obstruent_graphemes:
                    split_options.append([i, 3])
                # TODO - ADD VOICED OBSTRUENT + SONORANT
                elif next_consonant_grapheme in sonorant_graphemes:
                    split_options.append([i, 2])
            # Combination of a voiceless and a voiced obstruent grapheme (glas-Ba)
            elif current_consonant_grapheme in voiceless_obstruent_graphemes:
                if next_consonant_grapheme in voiced_obstruent_graphemes:
                    split_options.append([i, 4])
                # TODO - Add TWO VOICELESS OBSTRUENTS? (poS-Tulat)
                elif next_consonant_grapheme in voiceless_obstruent_graphemes:
                    split_options.append([i, 2])
                # TODO - Add VOICELESS OBSTRUENT + SONORANT
                #elif next_consonant_grapheme in sonorant_graphemes:
                #    split_options.append([i, 2])

        if split_options == []:
            return [''], consonants
        else:
            split = min(split_options, key=lambda x: x[1])
            return consonants[:split[0] + 1], consonants[split[0] + 1:]


def create_syllables(word, vowels):
    """A function that splits a word into syllables."""
    list_of_characters_in_word = list(word)
    consonants = []
    syllables = []
    for i in range(len(list_of_characters_in_word)):
        if is_vowel(list_of_characters_in_word, i, vowels):
            if syllables == []:
                consonants.append(list_of_characters_in_word[i])
                syllables.append(''.join(consonants))
            else:
                left_consonants, right_consonants = split_consonant_graphemes_between_syllables(list(''.join(consonants).lower()))  # TODO - EVERYTHING IS CONVERTED TO LOWER-CASE HERE
                syllables[-1] += ''.join(left_consonants)
                right_consonants.append(list_of_characters_in_word[i])
                syllables.append(''.join(right_consonants))
            consonants = []
        else:
            consonants.append(list_of_characters_in_word[i])
    if len(syllables) < 1:
        return word
    syllables[-1] += ''.join(consonants)

    return syllables