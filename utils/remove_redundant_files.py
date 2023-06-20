import os

# Path to your directory
directory = "./corpus"

# Sets to hold the filenames (without extension)
wav_files = set()
txt_files = set()

# Scan the directory and all its subdirectories
for root, dirs, files in os.walk(directory):
    for filename in files:
        name, extension = os.path.splitext(filename)
        if extension == ".wav":
            wav_files.add(os.path.join(root, name))
        elif extension == ".txt":
            txt_files.add(os.path.join(root, name))

# Calculate the difference between the sets
wav_only = wav_files - txt_files
txt_only = txt_files - wav_files

# Remove unpaired .wav and .txt files
for filename in wav_only:
    os.remove(f"{filename}.wav")
for filename in txt_only:
    os.remove(f"{filename}.txt")

