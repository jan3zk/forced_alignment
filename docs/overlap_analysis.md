# Overlap Analysis with Manually Annotated Prosodic Units

[![sl](https://img.shields.io/badge/lang-sl-blue.svg)](overlap_analysis.sl.md)

The analysis of overlap between manually annotated prosodic units (PU) and automatically detected prosodic parameters is essential for assessing the accuracy and consistency of speech processing algorithms. Prosodic units are speech segments that express features such as pitch, intensity, speech rate, pauses, and speaker changes. In this expanded analysis, we will delve into the methods for evaluating the alignment between these parameters and manual annotations.

## Prosodic Parameter Overlap

The script [`prosodic_param_overlap.py`](../prosodic_param_overlap.py) is designed to analyze the overlap between manually annotated prosodic units (PU) and parameters such as:

- **"pitch-reset"**,
- **"intensity-reset"**,
- **"speech-rate-reduction"**,
- **"pause"**,
- **"speaker-change"**.

**Analysis Process:**

The script compares intervals in the "PU" tier with the corresponding automatically detected intervals in the tiers mentioned above. For each comparison, it calculates the overlap ratio (in both absolute and relative forms) where the automatically detected parameter matched the manually annotated boundaries. Optionally, the script can save the results to a CSV file, which includes detailed information on the degree of overlap and non-overlap for each parameter.

**Command to Run the Analysis:**

```bash
python prosodic_param_overlap.py </path/to/*.TextGrid> [results.csv]
```

Where `</path/to/*.TextGrid>` is the path to the TextGrid files to be analyzed, and the optional argument `[results.csv]` allows the results of the analysis to be saved in CSV format.

## Discourse Marker Overlap Analysis

The script [`discourse_marker_overlap.py`](../discourse_marker_overlap.py) is intended to analyze the overlap between manually annotated prosodic units (PU tier) and discourse markers (DM), such as pauses in speech, emphasis, speaker changes, and other speech phenomena marked by DM.

**Analysis Process:**

The script compares DM intervals with manually determined prosodic unit boundaries ("PU" tier) and calculates overlap ratios for each unique discourse marker. Both relative and absolute overlap ratios are provided for automatically detected DMs (in the "discourse-marker" tier) and manually confirmed DMs (in the "actualDM" tier).

**Command to Run the Analysis:**

```bash
python discourse_marker_overlap.py </path/to/files/*.TextGrid>
```