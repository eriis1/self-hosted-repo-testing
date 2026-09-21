from agent_sdk import FileParam, UploadFileParams, info
import subprocess
import os

def convert_wiff_to_mzml(wiff_file_path, output_dir=None):
    """
    Convert a .wiff file to .mzML using MSConvert.

    Parameters:
    - wiff_file_path (str): The full path to the .wiff file.
    - output_dir (str, optional): Directory to save the .mzML file. If None, saves in the same directory as input.
    """

    # Ensure the .wiff file exists
    if not os.path.isfile(wiff_file_path):
        info(f"File not found: {wiff_file_path}")
        return

    # Set output directory to the same directory as input file if not specified
    if output_dir is None:
        output_dir = os.path.dirname(wiff_file_path)
    elif not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    # Construct the msconvert command
    command = [
        "C:\\Users\\nick\\AppData\\Local\\Apps\\ProteoWizard 3.0.24310.86a9ba6 64-bit\\msconvert.exe",                 # MSConvert executable
        wiff_file_path,              # Input .wiff file
        "--mzML",                    # Output format
        "--outdir", output_dir       # Output directory
    ]

    # Run the msconvert command
    try:
        subprocess.run(command, check=True)
        info(f"Conversion complete. Output saved in: {output_dir}")
    except subprocess.CalledProcessError as e:
        info(f"Error during conversion: {e}")
    except FileNotFoundError:
        info("MSConvert is not found. Ensure it is installed and in your PATH.")


# Required Function
def execute(**kwargs) -> UploadFileParams | None:
    """
    Executes on specified cadence.

    Returns
    -------
    UploadFileParams | None
        Files to upload; if set to None, then no files will be uploaded.
    """

    info("starting execute")
    # Example usage
    wiff_file_path = "C:\\Users\\nick\\Desktop\\wiff_dir\\102851-REDPPB-Hu_Rat_20231120.wiff"
    output_dir = "C:\\Users\\nick\\Desktop\\wiff_dir\\out"  # Optional
    convert_wiff_to_mzml(wiff_file_path, output_dir)

    info("done with execute")

    return None



