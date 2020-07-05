import numpy as np
import pandas as pd
import thecannon as tc
import time
from scipy.interpolate import interp1d
import scipy.signal
from run_trainedmodel_keck_post2004 import *


def interpolate_wavelengths(flux_interp_from, cont_interp_from, wv_interp_from, wv_interp_to):

    # ---------------------
    #
    # INPUTS:
    # flux_interp_from:
    #   - Fluxes from the raw spectrum, provided
    #     for the wavelengths in wv_interp_from.
    #     Shape (num_orders, num_pixels)
    # cont_interp_from:
    #   - Continuum fit to the raw spectrum, provided
    #     for the wavelengths in wv_interp_from.
    #     Shape (num_orders, num_pixels)
    # wv_interp_from:
    #   - Wavelength grid of the raw spectrum.
    #     Shape (num_orders, num_pixels)
    # wv_interp_to:
    #   - Wavelength grid to interpolate to
    #     from the raw spectrum.
    #
    #
    # OUTPUTS:
    # flux_interp_norm:
    #   - Continuum-normalized fluxes
    #     provided at interpolated wavelengths
    # sigma_interp_norm:
    #   - Continuum-normalized uncertainties
    #     provided at interpolated wavelengths
    #
    # ---------------------

    interp_arrs_created = False
    for order in range(0, len(wv_interp_to)):
        interp_function_flux = interp1d(wv_interp_from[order], flux_interp_from[order], kind='cubic')
        interp_function_cont = interp1d(wv_interp_from[order], cont_interp_from[order], kind='cubic')

        flux_interp_1order = interp_function_flux(wv_interp_to[order])
        cont_interp_1order = interp_function_cont(wv_interp_to[order])

        if interp_arrs_created != True:
            flux_interp = flux_interp_1order
            cont_interp = cont_interp_1order
            interp_arrs_created = True
        else:
            flux_interp = np.vstack((flux_interp, flux_interp_1order))
            cont_interp = np.vstack((cont_interp, cont_interp_1order))

    # Internal parameters
    gain = 1.2 #electrons/ADU
    readn = 2.0 #electrons RMS
    xwid = 5.0 #pixels, extraction width

    # Calculate the uncertainty in ADU from counts and read noise
    sigma_interp = np.sqrt((gain*flux_interp) + (xwid*readn**2.))/gain

    # Divide out the continuum
    flux_interp_norm = flux_interp/cont_interp
    sigma_interp_norm = sigma_interp/cont_interp

    return flux_interp_norm, sigma_interp_norm


