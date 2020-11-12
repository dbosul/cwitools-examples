# CWITOOLS - SIMPLE PIPELINE EXAMPLE - Extracting nebular emission around a QSO
#
# This script provides example of how to use CWITools' Scripts Module within a Python script.
#
#
# The pipeline shown here follows a typical flow: correct data, coadd data,
# extract 3D signal, and then make scientific products.
#
from cwitools.scripts import *

#Turn individual steps on and off here by setting stages to 1 (ON) or 0 (OFF)
crop    = 0
fix_wcs = 0
psf_sub = 0
coadd   = 0
bg_sub  = 0
mask    = 0
var     = 0
segment = 0
results = 0

#Use this to run all steps (over-rides others)
ALL = 0

# Step 1 - Cropping
if crop or ALL:
    cwi_crop(
        "example.list",
        ctype=["icubes.fits", "mcubes.fits", "vcubes.fits", "ocubes.fits"],
        xcrop=(5, 28),
        ycrop=(15, 80),
        wcrop=(5300, 5500)
    )

# Step 2: WCS Correction
if fix_wcs or ALL:
    #2A - Measure the coordinate system to create a 'WCS correction table'
    cwi_measure_wcs(
        "example.list",
        ctype="icubes.c.fits",
        xymode="src_fit",
        zmode="xcor",
        radec=(149.689272107, 47.056788021),
        plot=False
    )
    #2B - Apply the new WCS table to the cropped data cubes
    cwi_apply_wcs(
        "example.wcs",
        ctypes=["icubes.c.fits", "mcubes.c.fits", "vcubes.c.fits"]
    )

# Step 3 - Point-source Subtraction
if psf_sub or ALL:
    cwi_psf_sub(
        "icubes.c.wc.fits",
        clist="example.list",
        radec=(149.689272107, 47.056788021),
        r_fit=1.0,
        r_sub=5.0,
        mask_neb_z=2.49068, #Masking nebular emission at a redshift of 2.49068
        mask_neb_dv=750, #Velocity width of nebular emission mask
        wmask=[(5390, 5425)], #Manually masking CIV emission based on visual inspection
        var="vcubes.c.wc.fits"
    )

# Step 4 - Coadding
if coadd or ALL:
    #4A - Coadding the cropped, wcs-corrected data cubes
    cwi_coadd(
        "example.list",
        ctype="icubes.c.wc.fits",
        masks="mcubes.c.wc.fits",
        var="vcubes.c.wc.fits",
        verbose=True,
        out="example_coadd.fits"
    )
    #4B - Coadd the PSF-subtracted data cubes
    cwi_coadd(
        "example.list",
        ctype="icubes.c.wc.ps.fits",
        masks="mcubes.c.wc.fits",
        var="icubes.c.wc.ps.var.fits",
        verbose=True,
        out="example_coadd.ps.fits"
    )

# Step 5 - Subtract residual background
if bg_sub or ALL:
    cwi_bg_sub(
        "example_coadd.ps.fits",
        method="polyfit",
        poly_k=3,
        var="example_coadd.ps.var.fits",
        mask_neb_z=2.49068,
        mask_neb_dv=750,
        wmask=[(5390, 5425)]
    )

#Step 6 - Masking
if mask or ALL:
    #6A - Create PSF mask for the coadd based on our DS9 region file
    cwi_get_mask("example.reg", "example_coadd.fits", out="psf_mask.fits")
    #6B - Apply the mask to the data and variance
    cwi_apply_mask("psf_mask.fits", "example_coadd.ps.bs.fits")
    cwi_apply_mask("psf_mask.fits", "example_coadd.ps.bs.var.fits")

#Step 7 - Variance
if var or ALL:
    #7A - Scale the variance to match the background noise properties
    cwi_scale_var(
        "example_coadd.ps.bs.M.fits",
        "example_coadd.ps.bs.var.M.fits",
        snr_min=2.5,
        n_min=30
    )
    #7B - Measure the covariance of the data as a function of bin size
    cwi_fit_covar(
        "example_coadd.ps.bs.M.fits",
        "example_coadd.ps.bs.var.M.scaled.fits",
        wrange=(5300, 5500),
        xybins=range(1, 10),
        plot=True
    )

#Step 8 - Segmentation
if segment or ALL:
    cwi_segment(
        "example_coadd.ps.bs.M.fits",
        "example_coadd.ps.bs.var.M.scaled.fits",
        n_min=100,
        snr_min=3,
        include=[(5380, 5435)]
    )

#Step 9 - Generate scientific products
if results or ALL:
    #9A - Surface brightness map
    cwi_obj_sb(
        "example_coadd.ps.bs.M.fits", #Intensity cube
        "example_coadd.ps.bs.M.obj.fits", #Object cube
        1, #object ID
        var="example_coadd.ps.bs.var.M.scaled.fits",
        label="CIV"
    )
    #9B - Integrated spectrum
    cwi_obj_spec(
        "example_coadd.ps.bs.M.fits", #Intensity cube
        "example_coadd.ps.bs.M.obj.fits", #Object cube
        1, #object ID
        var="example_coadd.ps.bs.var.M.scaled.fits",
        label="CIV"
    )
    #9C - Radial profile
    cwi_get_rprof(
        "example_coadd.ps.bs.M.CIV_sb.fits", #CIV SB map
        (149.689272107, 47.056788021), #Central coordinate
        pos_type="radec",
        r_min=20,
        r_max=100,
        r_unit="pkpc",
        scale="log",
        n_bins=10,
        var="example_coadd.ps.bs.M.CIV_sb.var.fits",
        redshift=2.49068
    )
    #9D - Kinematic maps. We use line-fitting here because CIV is a doublet
    cwi_obj_zfit(
        "example_coadd.ps.bs.M.fits", #Intensity cube
        "example_coadd.ps.bs.M.obj.fits", #Object cube
        (1548, 1550), #Doublet peaks
        obj_id=1,
        redshift=2.49068,
        unit="kms",
        var="example_coadd.ps.bs.var.M.scaled.fits",
        label="CIV"
    )
