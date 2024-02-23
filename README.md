# drs2-judaica-update

Scripts for judaica remediation.  
Currently contains 1 script that:
- reads a file of file ids
- translates those file ids to object ids
- updates the DRS_OBJECT_UPDATE_STATUS table
- logs errors/updated object ids

## Setup, Building the docker container
- copy env-example to .env and fill values
- `docker build -t drs2-judaica-update:latest . -f Dockerfile` 
## Running the docker container
- `docker run --rm --name my-judaica-update --mount type=bind,source=${PWD},target=/app -it drs2-judaica-update` 

## Running the script
- For Usage
  - `python3 judaica.py`
- Run according to Usage
  - Place file in same dir as script
  - `python3 judaica.py -i input.txt -o output.txt`

## Notes
- The script is set up to overwrite a given output file on subsequent runs 
  