def continuum_renorm_poly(flux_flat, sigma_flat, wv_flat, percent_as_decimal=0.7,
                          num_orders=16, num_pixels=4021, savefolder=None):

    # ---------------------
    #
    # INPUTS:
    # flux_flat:
    #   - Continuum-normalized fluxes
    #     that have been pre-flattened,
    #     with dimensions
    #     (num_orders*num_pixels, num_stars)
    # sigma_flat:
    #   - Continuum-normalized uncertainties
    #     that have been pre-flattened,
    #     with dimensions
    #     (num_orders*num_pixels, num_stars)
    # wv_flat:
    #   - Wavelength grid; 1D array with length
    #     (num_orders*num_pixels)
    # percent_as_decimal:
    #   - fraction used to determine how stringent
    #     our conditions are for allowing a pixel
    #     to be considered part of the continuum.
    #     Default is 70%, which is used on the
    #     training spectra in spocstrained_post2004.model
    # num_orders:
    #   - Number of echelle orders; 16 for Keck
    # num_pixels:
    #   - Number of pixels in each echelle order
    # savefolder:
    #   - Folder to save renormalized fluxes and
    #     uncertainties (optional)
    #
    #
    # OUTPUTS:
    # fluxes_contdiv_all:
    #   - Continuum-renormalized fluxes
    # sig_contdiv_all:
    #   - Continuum-renormalized uncertainties
    # ** If savefolder != None:
    #    -> Saved .txt files providing continuum-
    #       renormalized fluxes and uncertainties
    #
    # ---------------------

    # Read in the model-- note, we must read in the model with *no* telluric mask here
    model = tc.CannonModel.read("spocstrained_post2004_notelluricmask.model")

    full_renorm_arr_defined = False
    for order in range(0, num_orders):

        # Find indices corresponding to the order of interest
        order_start = num_pixels * order
        order_end = num_pixels * (order+1)
        model_order = model.theta[order_start:order_end]

        # Include in the continuum only pixels within 1.5% of unity
        flux_cut = (model_order[:,0] < 1.015) & (model_order[:,0] > 0.985)
        model_flux_cut = model.theta[order_start:order_end,0][flux_cut]
        where_flux_cut = np.where(flux_cut==True)[0]

        # Check total number of spectra
        order_arrs_defined = False
        if flux_flat.ndim == 1:
            num_spectra = 1
        elif flux_flat.dim == 2:
            num_spectra = len(flux_flat)
        else:
            print('WARNING: dimensionality of input fluxes not recognized')

        # Loop through stars to continuum-divide all spectra
        for starcount in range(0, num_spectra):

            # Extract the flux, uncertainty, and wavelength of each star
            # in the given echelle order
            if flux_flat.ndim == 1:
                fluxes = flux_flat[order_start:order_end]
                sigmas = sigma_flat[order_start:order_end]

            elif flux_flat.ndim == 2:
                fluxes = flux_flat[starcount][order_start:order_end]
                sigmas = sigma_flat[starcount][order_start:order_end]

            waves = wv_flat[order_start:order_end]

            # Select just pixels with coefficients deviating furthest from zero
            num_pix_select = int(percent_as_decimal * len(fluxes))

            coeffs1 = model_order[:,1]
            coeffs2 = model_order[:,2]
            coeffs3 = model_order[:,3]
            coeffs4 = model_order[:,16]

            coeffs1_select_inds = np.argsort(abs(coeffs1))[:num_pix_select]
            coeffs2_select_inds = np.argsort(abs(coeffs2))[:num_pix_select]
            coeffs3_select_inds = np.argsort(abs(coeffs3))[:num_pix_select]
            coeffs4_select_inds = np.argsort(abs(coeffs4))[:num_pix_select]

            is12 = np.intersect1d(coeffs1_select_inds, coeffs2_select_inds)
            is34 = np.intersect1d(coeffs3_select_inds, coeffs4_select_inds)
            is1234 = np.intersect1d(is12, is34)

            # Determine continuum pixels
            continuum_pixels = np.intersect1d(is1234, where_flux_cut)

            # Start by setting reduced chisq to a very high value; loop through
            # polynomial fits to find the best one.
            redchisq_best = 1.e30
            for num_fit_params in range(1, 10):

                z = np.poly1d(np.polyfit(waves[continuum_pixels], fluxes[continuum_pixels], \
                                         num_fit_params))

                continuum_temp = z(waves)

                chisq = np.sum(((fluxes[continuum_pixels] - \
                    continuum_temp[continuum_pixels])**2.)/ \
                    (sigmas[continuum_pixels]**2.))

                redchisq = chisq/(len(continuum_pixels) - num_fit_params)

                if redchisq < redchisq_best:
                    redchisq_best = redchisq
                    continuum_fit = continuum_temp
                    order_select = num_fit_params
                else:
                    pass

            # Set pixels outside of the fit equal to 1
            continuum_fit[:min(continuum_pixels)] = 1.
            continuum_fit[max(continuum_pixels):] = 1.


            if order_arrs_defined == False:
                fluxes_contdiv = fluxes/continuum_fit
                sig_contdiv = sigmas/continuum_fit
                order_arrs_defined = True

            elif order_arrs_defined != False:
                fluxes_contdiv = np.vstack((fluxes_contdiv, fluxes/continuum_fit))
                sig_contdiv = np.vstack((sig_contdiv, sigmas/continuum_fit))


        if full_renorm_arr_defined == False:
            fluxes_contdiv_all = fluxes_contdiv
            sig_contdiv_all = sig_contdiv
            full_renorm_arr_defined = True

        elif full_renorm_arr_defined != False:
            fluxes_contdiv_all = np.hstack((fluxes_contdiv_all, fluxes_contdiv))
            sig_contdiv_all = np.hstack((sig_contdiv_all, sig_contdiv))


    # Optionally, save all newly continuum renormalized spectra
    if savefolder != None:
        np.savetxt(savefolder + 'fluxes_contdiv_all.txt', fluxes_contdiv_all)
        np.savetxt(savefolder + 'sigma_contdiv_all.txt', sig_contdiv_all)

    return fluxes_contdiv_all, sig_contdiv_all
