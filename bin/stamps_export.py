# Python script to use SNAP as InSAR processor compatible with StaMPS PSI processing
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
from pathlib import Path
import glob
import subprocess
from log_handler import get_log_handler
import time
import configparser


config = configparser.ConfigParser()
config.read("./bin/project.ini")

bar_message = (
    "\n#####################################################################\n"
)


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

###################################################################################
##### StaMPS PSI export ##################
###################################################################################
coregfolder = PROJECT + "/coreg"
ifgfolder = PROJECT + "/ifg"
head, tail = os.path.split(MASTER)
outputexportfolder = PROJECT + "/INSAR_" + tail[17:25]
logfolder = PROJECT + "/logs"

if not os.path.exists(outputexportfolder):
    os.makedirs(outputexportfolder)
if not os.path.exists(logfolder):
    os.makedirs(logfolder)


logger = get_log_handler(f"{logfolder}/split_proc_stdout.log")

graphxml = GRAPH + "/export.xml"
graph2run = GRAPH + "/export2run.xml"

logger.info("## StaMPS PSI export started")

k = 0
for dimfile in glob.iglob(coregfolder + "/*" + IW + ".dim"):
    head, tail = os.path.split(os.path.join(coregfolder, dimfile))
    k = k + 1
    message = "[" + str(k) + "] Exporting pair: master-slave pair " + tail
    ifgdim = Path(ifgfolder + "/" + tail)
    logger.info(ifgdim)
    if ifgdim.is_file():
        logger.info(message)
        with open(graphxml, "r") as file:
            filedata = file.read()
        # Replace the target string
        filedata = filedata.replace("COREGFILE", dimfile)
        filedata = filedata.replace("IFGFILE", str(ifgdim))
        filedata = filedata.replace("OUTPUTFOLDER", outputexportfolder)
        # Write the file out again
        with open(graph2run, "w") as file:
            file.write(filedata)
        args = [GPT, graph2run, "-c", CACHE, "-q", CPU]
        logger.info(args)
        # Launching process
        process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        timeStarted = time.time()
        stdout = process.communicate()[0]
        logger.info("SNAP STDOUT:{}".format(stdout))
        # Get execution time.
        timeDelta = time.time() - timeStarted
        logger.info(
            "[" + str(k) + "] Finished process in " + str(timeDelta) + " seconds."
        )

        if process.returncode != 0:
            message = "Error exporting " + str(tail)
            logger.error(message)
        else:
            message = "Stamps export of " + str(tail) + " successfully completed."
            logger.info(message)
        logger.info(bar_message)
