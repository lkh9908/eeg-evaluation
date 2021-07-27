import numpy as np
import mne
from loader import Loader


"""
The Cleaner class
Divide the EEG raw data into epochs
Optional preprocessing of the data
"""
class Cleaner(object):
    def __init__(self, args):
        self.raw = args
        self.epochs = None
        
    def remove_amplification(self):
        """
        input self.raw
        read the ch_names, acquire amplification factor as in naming convention
        output deamplified data in self.raw
        """
        for i in self.raw.ch_names:
            index = 0
            for j in i:
                if j == '_':
                    break
                index = index + 1
            #does not contain amplification factor in the format of Ch#_amp, assume as 1
            if i[index+1:] == '':
                amp = 1
            else:
                amp = int(i[index+1:])
            print('Based on channel name naming format, channel ' + i + ' has been amplified by a factor of ' + str(amp) + '. Deamplifying the data...')
            self.raw = self.raw.apply_function(lambda x: x / amp, picks = [i] )
        
    def into_epochs(self):
        """
        input  self.raw,
        output data divided into epochs
        """
        #divide into epochs
        new_events = mne.make_fixed_length_events(self.raw, duration=2.)
        event_dict = {'divide':1}
        #reject data with extreme/flat amplitude
        reject_criteria = {'eeg' : 400e-6}       # 400 µV
        flat_criteria = {'eeg' : 1e-6}          # 1 µV

#         self.epochs = mne.Epochs(self.raw,new_events, reject=reject_criteria, flat=flat_criteria,
#                             reject_by_annotation=False, preload=True)
        self.epochs = mne.Epochs(self.raw,new_events, reject_by_annotation=False, preload=True)
#         self.epochs.plot()
        return self.epochs

    def filter_by_freq(self, low=0.5, high=40):
        """
        input  self.epochs,
        output filtered self.epochs
        """
        self.epochs.load_data()
        self.epochs.filter(l_freq=low, h_freq=high, picks = 'all')
        return self.epochs
        
    def eog_removal(self):
        """
        input  self.raw,
        output self.epochs with eog movement removed using mne's built in method
        """
        print('ch_names are: ' + str(self.raw.ch_names))
        ch_name = input("Enter a channel for eog detection. Best if the channel is near eyes, like Fp1 and Fp2. All channels will be named like 'CH_1': ")
        eog_projs, eog_events = mne.preprocessing.compute_proj_eog(self.raw, n_grad=0, n_mag=0, n_eeg=1, ch_name=ch_name, reject = None)
        projs = eog_projs
        self.epochs.add_proj(projs)
        self.epochs.apply_proj()
        return self.epochs
        
    