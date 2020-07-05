## Description

This program is designed to output 18 stellar labels from input, continuum-normalized Keck HIRES spectra. The labels returned are Teff, logg, vsini, [Fe/H], [C/H], [N/H], [O/H], [Na/H], [Mg/H], [Al/H], [Si/H], [Ca/H], [Ti/H], [V/H], [Cr/H], [Mn/H], [Ni/H], and [Y/H]. The user inputs the fluxes and inverse variances at each wavelength value, and label estimates are outputted. We direct the user to Rice & Brewer 2020 for a detailed explanation of the code and its performance.


## Getting Started

Complete the following steps to get this model up and running on your computer:

1. Download the GitHub repo available at this site.

2. Make sure that you have an updated installation of The Cannon on your computer. Instructions for this installation can be found at https://github.com/andycasey/AnniesLasso.

3. Navigate to www.astro.yale.edu/malenarice/#keckspec to download the trained model file spocstrained_post2004.model. This file is 1.33 GB and contains the saved model. Move this file into the "keckspec" folder downloaded from Github.

4. Run the return_labels function in run_trainedmodel_keck_post2004.py with your input spectra. The two inputs required are normalized flux and inverse variances, and the code will output a .csv file called "stellar_labels.csv" containing the predicted stellar labels.



Below is a simple example label extraction for the star HD 22072, with all required files located in the 'examples' folder.

```python
import numpy as np
from run_trainedmodel_keck_post2004 import return_labels

example_folder_path = "../examples/HD22072/"

# Load the normalized fluxes and inverse variances for the star
flux = np.loadtxt(example_folder_path + "flux_HD22072_flat.txt")
ivar = np.loadtxt(example_folder_path + "ivar_HD22072_flat.txt")

# Provide the star's name (optional)
star_names = np.array(['HD 22072'])

return_labels(flux, ivar, star_names=star_names)
```

This program will output a file called 'stellar_labels.csv' that includes the output stellar labels determined by the model.

## Getting your spectra to the correct input format

The previous example assumed that your input spectra are already continuum-normalized and interpolated to the correct wavelength values. But what if they aren't?

In the example below, we determine stellar labels from a raw extracted HIRES spectrum, with each step included for clarity. Note that, for the continuum renormalization described in this section, you will also need to download the trained model file spocstrained_post2004_notelluricmask.model at www.astro.yale.edu/malenarice/#keckspec.


```python
import numpy as np
from run_trainedmodel_keck_post2004 import return_labels
from supplementary_functions import *

example_folder_path = "../examples/HD22072/raw_extracted_files/"

# Load the raw fluxes and uncertainties for the star
flux = np.loadtxt(example_folder_path + "flux_HD22072_raw.txt")
sigma = np.loadtxt(example_folder_path + "sigma_HD22072_raw.txt")

# Load the continuum fit to normalize each order of your spectrum 
cont = np.loadtxt(example_folder_path + "continuum_HD22072_raw.txt")

# Interpolate wavelengths to match the wavelengths.txt file listed 
# in "examples/HD22072". This function also normalizes the flux and 
# extracts the uncertainty for the interpolated wavelengths.
wv_interp_from = np.loadtxt(example_folder_path + "wavelengths_HD22072_raw.txt")
wv_interp_to = np.loadtxt("../examples/HD22072/wavelengths.txt") 
flux_norm_interp, sigma_norm_interp = interpolate_wavelengths(flux, cont, wv_interp_from, wv_interp_to)


# We have developed all of the following functions to require flattened arrays, 
# where all echelle orders are placed side-by-side. While this example shows the 
# setup for a single star, this makes it easier to handle many stars in bulk. 

# Flatten the arrays
flux_norm_interp_flat = np.ndarray.flatten(flux_norm_interp)
sigma_norm_interp_flat = np.ndarray.flatten(sigma_norm_interp)
wv_flat = np.ndarray.flatten(wv_interp_to)

# Run the data-driven continuum renormalization (optional, but recommended)
flux_renorm_interp_flat, sigma_renorm_interp_flat = continuum_renorm_poly(flux_norm_interp_flat, sigma_norm_interp_flat, wv_flat)

# Switch from uncertainty to inverse variance
ivar_renorm_interp_flat = 1./(sigma_renorm_interp_flat**2.)

# Provide the star's name (optional)
star_names = np.array(['HD 22072'])

# Return labels
return_labels(flux_renorm_interp_flat, ivar_renorm_interp_flat, star_names=star_names)
```

## Acknowledgement
If you use this code for your own research or would otherwise like to acknowledge it, we ask that you cite the associated paper Rice & Brewer 2020.


## Notes

To obtain reliable results, the input fluxes MUST be reported at wavelength values that match up with those that were used to train our supervised learning algorithm. These wavelengths can be found in the folder examples/HD22072 along with example flux and inverse variance files. To support the user, we have provided an interpolation scheme ('interpolate_wavelengths' in supplementary_functions.py) that will convert spectra to this wavelength range. See above for an example of how to use this function.

The input spectra must also be continuum-normalized in a manner that preserves the relative depths of all spectral lines as compared to the continuum. We provide an example raw spectrum and its associated continuum fit for reference in the folder examples/HD22072. This continuum was fit using a legacy code described in Valenti & Fischer 2005. An open-source continuum-fitting code is in development to be added to this site but is not yet available.
