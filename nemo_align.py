import sys
import subprocess
import glob

def run_alignment(nemo_dir, model_path, manifest_file, output_dir):
    try:
        subprocess.run(["python", f"{nemo_dir}/tools/nemo_forced_aligner/align.py", 
                        f"model_path={model_path}", f"manifest_filepath={manifest_file}", 
                        f"output_dir={output_dir}", "save_output_file_formats=['ctm']"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    # Call example
    # python nemo_align.py ~/repos/NeMo ./data/v2.0/conformer_ctc_bpe.nemo ./data/nemo/input/Artur-J/ "./data/nemo/output/Artur-J/"
    if len(sys.argv) != 5:
        print("Usage: python nemo_align.py <nemo_dir> <model_path> <manifest_dir> <output_dir>")
        sys.exit(1)

    nemo_dir = sys.argv[1]
    model_path = sys.argv[2]
    manifest_dir = sys.argv[3]
    output_dir = sys.argv[4]

    for manifest_file in sorted(glob.glob(f"{manifest_dir}*.json")):
        run_alignment(nemo_dir, model_path, manifest_file, output_dir)
