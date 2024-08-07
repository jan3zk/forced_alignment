def is_vowel(list_of_phonemes_in_word, position, vowels):
    """Function to determine whether a phoneme is a vowel"""
    return list_of_phonemes_in_word[position] in vowels


def get_vowel_phonemes(pdict):
    """Returns a list of vowel phonemes."""
    if pdict.lower() == 'gos':
        return ["@", "a", "e", "E", "i", "o", "O", "u"] #Gos
    else:
        return ["a", "\"a", "\"a:", "e", "\"e:", "E", "\"E", "\"E:", "@", "\"@", "i", "\"i", "\"i:", "I", "o", "\"o:", "O", "\"O", "\"O:", "u", "\"u", "\"u:"] #Optilex


def get_sonorant_phonemes(pdict):
    """Returns a list of sonorant phonemes. """
    if pdict.lower() == 'gos':
        return ["m", "n", "n'", "N", "v", "w", "W", "l", "l'", "r", "j"] #Gos
    else:
        return ["m", "n", "n'", "N", "v", "w", "W", "U", "l", "l'", "r", "j"] #Optilex


def get_voiced_obstruent_phonemes(pdict):
    """Returns a list of voiced obstruent phonemes."""
    if pdict.lower() == 'gos':
        return ["b", "d", "z", "Z", "g"] #Gos
    else:
        return ["b", "b_n", "b_f", "d", "d_l", "d_n", "z", "Z", "g"] #Optilex


def get_voiceless_obstruent_phonemes(pdict):
    """Returns a list of voiceless obstruent phonemes."""
    if pdict.lower() == 'gos':
        return ["F", "p", "t", "s", "S", "tS", "k", "f", "h", "x", "ts"] #Gos
    else:
        return ["F", "p", "p_n", "p_f", "t", "t_l", "t_n", "s", "S", "tS", "k", "f", "G", "x", "ts"] #Optilex


def get_consonant_phonemes(pdict):
    """Returns a list of all consonant phonemes."""
    if pdict.lower() == 'gos':
        return ["m", "n", "n'", "N", "v", "w", "W", "l", "l'", "r", "j", "b", "d",
                "z", "Z", "g", "p", "t", "s", "S", "tS", "k", "f", "F", "h", "x", "ts"] #Gos
    else:
        return ["m", "n", "n'", "N", "v", "w", "W", "U", "l", "l'", "r", "j", "b", "b_n", "b_f", "d", "d_l", "d_n",
                "z", "Z", "g", "p", "p_n", "p_f", "t", "t_l", "t_n", "s", "S", "tS", "k", "f", "F", "G", "x", "ts"] #Optilex


def split_consonant_phonemes_between_syllables(consonants, pdict):
    """A function that splits consonants between syllable 1 and syllable 2."""
    # GET LISTS OF PHONEMES BY CATEGORY
    sonorant_phonemes = get_sonorant_phonemes(pdict)
    voiced_obstruent_phonemes = get_voiced_obstruent_phonemes(pdict)
    voiceless_obstruent_phonemes = get_voiceless_obstruent_phonemes(pdict)

    # If there are no consonant phonemes, return empty lists for syllable 1 and syllable 2
    if len(consonants) == 0:
        return [], []

    # If there's only one consonant phoneme, attach it to syllable 2
    elif len(consonants) == 1:
        return [], consonants

    # If there are more consonant graphemes, perform the following:
    else:
        split_options = []
        for i in range(len(consonants)-1):
            current_consonant_phoneme = consonants[i]
            next_consonant_phoneme = consonants[i+1]

            if current_consonant_phoneme in ['-', '_']:
                split_options.append([i, -1])
            # If the consonants are the same (oDDaja)
            elif current_consonant_phoneme == next_consonant_phoneme:
                split_options.append([i, 0])
            # Combination of sonorant + obstruent phoneme (objeM-Ka, soN-Da)
            elif current_consonant_phoneme in sonorant_phonemes:
                if next_consonant_phoneme in voiced_obstruent_phonemes or next_consonant_phoneme in voiceless_obstruent_phonemes:
                    split_options.append([i, 2])
                # TODO - ADD SONORANT + SONORANT (orvejski? Narvik - narviški?)
                elif next_consonant_phoneme in sonorant_phonemes:
                    split_options.append([i, 2])
            # Combination of two voiced obstruents (oD-Ganjati) or a voiced and a voiceless obstruent phoneme (oD-Kleniti)
            elif current_consonant_phoneme in voiced_obstruent_phonemes:
                if next_consonant_phoneme in voiced_obstruent_phonemes:
                    split_options.append([i, 1])
                elif next_consonant_phoneme in voiceless_obstruent_phonemes:
                    split_options.append([i, 3])
                # TODO - ADD VOICED OBSTRUENT + SONORANT
                elif next_consonant_phoneme in sonorant_phonemes:
                    split_options.append([i, 2])
            # Combination of a voiceless and a voiced obstruent phoneme (glas-Ba)
            elif current_consonant_phoneme in voiceless_obstruent_phonemes:
                if next_consonant_phoneme in voiced_obstruent_phonemes:
                    split_options.append([i, 4])
                # TODO - Add TWO VOICELESS OBSTRUENTS? (poS-Tulat)
                elif next_consonant_phoneme in voiceless_obstruent_phonemes:
                    split_options.append([i, 2])
                # TODO - Add VOICELESS OBSTRUENT + SONORANT
                #elif next_consonant_phoneme in sonorant_phonemes:
                #    split_options.append([i, 2])

        if split_options == []:
            return [], consonants
        else:
            split = min(split_options, key=lambda x: x[1])
            return consonants[:split[0] + 1], consonants[split[0] + 1:]


def syllabize_phonemes(word: str) -> list[str]:
    """A function that splits a word into syllables."""
    consonants = []
    syllables = []
    pdict = 'optilex'
    phonemes_in_word = word.split()
    vowels = get_vowel_phonemes(pdict)
    for i in range(len(phonemes_in_word)):
        if is_vowel(phonemes_in_word, i, vowels):
            if syllables == []:
                consonants.append(phonemes_in_word[i])
                syllables.append(" ".join(consonants))
            else:
                left_consonants, right_consonants = split_consonant_phonemes_between_syllables(consonants, pdict)
                if left_consonants:
                    syllables[-1] += " " + " ".join(left_consonants)
                right_consonants.append(phonemes_in_word[i])
                syllables.append(" ".join(right_consonants))
            consonants = []
        else:
            consonants.append(phonemes_in_word[i])

    if len(syllables) < 1:
        return [word]

    if consonants:
        syllables[-1] += " " + " ".join(consonants)

    return syllables
