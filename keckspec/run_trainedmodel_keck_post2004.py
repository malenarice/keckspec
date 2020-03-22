import numpy as np
import pandas as pd
import thecannon as tc

def return_labels(normalized_flux, normalized_ivar,
                  save_file=True, star_names=None,
                  save_dir='./'):

    # ---------------------
    #
    # INPUTS:
    # normalized_flux:
    #   - Continuum-normalized fluxes
    #     at each wavelength, with
    #     dimensionality
    #     (number of stars, 64336)
    # normalized_ivar:
    #   - Inverse variances (1/sigma^2)
    #     associated with each flux
    #     measurement, with
    #     dimensionality
    #     (number of stars, 64336)
    # save_file (optional):
    #   - Default: True
    #   - Optional choice to save file
    #     or just return labels as an array
    # star_names (optional):
    #   - Default: None
    #   - Provide star names for easier
    #     readability of code outputs
    # save_dir (optional):
    #   - Default: Saves file in current directory
    #   - Choose directory in which results
    #     are saved
    #
    #
    # OUTPUTS:
    #   - labels: results as a Pandas dataframe
    #     with size (number of stars, 18) where
    #     there are 18 labels returned
    #   - If save_file == True:
    #       -> Saved .csv file providing results
    #          with size (number of stars, 18)
    #
    #
    # NOTES:
    #   - Wavelengths must be interpolated
    #     to the training set wavelength
    #     scale. Echelle orders placed in
    #     order from highest to lowest
    #     wavelength
    #   - The total number of
    #     wavelength values is 64336:
    #     4021 wavelengths x 16 echelle
    #     orders, where echelle orders
    #     are placed side by side
    #   - Contact the author (Malena Rice)
    #     if your wavelength range is smaller
    #     than that used in this model
    #
    # ---------------------

    # Read in trained model
    model = tc.CannonModel.read("spocstrained_post2004.model")

    # Label names provided in the order that will be outputted by this code
    label_names = ["TEFF", "LOGG", "VSINI", "FeH", "CH", "NH", "OH", "NaH",
         "MgH", "AlH", "SiH", "CaH", "TiH", "VH", "CrH", "MnH", "NiH", "YH"]

    # Return labels for input dataset
    labels, cov, metadata = model.test(normalized_flux, normalized_ivar)

    # Put results in a dataframe for easier readability
    df_results = pd.DataFrame(labels, columns=label_names, index=star_names)

    # Save results
    if save_file == True:
        df_results.to_csv(save_dir+'stellar_labels.csv')

    return df_results


initfiles_dir = '../post-2004/runs_allorders/finalruns_paper/final_combined_run/'

normalized_flux = np.loadtxt(initfiles_dir+'fluxes_contdiv_polynomial_all.txt')
normalized_ivar = np.loadtxt(initfiles_dir+'ivar_contdiv_polynomial_all.txt')
star_names = np.loadtxt('star_names.txt', delimiter='/t', dtype='str')
