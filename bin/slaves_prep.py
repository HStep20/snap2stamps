### Python script to use SNAP as InSAR processor compatible with StaMPS PSI processing
# Author Jose Manuel Delgado Blasco
# Date: 21/06/2018
# Version: 1.0

# Step 1 : preparing slaves in folder structure
# Step 2 : TOPSAR Splitting (Assembling) and Apply Orbit
# Step 3 : Coregistration and Interferogram generation
# Step 4 : StaMPS export

# Added option for CACHE and CPU specification by user
# Planned support for DEM selection and ORBIT type selection


import os
import shutil
import configparser

from log_handler import get_log_handler

config = configparser.ConfigParser()
config.read("./bin/project.ini")

bar_message = (
    "\n#####################################################################\n"
)

# Getting configuration variables from inputfile
PROJECT = os.getcwd()

##############################################################################
#### Slaves sortering in folders ########################
##############################################################################
logfolder = PROJECT + "/logs"
if not os.path.exists(logfolder):
    os.makedirs(logfolder)

logger = get_log_handler(f"{logfolder}/split_proc_stdout.log")

directory = PROJECT + "/slaves"
for filename in os.listdir(directory):
    if filename.endswith(".zip"):
        logger.info(os.path.join(directory, filename))
        head, tail = os.path.split(os.path.join(directory, filename))
        logger.info(tail[17:25])
        subdirectory = directory + "/" + tail[17:25]
        if not os.path.exists(subdirectory):
            os.makedirs(subdirectory)
        #### Moving files
        source = os.path.join(directory, filename)
        destination = os.path.join(subdirectory, tail)
        logger.info("Moving " + source + " to " + destination)
        shutil.move(source, destination)
    else:
        logger.info(f"{filename} is not a .zip")
