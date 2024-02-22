import argparse
import os
import shutil
from dotenv import load_dotenv
import time
import traceback
from drs2 import DrsDB

load_dotenv()

def process_file(input_file):
    """
    This function processes the input file and generates the output file.
    """
    # read the input file
    filename = input_file
    with open(filename) as f:
        content = f.readlines()

    # remove whitespace characters like `\n` at the end of each line
    file_ids = [x.strip() for x in content]
    return file_ids


if __name__ == "__main__":
    BATCH_SIZE = int(os.getenv("BATCH_SIZE"), 1000)
    LOG_FILE = os.getenv("LOGFILE_PATH", "./logs/drs_judaica.log")

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Process a text file and \
                                     generate list.")

    # Add command-line arguments
    parser.add_argument("-i", "--input_file",
                        required=True,
                        help="Path to the input file")
    parser.add_argument("-o", "--output_file",
                        required=True,
                        help="Path to the output file")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the process_file function
    file_ids = process_file(args.input_file)
    drs_db = DrsDB()

    data = []
    for file_id in file_ids:
        data.append(file_id)
        if len(data) % BATCH_SIZE == 0:
            object_ids = drs_db.get_object_ids(data)
            errors = drs_db.update_file_ids(object_ids)
            data = []
    if data:
        object_ids = drs_db.get_object_ids(data)
        errors = drs_db.update_file_ids(object_ids)
    drs_db.commit()
    drs_db.close()


