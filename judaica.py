#!/usr/bin/python3
import argparse
import os
import logging
from dotenv import load_dotenv
from drs2db.drsdb import DrsDB
from drs2db import configure_logger

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
    file_ids = [x.strip() for x in list(filter(lambda x:
                                               (x.strip()).isdigit(),
                                               content))]
    file_ids = list(set(file_ids))  # deduplicate
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
    output = open(args.output_file, "a")
    error_file = open("errors.txt", "w")
    processed_filename = "processed.txt"
    already_processed_ids = []
    if (os.path.exists(processed_filename)):
        with open(processed_filename, "r") as processed_file:
            processed_content = processed_file.readlines()
        already_processed_ids = [(int(x.strip()),) for x in processed_content]

    logger.info(f"Processing {len(file_ids)} file ids in {args.input_file}")
    data = []
    error_count = 0
    updated_count = 0
    skipped_count = 0
    unique_object_ids = []

    # get list of unique object ids
    for file_id in file_ids:
        data.append(file_id)
        if len(data) % BATCH_SIZE == 0:
            obj_tuple_list = drs_db.get_object_ids(data)
            unique_object_ids = unique_object_ids + obj_tuple_list
            data = []
    if data:
        obj_tuple_list = drs_db.get_object_ids(data)
        unique_object_ids = unique_object_ids + obj_tuple_list
    # deduplicate list
    unique_object_ids = list(set(unique_object_ids))

    # process the object ids in batches
    data = []
    for object_id in unique_object_ids:
        data.append(object_id)
        if len(data) % BATCH_SIZE == 0:
            # return a list of object_ids that are not in already_processed_ids
            object_ids = list(filter(lambda x: x not in already_processed_ids,
                                     data))
            skipped_object_ids = list(filter(lambda x: x in
                                             already_processed_ids,
                                             data))
            if skipped_object_ids:
                for skipped_object_id in skipped_object_ids:
                    logger.info(f"Object id {skipped_object_id[0]} " +
                                "already processed, skipping...")
                    skipped_count = skipped_count + 1
            rows_updated = []
            errors = []
            if object_ids:
                rows_updated, errors = drs_db.update_object_ids(object_ids)
            bad_object_ids = []
            if errors:
                for error in errors:
                    bad_object_id = object_ids[error['index']][0]
                    logger.error(f"ERROR: object id {bad_object_id} " +
                                 f"failed to update: {error['message']}")
                    error_file.write(f"{bad_object_id}\n")
                    bad_object_ids.append(bad_object_id)
                    error_count = error_count + 1
            if rows_updated:
                for object_id in object_ids:
                    if object_id not in bad_object_ids:
                        output.write(f"{object_id[0]}\n")
                        logger.info(f"Object id {object_id[0]} " +
                                    "updated successfully")
                        updated_count = updated_count + 1
                        already_processed_ids.append(object_id[0])
                        with open(processed_filename, "a+") as processed_file:
                            processed_file.write(f"{object_id[0]}\n")
            data = []
            bad_object_ids = []

    if data:
        # return a list of object_ids that are not in already_processed_ids
        object_ids = list(filter(lambda x: x not in already_processed_ids,
                                 data))
        skipped_object_ids = list(filter(lambda x: x in already_processed_ids,
                                         data))
        if skipped_object_ids:
            for skipped_object_id in skipped_object_ids:
                logger.info(f"Object id {skipped_object_id[0]} " +
                            "already processed, skipping...")
                skipped_count = skipped_count + 1
        rows_updated = []
        errors = []
        if object_ids:
            rows_updated, errors = drs_db.update_object_ids(object_ids)
        bad_object_ids = []
        if errors:
            for error in errors:
                bad_object_id = object_ids[error['index']][0]
                logger.error(f"ERROR: object id {bad_object_id} " +
                             f"failed to update: {error['message']}")
                error_file.write(f"{bad_object_id}\n")
                bad_object_ids.append(bad_object_id)
                error_count = error_count + 1
        if rows_updated:
            for object_id in object_ids:
                if object_id not in bad_object_ids:
                    output.write(f"{object_id[0]}\n")
                    logger.info(f"Object id {object_id[0]} " +
                                "updated successfully")
                    updated_count = updated_count + 1
                    already_processed_ids.append(object_id[0])
                    with open(processed_filename, "a+") as processed_file:
                        processed_file.write(f"{object_id[0]}\n")
        data = []
        bad_object_ids = []

    drs_db.close()
    error_file.close()
    output.close()
    # delete the error file if it is empty
    if os.stat("errors.txt").st_size == 0:
        os.remove("errors.txt")
    # delete the output file if it is empty
    if os.stat(args.output_file).st_size == 0:
        os.remove(args.output_file)

    logger.info(f"Completed processing {len(file_ids)} file ids")
    logger.info(f"Updated {updated_count} object ids")
    logger.info(f"Skipped {skipped_count} object ids")
    logger.info(f"Failed to update {error_count} object ids")
    logger.info(f"Unique object ids processed: {len(unique_object_ids)}")
