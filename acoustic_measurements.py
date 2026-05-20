import os
import sys
import csv
import xml.etree.ElementTree as ET
import parselmouth
import numpy as np
from textgrid import TextGrid
from extract_sonority import extract_sonority

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MSD_MAPPING_PATH = os.path.join(SCRIPT_DIR, "data", "Gos.TEI.2.1", "mte-msd.xml")
_MSD_EN_TO_SL = None

def compute_durations(tier):
    return [(interval.mark, "{:.2f}".format(interval.maxTime - interval.minTime)) for interval in tier]

def compute_pitch(
    input_wav,
    tier,
    time_step=0.01,
    pitch_floor=75,
    pitch_ceiling=500,
    voiced_ratio_threshold=0.5,
):
    """Return average pitch for each interval in ``tier``.

    Pitch is calculated using Praat's autocorrelation method to mirror the
    behaviour of the Praat GUI.  Intervals are considered unvoiced when fewer
    than ``voiced_ratio_threshold`` of the analysed frames contain a non-zero
    pitch value.  This guards against spurious pitch detections in voiceless
    segments (e.g. voiceless consonants).
    """

    sound = parselmouth.Sound(input_wav)
    pitch = sound.to_pitch_ac(
        time_step=time_step,
        pitch_floor=pitch_floor,
        pitch_ceiling=pitch_ceiling,
    )

    pitch_values = pitch.selected_array["frequency"]
    times = pitch.xs()
    phone_pitches = []

    for interval in tier:
        start_time = interval.minTime
        end_time = interval.maxTime

        indices = np.logical_and(times >= start_time, times <= end_time)
        interval_values = pitch_values[indices]

        if len(interval_values) == 0:
            phone_pitches.append(0.0)
            continue

        nonzero = interval_values[interval_values != 0]
        voiced_ratio = len(nonzero) / len(interval_values)

        if voiced_ratio < voiced_ratio_threshold:
            avg_phone_pitch = 0.0
        else:
            avg_phone_pitch = np.mean(nonzero) if len(nonzero) > 0 else 0.0

        phone_pitches.append(round(float(avg_phone_pitch), 1))

    return phone_pitches

