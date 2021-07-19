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
        self.args = args
        self.files = files
        self.output_edf_original = './output_edf/' + args.input_name + '_original.edf'
        self.output_edf = './output_edf/' + args.input_name + '.edf'
        self.output_fif = './output_fif/' + args.input_name + '-epo.fif'
        self.raw = None
        self.epochs = None
        
        self.ch_num = 0
        self.sample_rate = 0
        self.score = []
        self.avg_score = 0
        
    def file_setup(self):
        #output a .edf file if the input is txt
        if self.args.input_format == 'txt':
            signal = []
            headers = []
            
            xml_file = open(self.args.input_path + self.args.input_name + '.xml', "r")
            xml_content = xml_file.read()
            my_ordered_dict = xmltodict.parse(xml_content)
            dict = json.loads(json.dumps(my_ordered_dict))
            self.sample_rate = eval(dict['RECORD_INFO']['Record']['SamplesFreq'])
            
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
        
    def into_epochs(self):
        #divide into epochs
        new_events = mne.make_fixed_length_events(self.raw, duration=2.)
        event_dict = {'divide':1}
        reject_criteria = {'eeg' : 400e-6}       # 400 µV
        flat_criteria = {'eeg' : 1e-6}          # 1 µV

        self.epochs = mne.Epochs(self.raw,new_events, reject=reject_criteria, flat=flat_criteria,
                            reject_by_annotation=False, preload=True)

    def filter_by_freq(self, low=0.5, high=30):
        self.epochs.load_data()
        self.epochs.filter(l_freq=low, h_freq=high)
        
    def eog_removal(self, ch_name):
        print(self.raw.ch_names)
        eog_projs, eog_events = mne.preprocessing.compute_proj_eog(self.raw, n_grad=0, n_mag=0, n_eeg=1, ch_name=ch_name, reject = None)
        projs = eog_projs
        self.epochs.add_proj(projs)
        self.epochs.apply_proj()
        
    def save_epochs_fif(self):
        self.epochs.save(self.output_fif, overwrite=True)
        
    def save_epochs_edf(self):
        df = self.epochs.to_data_frame()
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
    
    def evaluate(self):
        print('Evaluation Started')
        
        for i in range(len(self.epochs)):
            df = self.epochs[i].to_data_frame()
            var = np.var(df)[2:]
            var_avg = sum(var) / len(var)

            psds_total, frqs_total = mne.time_frequency.psd_multitaper(self.epochs[i], fmin=0.5, fmax=44.5, tmin=None, tmax=None)
            total_sum_pds = np.sum(psds_total)

            #power 50Hz
            psds_power, frqs_power = mne.time_frequency.psd_multitaper(self.epochs[i], fmin=45, fmax=55, tmin=None, tmax=None)
            power_sum_pds = np.sum(psds_power)
            power_ratio = (power_sum_pds) / (total_sum_pds)

            #delta 2-4
            psds_delta, frqs_delta = mne.time_frequency.psd_multitaper(self.epochs[i], fmin=1.5, fmax=4.5, tmin=None, tmax=None)
            delta_sum_pds = np.sum(psds_delta)
            delta_ratio = (delta_sum_pds) / (total_sum_pds)

            #delta 5-7
            psds_theta, frqs_theta = mne.time_frequency.psd_multitaper(self.epochs[i], fmin=4.5, fmax=7.5, tmin=None, tmax=None)
            theta_sum_pds = np.sum(psds_theta)
            theta_ratio = (theta_sum_pds) / (total_sum_pds)

            #alpha 8-12
            psds_alpha, frqs_alpha = mne.time_frequency.psd_multitaper(self.epochs[i], fmin=7.5, fmax=12.5, tmin=None, tmax=None)
            alpha_sum_pds = np.sum(psds_alpha)
            alpha_ratio = (alpha_sum_pds) / (total_sum_pds)

            sum_DTA = delta_ratio + theta_ratio + alpha_ratio
            new_args =  [var_avg, power_ratio, sum_DTA]
            self.calc_score(new_args)
        self.avg_score = np.mean(self.score)
    
    def calc_score(self, args):
        var_avg = args[0]
        power_ratio = args[1]
        sum_DTA = args[2]
        #y1: variance score
        y1 = 0
        #x1: variance
        x1 = var_avg

        if x1 < 50:
            y1 = 0.02*np.power(x1,2)
        elif x1 >= 50 and x1 < 100:
            y1 = 0.6*x1 + 20
        #changed third condition from 2000 to 3000
        elif x1 >= 100 and x1 < 3000:
            y1 = 100
        elif x1 >= 3000 and x1 < 5000:
            y1 = -0.013333*x1 + 126.6
        elif x1 >= 5000 and x1 < 10000:
            y1 = 0.006*x1 + 90
        else:
            y1 = 15/0.02*np.power((x1-10000),2)

        #y2: power voltage score
        y2 = 0
        #x2: signal that are 50Hz (CN) / Total
        x2 = power_ratio


        if x2 < 0.01:
            y2 = 1
        elif x2 >= 0.01 and x2 < 0.1:
            y2 = 1 - 24.691*np.power((x2-0.01),2)
        elif x2 >= 0.1 and x2 < 5:
            y2 = 0.8 - 0.00833*np.power((x2-0.1),2)
        elif x2 >= 5 and x2 < 10:
            y2 = 0.9 - np.power(0.06,2)
        else:
            y2 = 30 / np.power(x2,2)


        #y3: eeg composition score
        y3 = 0
        #x3: alpha wave / Total
        x3 = sum_DTA

        if x3 < 0.5:
            y3 = 2.8 * np.power(x3,2)
        #             y3 = 4.375 * np.power(x3,2)
        else:
        #change 1.2 to -1.2
            y3 = -1.2 * np.power(x3,2) + 2.4*x3 - 0.2
        #             y3 = 0.376176*np.power(x3,2) + 0.623824

        print('x1: ' + str(x1))
        print('x2: ' + str(x2))
        print('x3: ' + str(x3))

        print('y1: ' + str(y1))
        print('y2: ' + str(y2))
        print('y3: ' + str(y3))

        #         print((y1*y2)*y3)
        self.score.append((y1*y2)*y3)
        
    def get_score(self):
        return [self.score, self.avg_score]

        
 
        
            