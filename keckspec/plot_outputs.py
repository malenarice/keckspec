import numpy as np
import matplotlib.pyplot as plt

def plot_model_comparison(wv, flux_data, metadata, num_orders=16, len_order=4021):

    # Onput flattened wavelength and flux array. Dimensions set to HIRES as default.

    for order in range(0, num_orders):

        # pull out model flux for this order
        model_flux = metadata[0]['model_flux'][order*len_order:(order+1)*len_order]
        wv_order = wv[order*len_order:(order+1)*len_order]
        flux_data_order = flux_data[order*len_order:(order+1)*len_order]

        if order == 0:
            plt.plot(wv_order, flux_data_order, color='blueviolet', label='HIRES template')
            plt.plot(wv_order, model_flux, color='darkcyan', label='model flux')

        else:
            plt.plot(wv_order, flux_data_order, color='blueviolet')
            plt.plot(wv_order, model_flux, color='darkcyan')

    plt.xlabel(r'wavelength ($\AA$)')
    plt.ylabel('normalized flux')
    plt.legend()
    plt.show()

    pass