def compute_pitch_trend(input_wav, tier):
    sound = parselmouth.Sound(input_wav)
    pitch = sound.to_pitch()
    pitch_values = pitch.selected_array['frequency']
    trends = []
    for interval in tier:
        start_index = int(interval.minTime // pitch.time_step)
        end_index = int(interval.maxTime // pitch.time_step)
        pitch_segment = pitch_values[start_index:end_index]
        if all(x < y for x, y in zip(pitch_segment, pitch_segment[1:])):
            trends.append('rising')
        elif all(x > y for x, y in zip(pitch_segment, pitch_segment[1:])):
            trends.append('falling')
        else:
            trends.append('mixed' if len(pitch_segment) > 1 else 'unknown')
    return trends

def compute_formants(input_wav, tier):
    sound = parselmouth.Sound(input_wav)
    formant = sound.to_formant_burg()
    formant_values = {'F1': [], 'F2': [], 'F3': [], 'F4': []}
    for interval in tier:
        start_time = interval.minTime
        end_time = interval.maxTime
        f1_value = formant.get_value_at_time(1, (start_time + end_time) / 2)  # Get F1 at midpoint
        f2_value = formant.get_value_at_time(2, (start_time + end_time) / 2)  # Get F2 at midpoint
        f3_value = formant.get_value_at_time(3, (start_time + end_time) / 2)  # Get F3 at midpoint
        f4_value = formant.get_value_at_time(4, (start_time + end_time) / 2)  # Get F4 at midpoint
         # Append formant values to respective lists in the dictionary
        formant_values['F1'].append(round(f1_value, 1) if f1_value is not None else 0.0)
        formant_values['F2'].append(round(f2_value, 1) if f2_value is not None else 0.0)
        formant_values['F3'].append(round(f3_value, 1) if f3_value is not None else 0.0)
        formant_values['F4'].append(round(f4_value, 1) if f4_value is not None else 0.0)
    return formant_values

def compute_intensity(input_wav, tier, intensity_threshold=50):
    sound = parselmouth.Sound(input_wav)
    intensity = sound.to_intensity()
    phone_intensities = []
    for interval in tier:
        start_time = interval.minTime
        end_time = interval.maxTime
        avg_phone_intensity = intensity.get_average(start_time, end_time)
        phone_intensities.append(round(avg_phone_intensity, 1))
    return phone_intensities

def compute_vot(
    input_wav,
    tier,
    pitch_time_step=0.01,
    pitch_floor=75,
    pitch_ceiling=500,
    f0_threshold=75,
    min_voiced_frames=2,
    max_search_after=0.2,
):
    """Compute VOT per interval.

    Definition used: time from the end of the phone (treated as release)
    to the onset of voicing (first reliable F0 > ``f0_threshold``). If
    voicing is already present before the phone end (prevoicing), VOT is
    negative and measured as -(release - voicing onset).
    """

    sound = parselmouth.Sound(input_wav)
    pitch = sound.to_pitch_ac(
        time_step=pitch_time_step, pitch_floor=pitch_floor, pitch_ceiling=pitch_ceiling
    )
    times = pitch.xs()
    f0 = pitch.selected_array["frequency"]
    is_voiced = f0 > f0_threshold

    vot_values = []
    n = len(times)

    for interval in tier:
        end_time = interval.maxTime

        # Index at/just after the phone end
        idx_end = int(np.searchsorted(times, end_time, side="left"))
        idx_end = max(0, min(idx_end, n - 1))

        # Check for prevoicing (voicing already present before release)
        prev_idx = max(0, idx_end - 1)
        vot = None

        if is_voiced[prev_idx]:
            # Find the start of the voiced run that leads into the release
            k = prev_idx
            while k > 0 and is_voiced[k - 1]:
                k -= 1
            # Require a minimum number of voiced frames to be robust
            if (prev_idx - k + 1) >= min_voiced_frames:
                vot = -(end_time - float(times[k]))

        if vot is None:
            # Find first reliable voiced frame after release within a max window
            after_max_time = end_time + max_search_after
            j_start = idx_end
            j_stop = int(np.searchsorted(times, after_max_time, side="left"))
            j_stop = max(j_start, min(j_stop, n - 1))

            j_found = None
            for j in range(j_start, j_stop + 1):
                # Require ``min_voiced_frames`` consecutive voiced frames
                end_j = j + min_voiced_frames
                if end_j <= n and np.all(is_voiced[j:end_j]):
                    j_found = j
                    break
            if j_found is not None:
                vot = float(times[j_found]) - end_time
            else:
                vot = 0.0

        vot_values.append(round(float(vot), 3))
    return vot_values

def compute_cog(input_wav, tier, power=2):
    snd = parselmouth.Sound(input_wav)
    cog_values = []
    for interval in tier:
        # Extract the audio within the given time interval
        audio_interval = snd.extract_part(from_time=interval.minTime, to_time=interval.maxTime)
        # Calculate the spectral centroid for the audio interval
        spectrum = audio_interval.to_spectrum()
        cog = spectrum.get_center_of_gravity(power)
        # Guard against NaN from silent/very short segments
        if cog is None or (isinstance(cog, float) and np.isnan(cog)):
            cog_values.append(0.0)
        else:
            cog_values.append(round(float(cog), 1))
    return cog_values

def compute_sonority(input_wav, tier):
    """Return average sonority for each interval in ``tier``."""
    sonority_vals, sonority_times = extract_sonority(input_wav, plot_graphs=False)
    sonority_values = []
    for interval in tier:
        start_time = interval.minTime
        end_time = interval.maxTime
        indices = np.logical_and(sonority_times >= start_time, sonority_times <= end_time)
        if np.any(indices):
            avg_sonority = float(np.mean(sonority_vals[indices]))
        else:
            avg_sonority = 0.0
        sonority_values.append(round(avg_sonority, 3))
    return sonority_values

def get_item(tier, item_tier):
    item_list = []
    for interval in tier:
        start_time = interval.minTime
        end_time = interval.maxTime
        # Find the word that corresponds to the time interval of the phone
        corresponding_item = next((item.mark for item in item_tier if item.minTime <= start_time and item.maxTime >= end_time), '')
        item_list.append(corresponding_item)
    return item_list

def get_optional_item(tier, textgrid, tier_name):
    try:
        item_tier = textgrid.getFirst(tier_name)
    except Exception:
        return [''] * len(tier)
    return get_item(tier, item_tier)

def phone_context(tier, offset):
    labels = [interval.mark for interval in tier]
    context = []
    for idx in range(len(labels)):
        other_idx = idx + offset
        if 0 <= other_idx < len(labels):
            context.append(labels[other_idx])
        else:
            context.append('')
    return context

def discover_xml_path(input_textgrid):
    audio_id = os.path.splitext(os.path.basename(input_textgrid))[0].replace("-avd", "")
    candidates = [
        os.path.join("data", "Gos.TEI.2.1", "Artur-J", audio_id + ".xml"),
        os.path.join("data", "Gos.TEI.2.1", "Artur-P", audio_id + ".xml"),
        os.path.join("data", "Gos.TEI.2.1", "Artur-N", audio_id + ".xml"),
        os.path.join("/storage", "janezk", "databases", "Arhiv", "nrobida_izbor", audio_id + ".xml"),
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None

def parse_msd_by_token_id(xml_file_path):
    if not xml_file_path or not os.path.exists(xml_file_path):
        return {}

    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    tei_ns = "http://www.tei-c.org/ns/1.0"
    xml_ns = "http://www.w3.org/XML/1998/namespace"
    token_tags = {f"{{{tei_ns}}}w", f"{{{tei_ns}}}pc"}

    msd_by_token_id = {}
    for elem in root.iter():
        if elem.tag not in token_tags:
            continue
        token_id = elem.get(f"{{{xml_ns}}}id", "")
        msd = normalize_msd_value(elem.get("ana", ""))
        if token_id:
            msd_by_token_id[token_id] = msd
    return msd_by_token_id

def normalize_msd_value(msd):
    values = []
    for value in (msd or "").split():
        if value.startswith("mte:"):
            value = value[4:]
        if value.startswith("#"):
            value = value[1:]
        values.append(value)
    return " ".join(values)

def msd_for_token_ids(token_ids, msd_by_token_id):
    values = []
    for label in token_ids:
        ids = label.split()
        msds = [msd_by_token_id.get(token_id, "") for token_id in ids]
        values.append(" ".join(msd for msd in msds if msd))
    return values

def load_msd_en_to_sl():
    global _MSD_EN_TO_SL
    if _MSD_EN_TO_SL is not None:
        return _MSD_EN_TO_SL

    tree = ET.parse(MSD_MAPPING_PATH)
    root = tree.getroot()
    tei_ns = "http://www.tei-c.org/ns/1.0"
    xml_ns = "http://www.w3.org/XML/1998/namespace"

    mapping = {}
    for fs in root.findall(f".//{{{tei_ns}}}fs"):
        if fs.get(f"{{{xml_ns}}}lang") != "en":
            continue
        msd_en = fs.get(f"{{{xml_ns}}}id")
        corresp = fs.get("corresp", "")
        if msd_en and corresp.startswith("#"):
            mapping[msd_en] = corresp[1:]

    _MSD_EN_TO_SL = mapping
    return _MSD_EN_TO_SL

def msd_en_to_sl(msd_values):
    mapping = load_msd_en_to_sl()
    converted_values = []
    for msd in msd_values:
        converted = []
        for value in (msd or "").split():
            if value not in mapping:
                raise ValueError(f"Missing Slovene MSD mapping for {value}")
            converted.append(mapping[value])
        converted_values.append(" ".join(converted))
    return converted_values

def save_to_csv(header, data, output_path):
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    delimiter = "\t" if os.path.splitext(output_path)[1].lower() == ".tsv" else ","
    with open(output_path, mode='w', newline='', encoding="utf-8-sig") as file:
        writer = csv.writer(file, delimiter=delimiter)
        writer.writerow(header)
        writer.writerows(zip(*data))

def main(input_textgrid, input_wav, output_csv, level="phones", input_xml=None):
    tg = TextGrid.fromFile(input_textgrid)
    tier = tg.getFirst(level)
    duration = compute_durations(tier)
    pitch = compute_pitch(input_wav, tier)
    pitch_trend = compute_pitch_trend(input_wav, tier)
    intensity = compute_intensity(input_wav, tier)
    sonority = compute_sonority(input_wav, tier)

    if level == "phones":
        formants = compute_formants(input_wav, tier)
        vot = compute_vot(input_wav, tier)
        cog = compute_cog(input_wav, tier)
        prev_phone_1 = phone_context(tier, -1)
        prev_phone_2 = phone_context(tier, -2)
        next_phone_1 = phone_context(tier, 1)
        next_phone_2 = phone_context(tier, 2)
        word = get_item(tier, tg.getFirst("strd-wrd-sgmnt"))
        token_id = get_optional_item(tier, tg, "word-ID")
        xml_path = input_xml if input_xml else discover_xml_path(input_textgrid)
        msd_en = msd_for_token_ids(token_id, parse_msd_by_token_id(xml_path))
        msd_sl = msd_en_to_sl(msd_en)
        sentence = get_item(tier, tg.getFirst("standardized-trs"))
        speakerID = get_item(tier, tg.getFirst("speaker-ID"))
        audioID = [os.path.splitext(os.path.basename(input_textgrid))[0].replace("-avd",'')] * len(duration)
        csv_data = [('Phone', [t[0] for t in duration]),
            ('Duration', [t[1] for t in duration]),
            ('AvgPitch', pitch),
            ('PitchTrend', pitch_trend),
            ('F1Formant', formants['F1']),
            ('F2Formant', formants['F2']),
            ('F3Formant', formants['F3']),
            ('F4Formant', formants['F4']),
            ('Intensity', intensity),
            ('Sonority', sonority),
            ('VOT', vot),
            ('COG', cog),
            ('prev_phone_1', prev_phone_1),
            ('prev_phone_2', prev_phone_2),
            ('next_phone_1', next_phone_1),
            ('next_phone_2', next_phone_2),
            ('Word', word),
            ('TokenID', token_id),
            ('MSD_en', msd_en),
            ('MSD_sl', msd_sl),
            ('Sentence', sentence),
            ('AudioID', audioID),
            ('SpeakerID', speakerID),
        ]

    elif level == "cnvrstl-syllables":
        csv_data = [
            ('Syllable', [d[0] for d in duration]),
            ('Duration', [d[1] for d in duration]),
            ('AvgPitch', pitch),
            ('PitchTrend', pitch_trend),
            ('Intensity', intensity),
            ('Sonority', sonority),
        ]

    save_to_csv( [t[0] for t in csv_data],  [t[1] for t in csv_data], output_csv)
    print(f"Acoustic measurements saved to {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv) == 5:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    elif len(sys.argv) == 6:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        print("Usage: python acoustic_measurements.py [input.TextGrid] [input.wav] [output.csv|output.tsv] [level (optional, default='phones')] [input.xml (optional)]")
