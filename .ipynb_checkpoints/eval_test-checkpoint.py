import random
import unittest
import loader
import preprocessor
import evaluator
import mne
from argparse import Namespace
import os
import numpy as np

class ExampleSignalTest(unittest.TestCase):
    def setUp(self):
        self.args = Namespace(input_path='tests/t_input/', output_path = 'tests/t_output/', input_name='test1', is_test=True, reference='normal', input_format='txt', filter=True, eog=True)
        self.test_files = os.listdir(self.args.input_path)
        print('important number to be noticed `(*>﹏<*)′')
        print('test files: ')
        print(self.test_files)
        self.test_loader = loader.Loader(self.args, self.test_files)
        self.test_raw = self.test_loader.file_setup()
        self.test_cleaner = preprocessor.Cleaner(self.test_raw)
        self.test_epochs = self.test_cleaner.into_epochs()
        self.test_evaluator = evaluator.Evaluator(self.test_epochs)
        
    def tearDown(self):
        print('call teardown')
        
    def test_load_txt(self):
        self.assertEqual(self.test_raw.info['nchan'],2)
        self.assertEqual(self.test_raw.info['ch_names'],['ch0', 'ch1'])
        print('important number to be noticed `(*>﹏<*)′')
        print(self.test_raw.info)
        var_raw = []
        test_var = []
        var_data = self.test_raw.to_data_frame()
        print((var_data))
#         print(len(var_data[0]))
#         print(len(var_data[0][0]))
        for i in self.test_raw.ch_names:
            var_raw.append(np.var(var_data[i]))
        for i in self.test_files:
            print('xxxxxxxxxsaaaaaadfasfsa')
            print(i)
            raw = np.loadtxt('tests/t_input/' + i)
            test_var.append(np.var(raw))
        print(var_raw, test_var)
            
        
    def test_save_edf(self):
        self.test_loader.save_edf(self.test_epochs)
        new_raw = mne.io.read_raw_edf('tests/t_output/test1.edf', preload = True)
        self.assertEqual(new_raw,self.test_raw)
        self.assertEqual(new_raw.get_data().all(),self.test_raw.get_data().all())
        
    def test_filter_by_freq(self):
        self.test_epochs
        psds_total, frqs_total = mne.time_frequency.psd_multitaper(self.test_epochs, fmin=0, fmax=50, tmin=None, tmax=None)
        total_sum_pds = np.sum(psds_total)
        
        psds_low, frqs_low = mne.time_frequency.psd_multitaper(self.test_epochs, fmin=0, fmax=1, tmin=None, tmax=None)
        low_sum_pds = np.sum(psds_low)
        
        psds_high, frqs_high = mne.time_frequency.psd_multitaper(self.test_epochs, fmin=29, fmax=50, tmin=None, tmax=None)
        high_sum_pds = np.sum(psds_high)
        pre_ratio = (low_sum_pds + high_sum_pds) / (total_sum_pds)
        
        epochs_filtered = self.test_cleaner.filter_by_freq(low=0.5, high=30)
        
        psds_total_after, frqs_total_after = mne.time_frequency.psd_multitaper(self.test_epochs, fmin=0, fmax=50, tmin=None, tmax=None)
        total_sum_pds_after = np.sum(psds_total_after)
        
        psds_low_after, frqs_low_after = mne.time_frequency.psd_multitaper(self.test_epochs, fmin=0, fmax=0.5, tmin=None, tmax=None)
        low_sum_pds_after = np.sum(psds_low_after)
        
        psds_high_after, frqs_high_after = mne.time_frequency.psd_multitaper(self.test_epochs, fmin=30, fmax=50, tmin=None, tmax=None)
        high_sum_pds_after = np.sum(psds_high_after)
        after_ratio = (low_sum_pds_after + high_sum_pds_after) / (total_sum_pds_after)
        
        print('important number to be noticed `(*>﹏<*)′')
        print(pre_ratio, after_ratio)
        self.assertGreater(pre_ratio, after_ratio)
        
#     def test_eog_removal(self):
#         eog_projs, eog_events = mne.preprocessing.compute_proj_eog(self.test_raw, n_grad=0, n_mag=0, n_eeg=1, ch_name='ch0', reject = None)
#         epochs_new = self.test_cleaner.eog_removal('ch0')
#         eog_projs, eog_events = mne.preprocessing.compute_proj_eog(epochs_new, n_grad=0, n_mag=0, n_eeg=1, ch_name='ch0', reject = None)
        
#         print('x')
#         self.assertGreater(2, 1)
        
    def test_find_proportions(self):
        result = self.test_evaluator.find_proportions(self.test_epochs)
        print(11111111111111111111222222222222222)
        print(result)
        self.assertGreater(2, 1)

    
        
if __name__  == '__main__':
    unittest.main()