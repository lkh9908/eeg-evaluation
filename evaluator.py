import pyedflib
import numpy as np
import xmltodict
import json
import mne
import matplotlib
import math
import pathlib
from mne_extras import write_mne_edf

class Evaluator(filename, isRaw):
    def _init_(self, filename, isRaw): 
        self.filename = filename
        self.isRaw = isRaw
        
        matplotlib.use('Qt5Agg')
        
        input_path = './input_txt/mzk_20210629/'
        output_path_edf = './output_edf/'
        output_path_fif = './output_fif/'

        # specifiable input
        # num of channel, raw vs filter

        #setting up paths for inputs and outputs
        #specify a name in the format of 
        # '2021-07-09_153143_RawData'

        ch_one = file_name + '_Ch1.txt'
        ch_two = file_name + '_Ch2.txt'

        ch_three = file_name + '_Ch3.txt'
        ch_four = file_name + '_Ch4.txt'

        xml = '2021-07-09_153143.xml'

        out_file_name = '2021-07-09_153143_pdk'
        out_name_edf = out_file_name + '.edf'
        out_name_fif = out_file_name + '.fif'
        out_name_final = 'final_' + out_file_name + '.edf'

        ch_one_path = input_path + ch_one
        ch_two_path = input_path + ch_two
        ch_three_path = input_path + ch_three
        ch_four_path = input_path + ch_four
        xml_path = input_path + xml
        out_file_path_edf = output_path_edf + out_name_edf
        out_file_path_fif = output_path_fif + out_name_fif
        out_final_edf = output_path_edf + out_name_final
    

def preprocess:
    #only used when input is raw data
    raw.filter(l_freq=0.5, h_freq=30)