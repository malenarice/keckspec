## Description

This program is designed to output 18 stellar labels from input, continuum-normalized Keck HIRES spectra. The labels returned are Teff, logg, vsini, [Fe/H], [C/H], [N/H], [O/H], [Na/H], [Mg/H], [Al/H], [Si/H], [Ca/H], [Ti/H], [V/H], [Cr/H], [Mn/H], [Ni/H], and [Y/H]. The user inputs the fluxes and inverse variances at each wavelength value, and label estimates are outputted. 


## Getting Started

Complete the following steps to get this model up and running on your computer:

1. Download the GitHub repo available here.

2. Navigate to [this link](www.astro.yale.edu/malenarice/keckspec) to download the trained model file spocstrained_post2004.model. This file is 1.33 GB and contains the saved model. Move this file into the "keckspec" folder downloaded from Github.

3. Run the return_labels function in run_trainedmodel_keck_post2004.py with your input spectra. The two inputs required are normalized flux and inverse variances, and the code will output a .csv file called "stellar_labels.csv" containing the predicted stellar labels.


## Notes

To obtain reliable results, the input fluxes MUST be reported at wavelength values that match up with those that were used to train our supervised learning algorithm. These wavelengths can be found in the folder examples/HD22072/wavelengths.txt along with example flux and inverse variance files. To support the user, we have provided an interpolation scheme ('interpolate_wavelengths' in supplementary_functions.py) that will convert spectra to this wavelength range.
