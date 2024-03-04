#!/usr/bin/python3
import argparse
import os
import logging
from dotenv import load_dotenv
from drs2.drsdb import DrsDB
from drs2 import configure_logger

load_dotenv()
configure_logger()
logger = logging.getLogger('drs2_judaica_update')


def process_file(input_file):
    """
    This function processes the input file and generates the output file.
    """
    # read the input file
    filename = input_file
    with open(filename) as f:
        content = f.readlines()

    # remove whitespace characters like `\n` at the end of each line
    object_ids = [x.strip() for x in list(filter(lambda x:
                                                 (x.strip()).isdigit(),
                                                 content))]
    object_ids = list(set(object_ids))  # deduplicate
    return object_ids


def get_updated_paths(descriptor_path):
    STORAGE_CLASS = "RE"
    INVENTORY_JSON = "inventory.json"
    INVENTORY_JSON_SHA512 = "inventory.json.sha512"
    updated_paths = []
    ocpf_root = descriptor_path[0:descriptor_path.find('v')]
    updated_paths.append(ocpf_root + INVENTORY_JSON + ", " + STORAGE_CLASS)
    updated_paths.append(ocpf_root + INVENTORY_JSON_SHA512 +
                         ", " + STORAGE_CLASS)
    descriptor_root = descriptor_path[0:descriptor_path.find('content')]
    updated_paths.append(descriptor_root + INVENTORY_JSON +
                         ", " + STORAGE_CLASS)
    updated_paths.append(descriptor_root + INVENTORY_JSON_SHA512 +
                         ", " + STORAGE_CLASS)
    updated_paths.append(descriptor_path + ", " + STORAGE_CLASS)
    return updated_paths


if __name__ == "__main__":
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 1000))
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
    object_ids = process_file(args.input_file)
    drs_db = DrsDB()

    # open the output file
    output = open(args.output_file, "a")
    error_file = open("errors.txt", "w")
    processed_filename = "processed_ocfl.txt"
    already_processed_ids = []
    if (os.path.exists(processed_filename)):
        with open(processed_filename, "r") as processed_file:
            processed_content = processed_file.readlines()
        already_processed_ids = [x.strip() for x in processed_content]

    logger.info(f"Processing {len(object_ids)} " +
                f"object ids in {args.input_file}")
    data = []
    error_count = 0
    updated_count = 0
    skipped_count = 0

    for object_id in object_ids:
        if object_id in already_processed_ids:
            logger.info(f"Object id {object_id} " +
                        "already processed, skipping...")
            skipped_count += 1
            continue
        ocfl_path, storage_class = drs_db.get_descriptor_path(object_id)
        if ocfl_path:
            ocfl_paths = get_updated_paths(ocfl_path)
            for path in ocfl_paths:
                output.write(f"{path}\n")
            updated_count += 1
            with open(processed_filename, "a") as processed_file:
                processed_file.write(f"{object_id}\n")
        else:
            logger.error("ERROR: failed to get descriptor for " +
                         f"object id {object_id}")
            error_file.write(f"{object_id}\n")
            error_count += 1

    drs_db.close()
    error_file.close()
    output.close()
    # delete the error file if it is empty
    if os.stat("errors.txt").st_size == 0:
        os.remove("errors.txt")
    # delete the output file if it is empty
    if os.stat(args.output_file).st_size == 0:
        os.remove(args.output_file)

    logger.info(f"Completed processing {len(object_ids)} object ids")
    logger.info(f"Updated {updated_count} object ids")
    logger.info(f"Failed to update {error_count} object ids")
