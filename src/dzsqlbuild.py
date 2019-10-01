import sys,os;
from build_objects import manifest;

##---------------------------------------------------------------------------##
## Step 10
## Check for incoming manifest
##---------------------------------------------------------------------------##
base    = os.environ['DZBASE'];
gitbase = os.environ['DZGITBASE'];

subdir = os.environ['DZSUBDIR'];
if subdir is None or subdir == "":
   manifest_location = gitbase + r"/manifest.json";
else:
   subdir = r"/" + subdir.strip("/");
   manifest_location = gitbase + subdir + r"/manifest.json";

if not os.path.exists(manifest_location):
   raise Exception('manifest.json file not found in target location.');
   
##---------------------------------------------------------------------------##
## Step 20
## Load the manifest workload
##---------------------------------------------------------------------------##
workload = manifest(base=base,gitbase=gitbase,subdirectory=subdir);

##---------------------------------------------------------------------------##
## Step 30
## Generate the concatenated results
##---------------------------------------------------------------------------##
workload.run();

