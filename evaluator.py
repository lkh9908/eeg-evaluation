import pyedflib
import numpy as np
import xmltodict
import json
import mne
import matplotlib
import math
import pathlib
from mne_extras import write_mne_edf

class Evaluator(object):
    def __init__(self, args, files):
        self.ref = args.reference
        self.format = args.input_format
        self.files = files
        edf = []
#         if self.format == 'txt':
#             edf = load_into_edf(self, self.format, self.files)
#         else:
#             edf = files
        
    def load_into_edf(self, format, files):
        ch_num = len(self.files)
        for i in self.files:
            raw = np.loadtxt(args.input_path + i)
            signal.append(raw)
            
        xml_file = open(args.input_path + args.input_name + '.xml', "r")
        xml_content = xml_file.read()
        my_ordered_dict = xmltodict.parse(xml_content)
        dict = json.loads(json.dumps(my_ordered_dict))
        sample_rate = eval(dict['RECORD_INFO']['Record']['SamplesFreq'])
        
        
