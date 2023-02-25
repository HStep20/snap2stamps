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

#############################################################################
### TOPSAR Splitting (Assembling) and Apply Orbit section ####
############################################################################
slavefolder = PROJECT + "/slaves"
splitfolder = PROJECT + "/split"
logfolder = PROJECT + "/logs"
graphfolder = PROJECT + "/graphs"
if not os.path.exists(splitfolder):
    os.makedirs(splitfolder)
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
if not os.path.exists(graphfolder):
    os.makedirs(graphfolder)

graph2run = PROJECT + "/graphs/splitgraph2run.xml"

logger = get_log_handler(f"{logfolder}/split_proc_stdout.log")

logger.info("## TOPSAR Splitting and Apply Orbit")

k = 0
for k, acdatefolder in enumerate(sorted(os.listdir(slavefolder))):
    k = k + 1
    logger.info("[" + str(k) + "] Folder: " + acdatefolder)
    logger.info(os.path.join(slavefolder, acdatefolder))
    files = glob.glob(os.path.join(slavefolder, acdatefolder) + "/*.zip")
    logger.info(files)
    head, tail = os.path.split(os.path.join(str(files)))
    splitslavefolder = splitfolder + "/" + tail[17:25]
    if not os.path.exists(splitslavefolder):
        os.makedirs(splitslavefolder)
    outputname = tail[17:25] + "_" + IW + ".dim"
    if len(files) == 1:
        graphxml = GRAPH + "/slave_split_applyorbit.xml"
        # Read in the file
        logger.info("FILE(s) : " + files[0])
        with open(graphxml, "r") as file:
            filedata = file.read()
        # Replace the target string
        filedata = filedata.replace("INPUTFILE", files[0])
        filedata = filedata.replace("IWs", IW)
        filedata = filedata.replace("OUTPUTFILE", splitslavefolder + "/" + outputname)
        # # Write the file out again
        with open(graph2run, "w") as file:
            file.write(filedata)
    if len(files) > 1:
        graphxml = GRAPH + "/slaves_assemble_split_applyorbit.xml"
        with open(graphxml, "r") as file:
            filedata = file.read()
        # Replace the target string
        filedata = filedata.replace("INPUTFILE1", files[0])
        filedata = filedata.replace("INPUTFILE2", files[1])
        filedata = filedata.replace("IWs", IW)
        filedata = filedata.replace("OUTPUTFILE", splitslavefolder + "/" + outputname)
        # Write the file out again
        with open(graph2run, "w") as file:
            file.write(filedata)

    args = [GPT, graph2run, "-c", CACHE, "-q", CPU]
    logger.info(args)
    # launching the process
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    timeStarted = time.time()
    stdout = process.communicate()[0]
    logger.info("SNAP STDOUT:{}".format(stdout))
    # Get execution time.
    timeDelta = time.time() - timeStarted
    logger.info("[" + str(k) + "] Finished process in " + str(timeDelta) + " seconds.")
    if process.returncode != 0:
        logger.error(f"Error splitting slave {str(files)}")
    else:
        logger.info(f"Split slave {str(files)} successfully completed.")
    logger.info(bar_message)
