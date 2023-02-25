### Python script to use SNAP as InSAR processor compatible with StaMPS PSI processing
# Author Jose Manuel Delgado Blasco
# Updated by HStep20 and gdm020
# Date: 2023-02-24
# Version: 2.0

# Step 1 : preparing slaves in folder structure
# Step 2 : TOPSAR Splitting (Assembling) and Apply Orbit
# Step 3 : Coregistration and Interferogram generation
# Step 4 : StaMPS export

# Added option for CACHE and CPU specification by user
# Planned support for DEM selection and ORBIT type selection


import os
from pathlib import Path
import sys
import glob
import subprocess
import shlex
import time
import re

from log_handler import get_log_handler

import configparser

config = configparser.ConfigParser()
config.read("./bin/project.ini")

bar_message = "#####################################################################"


PROJECT = os.getcwd()
GRAPH = f"{os.getcwd()}/graphs/"
IW = config.get("Production", "IW1")
MASTER = config.get("Production", "MASTER")
GPT = config.get("Production", "GPTBIN_PATH")
LONMIN = config.get("Production", "LONMIN")
LONMAX = config.get("Production", "LONMAX")
LATMIN = config.get("Production", "LATMIN")
LATMAX = config.get("Production", "LATMAX")
CACHE = config.get("Production", "CACHE")
CPU = config.get("Production", "CPU")


slavesplittedfolder = PROJECT + "/split"
outputcoregfolder = PROJECT + "/coreg"
outputifgfolder = PROJECT + "/ifg"
logfolder = PROJECT + "/logs"
if not os.path.exists(outputcoregfolder):
    os.makedirs(outputcoregfolder)
if not os.path.exists(outputifgfolder):
    os.makedirs(outputifgfolder)
if not os.path.exists(logfolder):
    os.makedirs(logfolder)

logger = get_log_handler(f"{logfolder}/coreg_ifg_proc_stdout.log")

if not os.path.exists(MASTER):
    logger.error(f"{MASTER} path does not exist on system")
    exit()


polygon = (
    "POLYGON (("
    + LONMIN
    + " "
    + LATMIN
    + ","
    + LONMAX
    + " "
    + LATMIN
    + ","
    + LONMAX
    + " "
    + LATMAX
    + ","
    + LONMIN
    + " "
    + LATMAX
    + ","
    + LONMIN
    + " "
    + LATMIN
    + "))"
)

logger.info(f"Using Polygon: {polygon}")

######################################################################################
## TOPSAR Coregistration and Interferogram formation ##
######################################################################################


# Check SNAP Version for correct GRAPH
args = ["gpt", "--diag"]
process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
stdout = process.communicate()[0]
stdout_lines = str(stdout).lower()
snap_release_version = re.search(
    "snap release version [0-9]+.[0-9]+", stdout_lines
).group()
snapversion = re.search("[0-9]+.[0-9]+", snap_release_version).group()
graph2run = GRAPH + "/coreg_ifg2run.xml"
if float(snapversion) < 7:
    graphxml = GRAPH + "/coreg_ifg_computation_subset_legacy.xml"
else:
    graphxml = GRAPH + "/coreg_ifg_computation_subset.xml"

logger.info(graphxml)
logger.info("## Coregistration and Interferogram computation started:")


k = 0
split_files = glob.iglob(slavesplittedfolder + "/*/*" + IW + ".dim")

for k, dimfile in enumerate(split_files):
    logger.info(dimfile)
    head, tail = os.path.split(os.path.join(slavesplittedfolder, dimfile))
    logger.info(f"[{str(k)}] Processing slave file : {tail}")
    head, tailm = os.path.split(MASTER)
    outputname = tailm[17:25] + "_" + tail[0:8] + "_" + IW + ".dim"
    with open(graphxml, "r") as file:
        filedata = file.read()
    # Replace the target string
    filedata = filedata.replace("MASTER", MASTER)
    filedata = filedata.replace("SLAVE", dimfile)
    filedata = filedata.replace("OUTPUTCOREGFOLDER", outputcoregfolder)
    filedata = filedata.replace("OUTPUTIFGFOLDER", outputifgfolder)
    filedata = filedata.replace("OUTPUTFILE", outputname)
    filedata = filedata.replace("POLYGON", polygon)
    # Write the file out again
    with open(graph2run, "w") as file:
        file.write(filedata)
    args = [GPT, graph2run, "-c", CACHE, "-q", CPU]
    # Launch the processing
    process = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    timeStarted = time.time()
    stdout = process.communicate()[0]
    logger.info("SNAP STDOUT:{}".format(stdout))
    timeDelta = time.time() - timeStarted  # Get execution time.
    logger.info("[" + str(k) + "] Finished process in " + str(timeDelta) + " seconds.")

    if process.returncode != 0:
        message = (
            "Error computing with coregistration and interferogram generation of splitted slave "
            + str(dimfile)
        )
        logger.error(message)
    else:
        message = (
            "Coregistration and Interferogram computation for data "
            + str(tail)
            + " successfully completed.\n"
        )
        logger.info(message)
    logger.info(bar_message)
else:
    logger.warning("No .dim Files Found to process")
