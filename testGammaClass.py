from myLibs.gammaSpectrumClass import *
import argparse


if __name__ == "__main__":
    # fetch input parameters
    parser = argparse.ArgumentParser(description='This is for testing the function writting the gamma spectrum')
    parser.add_argument('inputFile', metavar='f', type=str, nargs='?', help='Input file')
    parser.add_argument('-d', help='Detector flag (currently only \"boulby\" is defined', type=str, default="")
    args = parser.parse_args()

    spectrum = gamma_spectrum(args.inputFile, args.d)
    spectrum.read_spectrum_from_raw_file()

    binEnergies = spectrum.get_bin_energies()
    print(binEnergies[-1])

    spectrum.write_to_npz()