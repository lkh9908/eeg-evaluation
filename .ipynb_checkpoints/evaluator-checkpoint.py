import numpy as np
import mne

"""
Evaluate quality of EEG data with a modified algorithm 
(Based on the one created in the paper:
"Signal Quality Assessment Model for Wearable 
EEG Sensor on Prediction of Mental Stress")

y1 = score based on variance of data
y2 = score based on percentage of 50Hz
y3 = score based on percentage of delta, theta, and alpha wave

final score = y1*y2*y3
"""
class Evaluator(object):
    def __init__(self, epochs):
        self.epochs = epochs
        
        self.score = []
        self.avg_score = 0
        self.overall_score = 0
    
    def evaluate(self):
        """
        input  self.epochs,
        output 
        score of each epoch as an array
        mean score of all epochs
        score of the epochs as a whole
        """
        print('Evaluation Started')
        
        #find grading criteria of each epoch 
        for i in range(len(self.epochs)):
            #variance
            df = self.epochs[i].to_data_frame()
            var = np.var(df)[2:]
            var_avg = sum(var) / len(var)    
            [power_ratio, sum_DTA] = self.find_proportions(self.epochs[i])
            #calculate score
            new_args =  [var_avg, power_ratio, sum_DTA]
            this_score = self.calc_score(new_args)
            self.score.append(this_score)
        self.avg_score = np.mean(self.score)
        
        df_all = self.epochs.to_data_frame()
        var_all = np.var(df_all)[2:]
        var_avg_all = sum(var_all) / len(var_all)
        [power_ratio_all, sum_DTA_all] = self.find_proportions(self.epochs)
        #calculate score
        new_args_all =  [var_avg_all, power_ratio_all, sum_DTA_all]
        score_all = self.calc_score(new_args_all)
        self.overall_score = score_all

        
    def find_proportions(self, epoch):
        """
        input  epoch,
        output 
        an array containing proportion of 50 Hz
        and the sum of delta, theta, and alpha waves
        """
        psds_total, frqs_total = mne.time_frequency.psd_multitaper(self.epochs, fmin=0.5, fmax=44.5, tmin=None, tmax=None)
        total_sum_pds = np.sum(psds_total)

        #power 50Hz
        psds_power, frqs_power = mne.time_frequency.psd_multitaper(self.epochs, fmin=45, fmax=55, tmin=None, tmax=None)
        power_sum_pds = np.sum(psds_power)
        power_ratio = (power_sum_pds) / (total_sum_pds)

        #delta 2-4
        psds_delta, frqs_delta = mne.time_frequency.psd_multitaper(self.epochs, fmin=1.5, fmax=4.5, tmin=None, tmax=None)
        delta_sum_pds = np.sum(psds_delta)
        delta_ratio = (delta_sum_pds) / (total_sum_pds)

        #delta 5-7
        psds_theta, frqs_theta = mne.time_frequency.psd_multitaper(self.epochs, fmin=4.5, fmax=7.5, tmin=None, tmax=None)
        theta_sum_pds = np.sum(psds_theta)
        theta_ratio = (theta_sum_pds) / (total_sum_pds)

        #alpha 8-12
        psds_alpha, frqs_alpha = mne.time_frequency.psd_multitaper(self.epochs, fmin=7.5, fmax=12.5, tmin=None, tmax=None)
        alpha_sum_pds = np.sum(psds_alpha)
        alpha_ratio = (alpha_sum_pds) / (total_sum_pds)

        sum_DTA = delta_ratio + theta_ratio + alpha_ratio
       
        return [power_ratio, sum_DTA]
    
    def calc_score(self, args):
        """
        input  args containing variables for score evaluation:
        variance, 50 Hz ratio, and sum of delta, theta, and alpha wave,
        output 
        an array contains proportion of 50 Hz
        and the sum of delta, theta, and alpha waves
        """
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
        #x3: delta, theta, and alpha wave / Total
        x3 = sum_DTA

        if x3 < 0.5:
            y3 = 2.8 * np.power(x3,2)
        else:
        #change 1.2 to -1.2
            y3 = -1.2 * np.power(x3,2) + 2.4*x3 - 0.2

        print('x1: ' + str(x1))
        print('x2: ' + str(x2))
        print('x3: ' + str(x3))

        print('y1: ' + str(y1))
        print('y2: ' + str(y2))
        print('y3: ' + str(y3))

        #print((y1*y2)*y3)
        return ((y1*y2)*y3)
        
    def get_score(self):
        """
        input  self,
        output 
        an array containing 
        self.score, self.avg_score, and self.overall_score
        """
        return [self.score, self.avg_score, self.overall_score]

        
 
        
            