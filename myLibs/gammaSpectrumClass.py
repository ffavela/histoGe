import numpy as np
import argparse


class gamma_spectrum:

    # initialise the class 
    def __init__(self, file_name, detector_flag):
        self.fileName = file_name
        self.detectorTypFlag = detector_flag

        # counts for each bin
        self.countsInBins = list()
        self.firstBinValue = -1.0
        self.binWidth = -1.0

        """ The energy value for for each bin i, E_i, is calculated using a formula:
                E_i = a_0*(x_i-b_0)^c_0 + a_1*(x_i-b_1)^c_1 ... 
            where x_i is the ith raw bin value. The lists of as, bs and cs need to have the same size """
        self.energyCalibration_aValues = list()
        self.energyCalibration_bValues = list()
        self.energyCalibration_cValues = list()

        # data taking time
        self.lifeTime = -1.0

        # flag to indicate whether the class has already been set-up
        self.classSetup = False

        # check if the input file is already a spectrum file
        if self.fileName.endswith(".npz"):
            self.__read_spectrum_from_spectrum_file()

    # set up a gamma_spectrum form a npz file
    def __read_spectrum_from_spectrum_file(self):
        spectrum = np.load(self.fileName)

        self.detectorTypFlag = spectrum['detector_flag']
        self.countsInBins = spectrum['counts_in_bins']
        self.firstBinValue = spectrum['first_bin_value']
        self.binWidth = spectrum['bin_width']
        self.energyCalibration_aValues = spectrum['energy_calibration_multipliers']
        self.energyCalibration_bValues = spectrum['energy_calibration_offsets']
        self.energyCalibration_cValues = spectrum['energy_calibration_exponents']
        self.lifeTime = spectrum['life_time']

        self.classSetup = True
    
    # read the spectrum
    def read_spectrum_from_raw_file(self):
        # check if the gamma spectrum has been set-up previously
        # if not: set it up ...
        if not self.classSetup:
            # flag for a boulby detector - SPE
            if self.detectorTypFlag == "boulby":
                # open the file
                if not self.fileName.endswith(".SPE"): 
                    print("Detector type flag: %s and expected file name %s do not match" %(self.detectorTypFlag, self.fileName))
                    print("Attempt to read file anyway")
                
                with open(self.fileName) as f:
                    # read in the lines
                    fileContent = f.readlines()
            
                    # conversion factor(s)
                    energyPerBin = float(fileContent[-3].split()[1])
                    self.energyCalibration_aValues.append(energyPerBin)
                    self.energyCalibration_bValues.append(0.0)
                    self.energyCalibration_cValues.append(1.0)
                        
                    # measurement time
                    self.lifeTime = float(fileContent[3].split()[1])

                    # fill data related to the channel numbers
                    self.firstBinValue = int(fileContent[7].split()[0])
                    self.binWidth = 1.0
                    # find out how many bins we have
                    lastBin = int(fileContent[7].split()[1])
                    # get the content of each bin from the file
                    for lineID in range(8, 8 + lastBin):
                        self.countsInBins.append(float(fileContent[lineID].rstrip()))

                    self.classSetup = True
                
            # everything else: falg not defined
            else: print("Flag %s not defined" %self.detectorTypFlag)
        # ... if yes: do nothing
        else: print("Spectrum already set-up from %s" %(self.fileName))

        
            

    # create a list of bins
    def get_bin_list(self):
        return np.arange(self.firstBinValue, len(self.countsInBins), self.binWidth)

    # convert bin values to energy values
    def get_bin_energies(self):
        energyBinValues = list()
        for binValue in self.get_bin_list():
            energyBinValue = 0
            for calibrationFactorId in range(len(self.energyCalibration_aValues)):
                energyBinValue = energyBinValue + self.energyCalibration_aValues[energyBinValue]*(binValue-self.energyCalibration_bValues)**self.energyCalibration_cValues
            energyBinValues.append(energyBinValue[0])
        return energyBinValues

    # write spectrum data to file
    def write_to_npz(self):
        outName = self.fileName.rstrip('.SPE')
        # write the class data to a file
        np.savez(outName, detector_flag=self.detectorTypFlag, counts_in_bins=self.countsInBins, first_bin_value=self.firstBinValue, bin_width=self.binWidth, energy_calibration_offsets=self.energyCalibration_bValues, energy_calibration_multipliers=self.energyCalibration_aValues, energy_calibration_exponents=self.energyCalibration_cValues, life_time=self.lifeTime)





