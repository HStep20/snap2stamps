# Python script to use SNAP as InSAR processor compatible with StaMPS PSI processing
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
import glob
import subprocess
import time

import configparser
from log_handler import get_log_handler

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

masterfolder = PROJECT + "/master"
splitfolder = PROJECT + "/MasterSplit"
logfolder = PROJECT + "/logs"
graphfolder = PROJECT + "/graphs"
slavefolder = PROJECT + "/slaves"
if not os.path.exists(splitfolder):
    os.makedirs(splitfolder)
if not os.path.exists(logfolder):
    os.makedirs(logfolder)
if not os.path.exists(graphfolder):
    os.makedirs(graphfolder)

logger = get_log_handler(f"{logfolder}/split_proc_stdout.log")
try:
    POLARISATION = config.get("Production", "POLARISATION")
except:
    logger.error("POLARISATION not found in config file")

graph2run = PROJECT + "/graphs/splitgraph2run.xml"
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
print(polygon)
#############################################################################
### TOPSAR Splitting (Assembling) and Apply Orbit section ####
############################################################################


logger.info(bar_message)
logger.info("## TOPSAR Splitting and Apply Orbit\n")
logger.info(bar_message)
k = 0
for acdatefolder in sorted(os.listdir(masterfolder)):
    k = k + 1
    logger.info("[" + str(k) + "] Folder: " + acdatefolder)
    logger.info(os.path.join(masterfolder, acdatefolder))
    files = glob.glob(os.path.join(masterfolder, acdatefolder) + "/*.zip")
    if not os.path.exists(str(files)):
        files = glob.glob(
            os.path.join(slavefolder, acdatefolder) + "/*.SAFE/manifest.safe"
        )
    logger.info(str(files))
    splitmasterfolder = splitfolder + "/" + acdatefolder
    if not os.path.exists(splitmasterfolder):
        os.makedirs(splitmasterfolder)
        IWlist = ["IW1", "IW2", "IW3"]
        for IW in IWlist:
            outputname = acdatefolder + "_" + IW + ".dim"
            if len(files) == 1:
                graphxml = GRAPH + "/master_split_applyorbit.xml"
                # Read in the file
                logger.info("FILE(s) : " + files[0])
                with open(graphxml, "r") as file:
                    filedata = file.read()
                    # Replace the target string
                filedata = filedata.replace("INPUTFILE", files[0])
                filedata = filedata.replace("IWs", IW)
                filedata = filedata.replace("POLARISATION", POLARISATION)
                filedata = filedata.replace("POLYGON", polygon)
                filedata = filedata.replace(
                    "OUTPUTFILE", splitmasterfolder + "/" + outputname
                )
                # # Write the file out again
                with open(graph2run, "w") as file:
                    file.write(filedata)
            if len(files) == 2:
                graphxml = GRAPH + "/master_assemble_split_applyorbit2.xml"
                with open(graphxml, "r") as file:
                    filedata = file.read()
                    # Replace the target string
                filedata = filedata.replace("INPUTFILE1", files[0])
                filedata = filedata.replace("INPUTFILE2", files[1])
                filedata = filedata.replace("IWs", IW)
                filedata = filedata.replace("POLARISATION", POLARISATION)
                filedata = filedata.replace("POLYGON", polygon)
                filedata = filedata.replace(
                    "OUTPUTFILE", splitmasterfolder + "/" + outputname
                )
                # Write the file out again
                with open(graph2run, "w") as file:
                    file.write(filedata)

args = [GPT, graph2run, "-c", CACHE, "-q", CPU]
logger.info(args)
# launching the process
process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
timeStarted = time.time()
stdout = process.communicate()[0]
print("SNAP STDOUT:{}".format(stdout))
timeDelta = time.time() - timeStarted  # Get execution time.
logger.info("[" + str(k) + "] Finished process in " + str(timeDelta) + " seconds.\n")
if process.returncode != 0:
    logger.error(f"Error splitting slave {str(files)}")
else:
    logger.info(f"Split slave {str(files)} successfully completed.")
    logger.info(bar_message)
logger.info(bar_message)
