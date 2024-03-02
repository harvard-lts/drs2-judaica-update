#!/usr/bin/python3

import argparse
import os
import logging
from dotenv import load_dotenv
from drs2 import configure_logger
import time

load_dotenv()
configure_logger()
logger = logging.getLogger('drs2_judaica_update')


def process_judaica(input_dir, output_dir):
    """
    This function processes all judaica files in the input dir &
    writes files of object ids to the output dir.
    """
    DELAY_SECS = int(os.getenv("DELAY_SECS", 5))
    judaica_path = os.getenv("JUDAICA_PATH", "/home/drsadm/bin/judaica.py")
    files_processed = 0

    for f in os.listdir(input_dir):
        if f.endswith(".txt") or f.endswith(".csv"):
            ocflpaths_filename = f"ocflpath_input_{files_processed}.txt"
            input_file = os.path.join(input_dir, f)
            output_file = os.path.join(output_dir, ocflpaths_filename)
            logger.info(f"Processing {input_file} for judaica...")
            os.system(f"{judaica_path} -i {input_file} -o {output_file}")
            files_processed = files_processed + 1
            logger.info(f"Processing {input_file} for judaica complete")
            time.sleep(DELAY_SECS)

    return files_processed


def process_ocflpath(input_dir, output_dir):
    """
    This function processes all files of object ids in the input dir &
    writes files of ocfl paths to the output dir.
    """
    DELAY_SECS = int(os.getenv("DELAY_SECS", 5))
    ocflpaths_path = os.getenv("OCFLPATHS_PATH", "/home/drsadm/bin/ocflpaths.py")
    files_processed = 0

    for f in os.listdir(input_dir):
        if f.startswith("ocflpath_input_") and f.endswith(".txt"):
            ocflpaths_filename = f"output_{files_processed}.txt"
            input_file = os.path.join(input_dir, f)
            output_file = os.path.join(output_dir, ocflpaths_filename)
            logger.info(f"Processing ocfl paths from {input_file}...")
            os.system(f"{ocflpaths_path} -i {input_file} -o {output_file}")
            files_processed = files_processed + 1
            logger.info(f"Processing ocfl paths from {input_file} completed")
            time.sleep(DELAY_SECS)

    return files_processed


if __name__ == "__main__":
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 1000))
    LOG_FILE = os.getenv("LOGFILE_PATH", "./logs/drs_judaica.log")

    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Process a directory  and \
                                     generate object id files & ocfl paths.")

    # Add command-line arguments
    parser.add_argument("-i", "--input_dir",
                        required=True,
                        help="Path to the input directory")
    parser.add_argument("-o", "--output_dir",
                        required=True,
                        help="Path to the judaica output dir/ ocfl input dir")
    parser.add_argument("-x", "--final_dir",
                        required=True,
                        help="Path to the final output dir of ocfl paths")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Step 1: Call the process_file function
    logger.info(f"Processing judaica files in {args.input_dir}")
    judaica_files = process_judaica(args.input_dir, args.output_dir)
    logger.info(f"Processed {judaica_files} judaica files")
    time.sleep(10)
    # Step 2: Call the process_ocfl function
    logger.info("Now processing ocfl paths for all judaica files")
    ocflpaths_files = process_ocflpath(args.output_dir, args.final_dir)
    logger.info(f"Processed {ocflpaths_files} ocflpaths files")
    logger.info("Processing completed")
