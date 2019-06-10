import sys,os;
from build_objects import manifest;

##---------------------------------------------------------------------------##
## Step 10
## Check for incoming manifest
##---------------------------------------------------------------------------##
manifest_location = r"/home/ubuntu/target/manifest.json";

if not os.path.exists(manifest_location):
   raise Exception('manifest.json file not found in target location.');
   
##---------------------------------------------------------------------------##
## Step 20
## Load the manifest workload
##---------------------------------------------------------------------------##
workload = manifest(filename=manifest_location);

##---------------------------------------------------------------------------##
## Step 30
## Generate the concatenated results
##---------------------------------------------------------------------------##
workload.concatenate();

