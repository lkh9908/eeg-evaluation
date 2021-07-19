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
The Cleaner class
Divide the EEG raw data into epochs
Optional preprocessing of the data
"""
class Cleaner(object):
    def __init__(self, args):
        self.raw = args
        self.epochs = None
        
    def into_epochs(self):
        #divide into epochs
        new_events = mne.make_fixed_length_events(self.raw, duration=2.)
        event_dict = {'divide':1}
        
        #reject data with extreme/flat amplitude
        reject_criteria = {'eeg' : 400e-6}       # 400 µV
        flat_criteria = {'eeg' : 1e-6}          # 1 µV

        self.epochs = mne.Epochs(self.raw,new_events, reject=reject_criteria, flat=flat_criteria,
                            reject_by_annotation=False, preload=True)
        return self.epochs

    def filter_by_freq(self, low=0.5, high=30):
        self.epochs.load_data()
        self.epochs.filter(l_freq=low, h_freq=high)
        return self.epochs
        
    def eog_removal(self, ch_name):
        #removes eog movement using function provided by mne
        eog_projs, eog_events = mne.preprocessing.compute_proj_eog(self.raw, n_grad=0, n_mag=0, n_eeg=1, ch_name=ch_name, reject = None)
        projs = eog_projs
        self.epochs.add_proj(projs)
        self.epochs.apply_proj()
        return self.epochs
        
    