# drs2-judaica-update

Scripts for judaica remediation.  
Currently contains 1 script that:
- Reads a file of file ids, one id per line.
- Translates those file ids to object ids.
- Updates the DRS_OBJECT_UPDATE_STATUS table.
- Logs errors/updated object ids.

## Setup, Building the docker container
- copy env-example to .env and fill values
- `docker build -t drs2-judaica-update:latest . -f Dockerfile` 
## Running the docker container
- `docker run --rm --name my-judaica-update --mount type=bind,source=${PWD},target=/app --env-file .env -it drs2-judaica-update` 

## Running the script to populate the DRS update table
- For Usage
  - `judaica.py`
- Run according to Usage
  - Place input file in same dir as script
  - `judaica.py -i input.txt -o output.txt`
  The output file is a list of successfully updated object ids. 
  Object ids of failed updated will be written to `errors.txt`.

## Running the script to create S3 path CSV
- For Usage
  - `ocflpaths.py`
- Run according to Usage
  - Place input file in same dir as script
  - `ocflpaths.py -i object_ids.txt -o ocflpaths.txt`
  The output file is a CSV containing the S3 path and disposition
  of the descriptor and latest OCFL files for all objects
  in the input file.
  Failures will be written to `errors.txt`.

## Running the controller script to invoke the other two scripts
- For usage
  - `populate.py`
- Set up directory structure (example)
  - `mkdir ./io ./io/judaica ./io/ocfl-input ./io/ocfl-paths`
  - Place input file(s) containing file IDs in `./io/judaica`
- Run according to usage
  - `populate.py -i /app/io/judaica -o /app/io/ocfl-input -x /app/io/ocfl-paths`
  - `populate.py` will call `judaica.py` for each file in `io/judaica`. After the output
  has been created in `io/ocfl-input`, it will pass each output file to `ocflpaths.py`.
  The final output of CSV files containg S3 paths will be written to `io/ocfl-paths`
  There is a configurable delay between calls, which defaults to 5 seconds.

## Notes
- The script is set up to overwrite a given output file on subsequent runs.
  