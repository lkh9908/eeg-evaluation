import pyedflib
import numpy as np
import xmltodict
import json
import mne
import matplotlib
import math
import pathlib

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
        self.output_edf_original = args.output_path + args.input_name + '_original.edf'
        self.output_edf = args.output_path + args.input_name + '.edf'
        self.output_fif = args.output_path + args.input_name + '-epo.fif'
        
        #define information needed to write an .edf file
        self.raw = None
        self.epochs = None
        self.ch_names = []
        self.ch_num = 0
        self.sample_rate = 0
        
        self.physical_max = []
        self.physical_min = []
        self.digital_max = []
        self.digital_min = []

        
    def file_setup(self):
        """
        input  args from user input and file lists
        output a mne.raw file containing the data
        """
        #output a .edf file if the input is txt
        if self.args.input_format == 'txt':
            signal = []
            headers = []
            
            #read sample frequency from a .xml file
            if self.args.is_test:
                self.sample_rate = 1024
            else:
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
                    self.physical_max.append(np.max(raw))
                    self.physical_min.append(np.min(raw))
                
                
                    signal.append(raw)
                    new_header = header.copy()
                    new_header['label'] = 'ch' + str(j)
                    new_header['physical_max'] = np.max(raw)
                    new_header['physical_min'] = np.min(raw)

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
            self.raw=mne.io.read_raw_edf(self.output_edf_original,preload=True)
            print(self.raw.get_data())
            print(self.raw.to_data_frame())
            self.ch_names = self.raw.ch_names
            
        #if already a .edf
        elif self.args.input_format == 'bdf':
            self.raw = mne.io.read_raw_bdf(self.args.input_path + self.files[0], preload = True)
            self.ch_num = len(self.raw.ch_names)
            self.ch_names = self.raw.ch_names
            self.sample_rate = self.raw.info['sfreq']
            
            print(self.raw.info)
        elif self.args.input_format == 'edf':
            self.raw = mne.io.read_raw_edf(self.args.input_path + self.files[0], preload = True)
            self.ch_num = len(self.raw.ch_names)
            self.ch_names = self.raw.ch_names
            self.sample_rate = self.raw.info['sfreq']
        elif self.args.input_format =='mne':
            mne_exp = mne.datasets.eegbci.load_data(1, 2, path=None, force_update=False, update_path=None, base_url='https://physionet.org/files/eegmmidb/1.0.0/', verbose=None)[0]
            self.raw = mne.io.read_raw_edf(mne_exp, preload = True)
            self.ch_num = len(self.raw.ch_names)
            self.ch_names = self.raw.ch_names
            self.sample_rate = self.raw.info['sfreq']
            
            
        return self.raw
        
    def save_fif(self, data):
        data.save(self.output_fif, overwrite=True)
        
    def save_edf(self, data):
        df = data.to_data_frame()
        print(df)
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
        for i in self.ch_names:
            out_raw_ch = np.array(df[i])
            out_raw.append(out_raw_ch)
            new_header = header.copy()
            new_header['physical_max'] = np.max(out_raw_ch)
            new_header['physical_min'] = np.min(out_raw_ch)
            new_header['digital_max'] = np.max(out_raw_ch)
            new_header['digital_min'] = np.min(out_raw_ch)
            
            headers.append(new_header)
            
        with open(self.output_edf, 'w') as output:
            flag = pyedflib.highlevel.write_edf(output.name, out_raw, headers, header=None, digital=False, file_type=-1, block_size=1)
            if flag == False:
                print('unable to save file into .edf')
                exit()
            else:
                print('txt data loaded into edf, edf saved at ./output_edf as: ' + self.output_edf)
        
            