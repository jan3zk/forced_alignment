import os
import shutil

# specify the directory you want to start from
inputDir = './corpus/'
outputDir = './corpus/'

for dirName, subdirList, fileList in os.walk(inputDir):
    for fname in fileList:
        if fname.endswith('.wav') or fname.endswith('.txt'):
            # Get the first 13 characters of the file
            new_dir = os.path.join(outputDir, fname[:13])

            # Create a new directory if it does not exist
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)

            # Move the file to new directory
            shutil.move(os.path.join(dirName, fname), os.path.join(new_dir, fname))

