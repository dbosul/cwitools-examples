# CWITools Examples 

This repository contains a folder with some sample data and scripts to help you get familiar with CWITools. 

The folder 'sample-data/' contains a few reduced KCWI data cubes for a FLASHES Survey (O'Sullivan et al. 2020) target. Specficially, it contains 7 exposures, reduced to the flux-calibrated ('cubes.fits') stage. For each exposure, the sky-subtracted intensity ('icubes'), sky + object intensity ('ocubes'), variance ('vcubes.fits') and mask ('mcubes') file-types are included. 

There are two main examples included.

First, "example-bash.sh" is a basic bash script with commands for reducing, coadding, and analyzing the data. You should be able to run this as-is, but we recommend copying/pasting the commands one at a time and executing them yourself. Also, try playing with the parameters and exploring the help menus for each script by passing the '-h' flag. Advanced users, more familiar with bash, can use this as a basis to build a dynamic pipeline using bash variables to substitute things like input files or script parameters.

Second, "example-python3.py" shows the same pipeline, except this one is constructed as a Python script rather than a bash script. Again, users who are familiar with Python can use this as a basis from which to build their own, customizable analysis pipelines with variables for things like input files, target parameters, cropping parameters etc.
