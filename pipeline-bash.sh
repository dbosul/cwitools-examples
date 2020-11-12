#
# CWITOOLS - SIMPLE PIPELINE EXAMPLE - Extracting nebular emission around a QSO
#
# This script provides example of how to use CWITools from the command-line in
# a linux environment, and should extend simply to MacOS environments as well.
#
#
# The pipeline shown here follows a typical flow: correct data, coadd data,
# extract 3D signal, and then make scientific products.
#

# Step 1 - Cropping the data cubes.
cwi_crop example.list -ctype icubes.fits mcubes.fits vcubes.fits ocubes.fits -xcrop 5 28 -ycrop 15 80 -wcrop 5300 5500

# Step 2-A - Measure the coordinate system to create a 'WCS correction table'
cwi_measure_wcs example.list -ctype icubes.c.fits -xymode src_fit -radec 149.689272107 47.056788021 -zmode xcor -sky_type ocubes.c.fits -plot

# Step 2-B - Apply the new WCS table to the cropped data cubes
cwi_apply_wcs example.wcs icubes.c.fits mcubes.c.fits vcubes.c.fits

# Step 3 - Subtract the QSO from the input cubes
cwi_psf_sub icubes.c.wc.fits -clist example.list -radec 149.689272107 47.056788021 -r_fit 1.0 -r_sub 5.0 -mask_neb_z 2.49068 -mask_neb_dv 750 -wmask 5390:5425 -var vcubes.c.wc.fits

# Step 4A - Coadd the cropped, wcs-corrected data cubes
cwi_coadd example.list -ctype icubes.c.wc.fits -masks mcubes.c.wc.fits -var vcubes.c.wc.fits -verbose -out example_coadd.fits

# Step 4B - Coadd the PSF-subtracted data cubes
cwi_coadd example.list -ctype icubes.c.wc.ps.fits -masks mcubes.c.wc.fits -var icubes.c.wc.ps.var.fits -verbose -out example_coadd.ps.fits

# Step 5 - Subtract residual background
# Again, we mask the same wavelengths to avoid over-fitting signal.
cwi_bg_sub example_coadd.ps.fits -method polyfit -poly_k 3 -var example_coadd.ps.var.fits -mask_neb_z 2.49068 -mask_neb_dv 750 -wmask 5390:5425

#Step 6A - Create source mask for the coadd based on our DS9 region file
cwi_get_mask example.reg example_coadd.fits -out psf_mask.fits

#Step 6B - Apply the mask to the data and variance
cwi_apply_mask psf_mask.fits example_coadd.ps.bs.fits
cwi_apply_mask psf_mask.fits example_coadd.ps.bs.var.fits

#Step 7A - Scale the variance to match the background noise properties
cwi_scale_var example_coadd.ps.bs.M.fits  example_coadd.ps.bs.var.M.fits -snr_min 2.5 -n_min 30

#Step 7B - Measure the covariance of the data as a function of bin size
cwi_fit_covar example_coadd.ps.bs.M.fits example_coadd.ps.bs.var.M.scaled.fits -wrange 5300 5500

#Step 8 - Segment the data into regions above a particular signal-to-noise ratio. Exclude sky line.
cwi_segment example_coadd.ps.bs.M.fits example_coadd.ps.bs.var.M.scaled.fits -n_min 30 -snr_min 3 -include 5390:5425

#Step 9 - Create data products for the object which should have been detected (Obj #1 - a giant LyA nebula)
#9A - Surface brightness map
cwi_obj_sb example_coadd.ps.bs.M.fits example_coadd.ps.bs.M.obj.fits 1 -label CIV -var example_coadd.ps.bs.var.M.scaled.fits

#9B - Integrated spectrum
cwi_obj_spec example_coadd.ps.bs.M.fits example_coadd.ps.bs.M.obj.fits 1 -label CIV -var example_coadd.ps.bs.var.M.scaled.fits

#9C - Radial profile
cwi_get_rprof example_coadd.ps.bs.M.CIV_sb.fits 149.689272107 47.056788021 -pos_type radec -r_min 20 -r_max 100 -n_bins 10 -r_unit pkpc -scale lin -var example_coadd.ps.bs.M.CIV_sb.var.fits -redshift 2.49068

#9D - 2D Maps of kinematic moments, we use line-fitting here instead of statistical moments because CIV is a doublet
cwi_obj_zfit example_coadd.ps.bs.M.fits example_coadd.ps.bs.M.obj.fits 1548 1550 -obj_id 1 -redshift 2.49068 -unit kms -var example_coadd.ps.bs.var.M.scaled.fits -label CIV
