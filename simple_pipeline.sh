#
# CWITOOLS - SIMPLE PIPELINE EXAMPLE - Extracting nebular emission around a QSO
#
# You can copy/paste these commands into your terminal to run them one at a time, or run the script.
# This pipeline follows a typical flow: correct, coadd, extract signal, make scientific products.
#

# Step 1 - Cropping the data cubes.
cwi_crop example.list -ctype icubes.fits mcubes.fits vcubes.fits -xcrop 5 28 -ycrop 15 80 -wcrop 4085 6079

# Step 2-A - Measure the coordinate system to create a 'WCS correction table'
cwi_measure_wcs example.list -ctype icubes.c.fits -xymode src_fit -zmode xcor -radec 149.689272107 47.056788021 -plot

# Step 2-B - Apply the new WCS table to the cropped data cubes
cwi_apply_wcs example.wcs -ctype icubes.c.fits mcubes.c.fits vcubes.c.fits

# Step 3 - Subtract the QSO from the input cubes
# We mask nebular emission at a redshift z with a line-width of 750 km/s. We also mask the
# wavelength ranges 4210A:4270A and 5570A:558A, which contain broad LyA and a sky line.
# Masking these regions improves the empirical PSF model.
cwi_psf_sub icubes.c.wc.fits -clist example.list -radec 149.689272107 47.056788021 -r_fit 1.0 -r_sub 5.0 -mask_neb_z 2.49068 -mask_neb_dv 750 -wmask 4210:4270 5570:5585 -var vcubes.c.wc.fits

# Step 4A - Coadd the cropped, wcs-corrected data cubes
cwi_coadd example.list -ctype icubes.c.wc.fits -masks mcubes.c.wc.fits -var vcubes.c.wc.fits -verbose -out example_coadd.fits

# Step 4B - Coadd the PSF-subtracted data cubes
cwi_coadd example.list -ctype icubes.c.wc.ps.fits -masks mcubes.c.wc.fits -var icubes.c.wc.ps.var.fits -verbose -out example_coadd.ps.fits

# Step 5 - Subtract residual background
# Again, we mask the same wavelengths to avoid over-fitting signal.
cwi_bg_sub example_coadd.fits -method polyfit -poly_k 3 -var example_coadd.var.fits -mask_neb_z 2.49068 -mask_neb_dv 750 -wmask 4210:4270 5570:5585

# Step 6A - Create source mask for the coadd based on our DS9 region file
cwi_get_mask example.reg example_coadd.fits -out psf_mask.fits

# Step 6B - Apply the mask to the data and variance
cwi_apply_mask psf_mask.fits example_coadd.ps.bs.fits
cwi_apply_mask psf_mask.fits example_coadd.ps.bs.var.fits

# Step 7 - Segment into contiguous regions above 2-sigma, greater than 1000 voxels in size
cwi_segment example_coadd.ps.bs.M.fits example_coadd.ps.bs.var.M.fits -snr_min 2.0 -n_min 1000

# At this point, you would inspect the output cube (".obj.fits") and note the ID of objects,
# e.g. "object 3 is a giant LyA nebula, object 10 appears to be CIV emission"
#
# Once you have an object ID - you can use the section below to generate data products
# Just change the bash variables 'obj_id' and 'obj_label' to whatever you want

obj_id=1
obj_label="LyA"

# Step 8A - Get an object surface brightness map
cwi_obj_sb example_coadd.ps.bs.M.fits example_coadd.ps.bs.M.obj.fits $obj_id -var example_coadd.ps.bs.var.M.fits -ext $obj_label.fits

# Step 8B - Get first and second moment maps (i.e. velocity and dispersion)
cwi_obj_zmoments example_coadd.ps.bs.M.fits example_coadd.ps.bs.M.obj.fits $obj_id -var example_coadd.ps.bs.var.M.fits -ext $obj_label.fits

# Step 8C- Get an integrated object spectrum
cwi_obj_spec example_coadd.ps.bs.M.fits example_coadd.ps.bs.M.obj.fits $obj_id -var example_coadd.ps.bs.var.M.fits.fits -ext $obj_label.fits

# Step 8D - Get a radial surface brightness profile of the object
cwi_obj_rprof example_coadd.ps.bs.M.fits example_coadd.ps.bs.M.obj.fits $obj_id -var example_coadd.ps.bs.var.M.fits.fits -ext $obj_label.fits

# Step 8E - Calculate the object luminosity
cwi_obj_lum example_coadd.ps.bs.M.fits example_coadd.ps.bs.M.obj.fits $obj_id -var example_coadd.ps.bs.var.M.fits.fits -ext $obj_label.fits

#Step 8F - Calculate the object radial extent and eccentricity
cwi_obj_morpho example_coadd.ps.bs.M.fits example_coadd.ps.bs.M.obj.fits $obj_id -var example_coadd.ps.bs.var.M.fits.fits -ext $obj_label.fits
