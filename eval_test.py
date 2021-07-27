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
        print('important number to be noticed `(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′')
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
        self.assertEqual(self.test_raw.info['nchan'],1)
        self.assertEqual(self.test_raw.info['ch_names'],['CH_0'])
        print('important number to be noticed `(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′')
        print('info of raw')
        print(self.test_raw.info)
        var_raw = []
        test_var = []
        var_data = self.test_raw.get_data(units = 'uV')
        for i in var_data:
            var_raw.append(np.var(i))
        for i in self.test_files:
            raw = np.loadtxt('tests/t_input/' + i)
            test_var.append(np.var(raw))
        print('important number to be noticed `(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′')
        print('variance of original txt data and saved edf data')
        print(var_raw, test_var)
        for i in range(len(var_raw)):
            self.assertGreater(var_raw[i] + 100, test_var[i])
            self.assertGreater(test_var[i] + 100, var_raw[i])
        
    def test_save_edf(self):
        'testing save edf'
        self.test_loader.save_edf(self.test_raw)
        new_raw = mne.io.read_raw_edf('tests/t_output/test1.edf', preload = True)
        print('important number to be noticed `(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′')
        print('data of saved edf and original')
        print(new_raw.get_data(), self.test_raw.get_data())
        self.assertEqual(new_raw.get_data().all(),self.test_raw.get_data().all())
        
    def test_filter_by_freq(self):
        test_epochs_copy = self.test_epochs.copy()
        psds_total, frqs_total = mne.time_frequency.psd_multitaper(test_epochs_copy, fmin=0, fmax=45, tmin=None, tmax=None)
        total_sum_pds = np.sum(psds_total)
        
        psds_low, frqs_low = mne.time_frequency.psd_multitaper(test_epochs_copy, fmin=0, fmax=1, tmin=None, tmax=None)
        low_sum_pds = np.sum(psds_low)
        
        psds_high, frqs_high = mne.time_frequency.psd_multitaper(test_epochs_copy, fmin=39, fmax=50, tmin=None, tmax=None)
        high_sum_pds = np.sum(psds_high)
        pre_ratio = (low_sum_pds + high_sum_pds) / (total_sum_pds)
        
        epochs_filtered = self.test_cleaner.filter_by_freq()
        
        psds_total_after, frqs_total_after = mne.time_frequency.psd_multitaper(epochs_filtered, fmin=0, fmax=45, tmin=None, tmax=None)
        total_sum_pds_after = np.sum(psds_total_after)
        
        psds_low_after, frqs_low_after = mne.time_frequency.psd_multitaper(epochs_filtered, fmin=0, fmax=1, tmin=None, tmax=None)
        low_sum_pds_after = np.sum(psds_low_after)
        
        psds_high_after, frqs_high_after = mne.time_frequency.psd_multitaper(epochs_filtered, fmin=39, fmax=50, tmin=None, tmax=None)
        high_sum_pds_after = np.sum(psds_high_after)
        after_ratio = (low_sum_pds_after + high_sum_pds_after) / (total_sum_pds_after)
        
        print('important number to be noticed `(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′')
        print('proportion of 0-->1 and 39-->50 hz before and after the filter of (0.5hz to 40hz)')
        print(pre_ratio, after_ratio)
        self.assertGreater(pre_ratio, after_ratio)
        
    def test_find_proportions(self):
        result = self.test_evaluator.find_proportions(self.test_epochs)
        
        #the test data, based on what is shown on edf browser
        #should have 19.9% delta, 20.3% theta, 39.0% alpha, and 19.7% 50Hz.
        #thus sum(alpha, delta, theta) : 50Hz --> 80 : 20 --> 4
        #to allow for a margin, this test passes as along as:
        #the factor is above 3 and below 5
        print('important number to be noticed `(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′`(*>﹏<*)′')
        print('sum(alpha, delta, theta) and 50 Hz: ')
        print(result[1], result[0])
        print('factor')
        factor = result[1] / result[0]
        print(factor)
        self.assertGreater(factor, 3)
        self.assertGreater(5, factor)
        
    def test_scores(self):
        #test x1
        score1 = self.test_evaluator.calc_score([1,1,1])
        print('test score 1: ' + str(score1))
        self.assertEqual(round(score1,3), 0.016)
        score2 = self.test_evaluator.calc_score([100,0.5,0.4])
        print('test score 1: ' + str(score2))
        self.assertEqual(round(score2,3), 35.780)

    
        
if __name__  == '__main__':
    unittest.main()