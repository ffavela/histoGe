# own functions and classes
from myLibs.gammaSpectrumClass import *
# get input parameters
import argparse
# plotting and printing
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


# lets do something: ...
if __name__ == "__main__":
    """ fetch input parameters """
    parser = argparse.ArgumentParser(description='This is for testing the function writting the gamma spectrum')
    parser.add_argument('inputFile', metavar='f', type=str, nargs='?', help='Input file')
    parser.add_argument('-d', help='Detector flag (currently only \"boulby\" is defined', type=str, default="")
    args = parser.parse_args()

    # get spectrum from file
    spectrum = gamma_spectrum(args.inputFile, args.d)
    spectrum.read_spectrum_from_raw_file()


    """ do something with the data in the spectrum class. """
    # ... I.e. print the energy of the last bin:
    binEnergies = spectrum.get_bin_energies()
    binContents = spectrum.get_bin_contents()
    print(binEnergies[-1])

    # ... or: a plot
    matplotlib.rc('text', usetex = True)
    params = {'text.latex.preamble': [r'\usepackage{siunitx}', r'\usepackage{cmbright}']}
    plt.rcParams.update(params)
    plt.rc('xtick',labelsize=20)
    plt.rc('ytick',labelsize=20)
    fig, ax = plt.subplots(figsize=(7.0, 5.4))
    ax.plot(binEnergies, binContents, "bo", alpha = 1.0, markersize= 5)
    matplotlib.rcParams.update({'font.size': 24})

    ax.set_ylabel("Counts", horizontalalignment='right', y=1.0, fontsize = 24)
    #ax.set_xlabel('Bin Nb', horizontalalignment='right', x=1.0, fontsize = 24)
    ax.set_xlabel('Energy [\si{\kilo\electronvolt}]', horizontalalignment='right', x=1.0, fontsize = 24)

    plt.tight_layout()
    #plt.show()

    print("."+args.inputFile.split(".")[-2]+".pdf")

    outputPdf = PdfPages("."+args.inputFile.split(".")[-2]+".pdf")
    outputPdf.savefig(fig)
    outputPdf.close()


    """ write the class back to a file """
    spectrum.write_to_npz()