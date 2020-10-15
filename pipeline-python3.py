# CWITOOLS - SIMPLE PIPELINE EXAMPLE - Extracting nebular emission around a QSO
#
# This script provides example of how to use CWITools' Scripts Module within a Python script.
#
#
# The pipeline shown here follows a typical flow: correct data, coadd data,
# extract 3D signal, and then make scientific products.
#
from cwitools.scripts import *

# Step 1 - Cropping the data cubes.
cwi_crop(
    "example.list",
    ctype=["icubes.fits", "mcubes.fits", "vcubes.fits"],
    xcrop=(5, 28),
    ycrop=(15, 80),
    wcrop=(4085, 6079)
)

# Step 2-A - Measure the coordinate system to create a 'WCS correction table'
cwi_measure_wcs(
    "example.list",
    ctype="icubes.c.fits",
    xymode="src_fit",
    zmode="xcor",
    radec=(149.689272107, 47.056788021),
    plot=False
)

# Step 2-B - Apply the new WCS table to the cropped data cubes
cwi_apply_wcs(
    "example.wcs",
    ctypes=["icubes.c.fits", "mcubes.c.fits", "vcubes.c.fits"]
)

# Step 3 - Subtract the QSO from the input cubes
cwi_psf_sub(
    "icubes.c.wc.fits",
    clist="example.list",
    radec=(149.689272107, 47.056788021),
    r_fit=1.0,
    r_sub=5.0,
    mask_neb_z=2.49068, #Masking nebular emission at a redshift of 2.49068
    mask_neb_dv=750, #Velocity width of nebular emission mask
    wmask=[(4210, 4270), (5570, 5585)], #Masking broad LyA and a sky-line at ~5577A
    var="vcubes.c.wc.fits"
)

# Step 4A - Coadd the cropped, wcs-corrected data cubes
cwi_coadd(
    "example.list",
    ctype="icubes.c.wc.fits",
    masks="mcubes.c.wc.fits",
    var="vcubes.c.wc.fits",
    verbose=True,
    out="example_coadd.fits"
)

# Step 4B - Coadd the PSF-subtracted data cubes
cwi_coadd(
    "example.list",
    ctype="icubes.c.wc.ps.fits",
    masks="mcubes.c.wc.fits",
    var="icubes.c.wc.ps.var.fits",
    verbose=True,
    out="example_coadd.ps.fits"
)

# Step 5 - Subtract residual background
cwi_bg_sub(
    "example_coadd.ps.fits",
    method="polyfit",
    poly_k=3,
    var="example_coadd.ps.var.fits",
    mask_neb_z=2.49068,
    mask_neb_dv=750,
    wmask=[(4210, 4270), (5570, 5585)]
)

#Step 6A - Create PSF mask for the coadd based on our DS9 region file
cwi_get_mask("example.reg", "example_coadd.fits", out="psf_mask.fits")

#Step 6B - Apply the mask to the data and variance
cwi_apply_mask("psf_mask.fits", "example_coadd.ps.bs.fits")
cwi_apply_mask("psf_mask.fits", "example_coadd.ps.bs.var.fits")

#Step 7A - Scale the variance to match the background noise properties
cwi_scale_var(
    "example_coadd.ps.bs.M.fits",
    "example_coadd.ps.bs.var.M.fits",
    snr_min=2.5,
    n_min=30
)

#Step 7B - Measure the covariance of the data as a function of bin size
cwi_fit_covar(
    "example_coadd.ps.bs.M.fits",
    "example_coadd.ps.bs.var.M.scaled.fits",
    wrange=(4300, 5500),
    xybins=range(1, 10),
    plot=True
)

#Step 8 - Segment the data into regions above a particular signal-to-noise ratio. Exclude sky line.
cwi_segment(
    "example_coadd.ps.bs.M.fits",
    "example_coadd.ps.bs.var.M.scaled.fits",
    n_min=100,
    snr_min=3,
    include=[(4225, 4260)]
)

#
# At this point,
#
