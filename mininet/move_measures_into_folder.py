import os

from pathlib import Path

def create_measurement_folder(filename, exist_ok=False):
    """Creating the folder for the current measurement"""

    measurement_dir = "mininet_measurements"
    pure_filename = Path(filename).stem
    measurement_path = Path(measurement_dir).joinpath(filename)
    measurement_path.mkdir(parents=False, exist_ok=exist_ok)
    
    return measurement_path

def move_file(input_dir, file_pattern, output_dir):
    """Moving all files with the given name (exclude extension) from the input dir to the given output directory"""
    
    for file_to_move in os.listdir(input_dir):
        if file_pattern in file_to_move:
            input_filename = Path(input_dir).joinpath(file_to_move)
            suffix = Path(file_to_move).suffix
            output_filename = Path(output_dir).joinpath(input_dir+suffix)
            os.replace(input_filename, output_filename)

def list_pcap_files(folder):
    """Listing all pcap file names that can be found."""
        
    logfiles = []
    for file in os.listdir(folder):
        if Path(file).is_file:
            # print(file)
            # Chop of the .log from the name to make finding files easier
            basename = Path(file).stem
            logfiles.append(basename)
    
    # Remove the doubled files from pcap and logfile
    logfiles = list(set(logfiles))
    
    print(f"Found {len(logfiles)} logfiles")
    return logfiles
        
def move_all_measurement_files():
    """
    Moving all pcap, log and other files into the measurement folder given.
    Uniting them in a single folder showing the date and time taken.
    """

    h1_dir = "h1"
    h2_dir = "h2"
    nat1_dir = "nat1"
    nat2_dir = "nat2"
    s3_dir = "s3"
    turn_dir = "turn"

    # The pcaps and logfiles are the most often once, iterate over them and try to collect
    # everything else that also can be found
    for file_to_move in list_pcap_files(turn_dir):
        print(file_to_move)
        new_folder = create_measurement_folder(file_to_move, True)
        # move_file(h1_dir, file_to_move, new_folder)
        # move_file(h2_dir, file_to_move, new_folder)
        move_file(nat1_dir, file_to_move, new_folder)
        move_file(nat2_dir, file_to_move, new_folder)
        move_file(s3_dir, file_to_move, new_folder)
        move_file(turn_dir, file_to_move, new_folder)
        
        
if __name__ == "__main__":
    move_all_measurement_files()