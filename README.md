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
- `docker run --rm --name my-judaica-update --mount type=bind,source=${PWD},target=/app -it drs2-judaica-update` 

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

## Notes
- The script is set up to overwrite a given output file on subsequent runs.
  