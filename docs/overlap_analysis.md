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

The script [`discourse_marker_overlap.py`](../discourse_marker_overlap.py) analyzes the overlap between discourse markers and prosodic unit boundaries in TextGrid files. It processes files containing annotated speech data where discourse markers and prosodic units have been marked in separate tiers.

### Features

The script performs three types of analysis:
1. Overlaps between "af" marks from the "actualDM" tier and prosodic unit boundaries
2. Overlaps between discourse marker group labels (TI, TQ, TR, I, C) and prosodic unit boundaries
3. Overlaps between discourse marker subgroup labels and prosodic unit boundaries

### Input Data Requirements

The script expects TextGrid files with the following tiers:
- "PU": Contains prosodic unit boundary markings
- "actualDM": Contains discourse marker annotations with "af" marks
- "actual-DM-classif": Contains discourse marker classifications in the format X-YY where:
  - X[X] is the main group (TI, TQ, TR, I, C, ...)
  - YY is the subgroup (e.g., MC, MO, PI, RI, RR, etc.)

### Usage

```bash
python discourse_marker_overlap.py <path_to_textgrid_file_or_directory>
```

The script can process either:
- A single TextGrid file
- A directory containing multiple TextGrid files (using wildcards)

Examples:
```bash
# Process a single file
python discourse_marker_overlap.py path/to/file.TextGrid

# Process all TextGrid files in a directory
python discourse_marker_overlap.py "path/to/directory/*.TextGrid"
```

### Output

The script provides detailed statistics for each processed file and total results across all files:

1. ActualDM overlaps:
   - Number and percentage of "af" marks that overlap with prosodic unit boundaries

2. Group overlaps:
   - Number and percentage of overlaps for each main group (TI, TQ, TR, I, C, ...)

3. Subgroup overlaps:
   - Number and percentage of overlaps for each subgroup

Results are displayed in the format: `X/Y (Z%)` where:
- X is the number of overlaps
- Y is the total number of occurrences
- Z is the percentage of overlaps
