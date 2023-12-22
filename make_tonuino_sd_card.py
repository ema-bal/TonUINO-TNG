
import os
import unicodedata
from datetime import datetime
import shutil
import re

# List to store the tree structure
tree_structure = []

# Add the current date and time as the first line
tree_structure.append(f"Tonuino SD Card\nGenerated on: {datetime.now().strftime('%Y%m%d_%H%M%S')}")

# Function to generate tree structure
def generate_tree_structure(folder, name="", indent="", comment=""):
    if name != "":
        name = f" ({name})"
    if comment != "":
        comment = f" [{comment}]"
    tree_structure.append(f"{indent}{os.path.basename(folder)}/{name}{comment}")
    indent += "    "
    for item in os.listdir(folder):
        item_path = os.path.join(folder, item)
        if os.path.isdir(item_path):
            generate_tree_structure(item_path, indent=indent)
        else:
            tree_structure.append(f"{indent}{item}")

def normalize_filename(filename):
    # Replace German umlauts with specific replacements
    replacements = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'}
    for original, replacement in replacements.items():
        filename = filename.replace(original, replacement)

    # Normalize the filename to remove accents and diacritic marks
    normalized_filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('utf-8')
    return normalized_filename

def rename_mp3_files(folder_path, string_to_remove):

    # Get the list of files in the folder with creation dates
    files_with_dates = [(file, os.path.getctime(os.path.join(folder_path, file))) for file in os.listdir(folder_path) if file.endswith(".mp3")]

    # Check if the folder contains only MP3 files starting with three numbers and underscore
    mp3_files = [file for file in os.listdir(folder_path) if file.endswith(".mp3") and file[:3].isdigit() and file[3] == "_"]
    if len(mp3_files) == len(files_with_dates):
        print(f'Skipped folder: {os.path.basename(folder_path)} (Nothing to do here)')
        return

    # Sort files based on creation date
    sorted_files = sorted(files_with_dates, key=lambda x: x[1])

    # Iterate through each MP3 file and rename it
    for index, (mp3_file, _) in enumerate(sorted_files):
        # Decode the file name to handle special characters (umlauts, etc.)
        decoded_name = os.fsdecode(mp3_file)

        # Check if the constant string is at the beginning of the file name
        if decoded_name.startswith(string_to_remove):
            # Construct the new file name by removing the constant string
            new_name = decoded_name[len(string_to_remove):]
        else:
            # If the constant string is not at the beginning, use the original name
            new_name = decoded_name

        # Normalize the new name to handle umlauts
        new_name = normalize_filename(new_name)

       # Remove existing number prefix
        new_name = new_name.split('_', 1)[-1]
        new_name = new_name.split('_', 1)[-1]

        # Add a running number as a prefix
        new_name = f"{index + 1:03}_{new_name}"
            
        # Construct the full paths for the old and new names
        old_path = os.path.join(folder_path, mp3_file)
        new_path = os.path.join(folder_path, new_name)

        # Rename the file
        os.rename(old_path, new_path)
        print(f'Renamed: {mp3_file} -> {new_name}')


def copy_and_rename_folders(source_base_path, source_folders, destination_folder, string_to_remove):

    # Iterate through each source folder
    for index, source_folder in enumerate(source_folders, start=1):
        comment = source_folder[1]
        source_folder = os.path.join(source_base_path, source_folder[0])
        # Get the base name of the source folder
        base_name = os.path.basename(source_folder)

        # Copy the source folder to the destination folder
        destination_path = os.path.join(destination_folder, f"{index:02d}")
        shutil.copytree(source_folder, destination_path)
        print(f'Copied folder: {base_name} -> {destination_path}')

        # Rename MP3 files in the copied folder
        rename_mp3_files(destination_path, string_to_remove)

        # Generate tree structure for the copied folder
        generate_tree_structure(destination_path, base_name, comment=comment)

string_to_remove = 'SpotifyMate.com - '

source_base_path = "./music_source"
# specified order defines output folder names starting with 01, 02, etc.
source_folders = [
                # folder name, comment
                ["Lieder", "blau Rakete"],
                ["Winter", "weiss Schneeflocke"],
                ["Herbst", "rot Blatt"],
                ["AnneKaffeekanne","schwarz Kaffeekanne"],
                ["Vogelhochzeit","gruen Vogel"],
                ["Fruehling", "gruen Blume"],
                ["Sommer", "gelb Sonne"],
            ]
output_folder = "./sd-card"


# Clear the destination folder if it exists
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)

# Create the destination folder
os.makedirs(output_folder)

# Copy "mp3" and "advert"
system_folders = ["mp3", "advert"]
for f in system_folders:
    source_folder = os.path.join(source_base_path, f)
    destination_path = os.path.join(output_folder, f)
    shutil.copytree(source_folder, destination_path)
    print(f'Copied folder: {source_folder} -> {destination_path}')

copy_and_rename_folders(source_base_path, source_folders, output_folder, string_to_remove)

# Write the tree structure to a text file
datetime_str = re.sub(re.compile(r'^[^0-9]*'), '', tree_structure[0])
output_tree_file = f"file_structure_{datetime_str}.txt"
with open(output_tree_file, 'w') as tree_file:
    tree_file.write('\n'.join(tree_structure))

print("Done.")
