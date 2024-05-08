import os
import re
import shutil

from pathlib import Path

def create_measurement_folder(filename, exist_ok=False):
    """Creating the folder for the current measurement"""

    measurement_dir = "old_mn_measurements"
    pure_filename = Path(filename).stem
    measurement_path = Path(measurement_dir).joinpath(filename)
    measurement_path.mkdir(parents=False, exist_ok=exist_ok)
    
    return measurement_path

def resolve_pos_filtered(foldername):
    """
    Getting a foldername, checking if it is a pos_filtered one
    and moving the files in these folders into the matching folder.
    """
    
    measurement_dir = "mininet_measurements"
    # Check if it is one of the pos_filtered folders
    found = re.match("^pos_filtered_(\d+_\d+)_(\d+_\d+)", f"{foldername}")
    if found is None:
        return
    day_match = found.group(1)
    time_match = found.group(2)
    
    new_path = Path(measurement_dir).joinpath(day_match).joinpath(time_match)
    new_path.mkdir(parents=True, exist_ok=True)
    shutil.move(Path(measurement_dir).joinpath(foldername).joinpath("h1.log"), new_path.joinpath("pos_filtered_h1.log"))
    shutil.move(Path(measurement_dir).joinpath(foldername).joinpath("h2.log"), new_path.joinpath("pos_filtered_h2.log"))
    os.remove(Path(measurement_dir).joinpath(foldername))

def create_stacked_mm_folder(foldername, exists_ok=False):
    """
    Creating a single folder per day containing all measurements of the day
    in subfolders showing only the time of measurement.
    """

    measurement_dir = "mininet_measurements"
    old_folder = Path(foldername).stem
    measurement_day_path = re.match("^([0-9]+_[0-9]+)_([0-9]+_[0-9]+)", f"{old_folder}")
    if measurement_day_path is None:
        return
    day_folder = measurement_day_path.group(1)
    time_folder = measurement_day_path.group(2)
    new_mm_dir = Path(measurement_dir).joinpath(day_folder).joinpath(time_folder)
    Path(new_mm_dir).mkdir(parents=True, exist_ok=True)

    # Now moving all data from the old dir into the new dir
    input_dir = Path(measurement_dir).joinpath(foldername)
    move_folder(input_dir, new_mm_dir)
    delete_old_folder(input_dir)

def move_folder(input_dir, output_dir):
    """
    Moving all files in the given input_dir to output_dir.
    """

    print(f"Moving folder {input_dir} to {output_dir}")
    for file_to_move in os.listdir(input_dir):
        shutil.move(Path(input_dir).joinpath(file_to_move), output_dir)

def move_file(input_dir, file_pattern, output_dir):
    """Moving all files with the given name (exclude extension) from the input dir to the given output directory"""
    
    for file_to_move in os.listdir(input_dir):
        if file_pattern in file_to_move:
            input_filename = Path(input_dir).joinpath(file_to_move)
            suffix = Path(file_to_move).suffix
            output_filename = Path(output_dir).joinpath(input_dir+suffix)
            os.replace(input_filename, output_filename)

def delete_old_folder(folder):
    """
    Removing the old folder
    """

    if Path(folder).exists():
        os.rmdir(folder)

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

def list_all_folders(directory):
    """
    Listing all folders in the given directory
    """

    folders = []
    for folder in os.listdir(directory):
        if Path(folder).is_dir:
            folder_name = Path(folder).stem
            folders.append(folder_name)

    return folders

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
        
def reorganize_into_day_time_subfolders():
    """
    Moving all current tests into a single folder per day, holding subfolders
    with the time per measurement.
    """

    directory_to_modify = "mininet_measurements"

    for folder in list_all_folders(directory_to_modify):
        # create_stacked_mm_folder(folder)
        resolve_pos_filtered(folder)

        # break

if __name__ == "__main__":
    # move_all_measurement_files()
    reorganize_into_day_time_subfolders()