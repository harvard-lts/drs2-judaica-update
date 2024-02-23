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
    file_ids = [x.strip() for x in content]
    return file_ids


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
    file_ids = process_file(args.input_file)
    drs_db = DrsDB()

    # open the output file
    output = open(args.output_file, "w")
    error_file = open("errors.txt", "w")

    logger.info(f"Processing {len(file_ids)} file ids")
    data = []
    for file_id in file_ids:
        data.append(file_id)
        if len(data) % BATCH_SIZE == 0:
            object_ids = drs_db.get_object_ids(data)
            errors = drs_db.update_file_ids(object_ids)
            bad_object_ids = []
            if errors:
                for error in errors:
                    bad_object_id = data[error['index']]
                    logger.error(f"ERROR: object id {bad_object_id} " +
                                 f"failed to update: {error['message']}")
                    error_file.write(f"{bad_object_id}")
                    bad_object_ids.append(bad_object_id)
            for object_id in data:
                if object_id not in bad_object_ids:
                    output.write(f"{object_id}")
                    logger.info(f"Object id {object_id} updated successfully")
            data = []
            bad_object_ids = []
    if data:
        object_ids = drs_db.get_object_ids(data)
        errors = drs_db.update_file_ids(object_ids)
        bad_object_ids = []
        if errors:
            for error in errors:
                bad_object_id = data[error['index']]
                logger.error(f"ERROR: object id {bad_object_id} " +
                             f"failed to update: {error['message']}")
                error_file.write(f"{bad_object_id}")
                bad_object_ids.append(bad_object_id)
        for object_id in data:
            if object_id not in bad_object_ids:
                output.write(f"{object_id}")
                logger.info(f"Object id {object_id} updated successfully")
        data = []
        bad_object_ids = []
    drs_db.close()
    error_file.close()
    output.close()
    logger.info(f"Completed updating {len(file_ids)} file ids")
