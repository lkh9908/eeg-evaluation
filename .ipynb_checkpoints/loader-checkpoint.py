import pyedflib
import numpy as np
import xmltodict
import json
import mne
import matplotlib
import math
import pathlib
from mne_extras import write_mne_edf

"""
The Loader class
Load data formatted in .txt or .edf file
Create .edf file if the input is in .txt file
Also contains functions that write a .edf or .fif file given epochs as input
"""
class Loader(object):
    def __init__(self, args, files):
        self.args = args
        self.files = files
        
        #define output path
        self.output_edf_original = './output_edf/' + args.input_name + '_original.edf'
        self.output_edf = './output_edf/' + args.input_name + '.edf'
        self.output_fif = './output_fif/' + args.input_name + '-epo.fif'
        
        #define information needed to write an .edf file
        self.raw = None
        self.epochs = None
        self.ch_num = 0
        self.sample_rate = 0

        
    def file_setup(self):
        #output a .edf file if the input is txt
        if self.args.input_format == 'txt':
            signal = []
            headers = []
            
            #read sample frequency from a .xml file
            xml_file = open(self.args.input_path + self.args.input_name + '.xml', "r")
            xml_content = xml_file.read()
            my_ordered_dict = xmltodict.parse(xml_content)
            dict = json.loads(json.dumps(my_ordered_dict))
            self.sample_rate = eval(dict['RECORD_INFO']['Record']['SamplesFreq'])
            
            #define header, needed for .edf file
            header = {'label':'ch_name', 
                    'dimension': 'uV',
                    'sample_rate': self.sample_rate,
                    'physical_max': 5000,
                    "physical_min": -5000,
                    'digital_max': 5000,
                    'digital_min': -5000,
                    'transducer': 'None',
                    'prefilter': 'None'}

            j = 0
            for i in self.files:
                if i[-3:] != 'xml' and i[-4:] != 'xysw':
                    raw = np.loadtxt(self.args.input_path + i)
                    signal.append(raw)
                    new_header = header.copy()
                    new_header['label'] = 'ch' + str(j)
                    j = j+1
                    headers.append(new_header)
                    self.ch_num = self.ch_num+1
            
            #write edf
            with open(self.output_edf_original, 'w') as output:
                flag = pyedflib.highlevel.write_edf(output.name, signal, headers, header=None, digital=False, file_type=-1, block_size=1)
            if flag == False:
                print('unable to save file into .edf')
                exit()
            else:
                print('txt data loaded into edf, edf saved at ./output_edf as: ' + self.output_edf_original)
            self.raw=mne.io.read_raw_edf(self.output_edf_original,preload=False)
            
        #if already a .edf
        elif self.args.input_format == 'edf' or self.args.input_format == 'bdf':
            self.raw = files
            ch_num = len(self.raw.ch_names)
            
        return self.raw
        
        
    def save_epochs_fif(self, epochs):
        epochs.save(self.output_fif, overwrite=True)
        
    def save_epochs_edf(self, epochs):
        df = epochs.to_data_frame()
        out_raw = []
        headers = []
        header = {'label':'ch_name', 
                    'dimension': 'uV',
                    'sample_rate': self.sample_rate,
                    'physical_max': 5000,
                    "physical_min": -5000,
                    'digital_max': 5000,
                    'digital_min': -5000,
                    'transducer': 'None',
                    'prefilter': 'None'}
        j = 0
        for i in range(self.ch_num):
            out_raw_ch = np.array(df['ch' + str(i)])
            out_raw.append(out_raw_ch)
            new_header = header.copy()
            new_header['label'] = 'ch' + str(j)
            j = j+1
            headers.append(new_header)
            
        with open(self.output_edf, 'w') as output:
            flag = pyedflib.highlevel.write_edf(output.name, out_raw, headers, header=None, digital=False, file_type=-1, block_size=1)
            if flag == False:
                print('unable to save file into .edf')
                exit()
            else:
                print('txt data loaded into edf, edf saved at ./output_edf as: ' + self.output_edf)
        
            