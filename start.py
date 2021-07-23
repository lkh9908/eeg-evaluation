import argparse
from tqdm import tqdm
import os, sys
from loader import Loader
from preprocessor import Cleaner
from evaluator import Evaluator

"""
The starter file of EEG evaluator
Author: Kaihao Liu

Functionalities:
1. Load EEG data formatted in .edf or .txt files
2. Preprocess the data using functions provided by mne
3. Evaluate quality of EEG data with a modified algorithm 
(Based on the one created in the paper:
"Signal Quality Assessment Model for Wearable 
EEG Sensor on Prediction of Mental Stress")
"""
def main(args):
    files = os.listdir(args.input_path)
    if args.input_name == None:        
        print('please input a file name with --input_name')
        exit() 
            
    input_list = []
    for i in files:
        #todo
        if args.input_name in i:
            input_list.append(i)
#     print(input_list)
    ch_num = len(input_list)
        
    loader = Loader(args, input_list)
    raw = loader.file_setup()
        
    cleaner = Cleaner(raw)
    
    cleaner.remove_amplification()

    epochs = cleaner.into_epochs()
    
    if args.filter:
        epochs = cleaner.filter_by_freq(low=0.5, high=30)

    if args.eog:
        ch_name = input("Enter a channel for eog detection. Best if the channel is near eyes, like Fp1 and Fp2. If your input is txt file, all channels will be named like 'ch1': ")
        epochs = cleaner.eog_removal(ch_name)
    
    save_fif = str.lower(input("Do you want to save the processed data as a .fif? (y/n) "))
    
    if save_fif == 'yes' or save_fif == 'ye' or save_fif == 'y':
        loader.save_fif(epochs)
        
    save_edf = str.lower(input("Do you want to save the processed data as a .edf? (y/n) "))
    
    if save_edf == 'yes' or save_edf == 'ye' or save_edf == 'y':
        loader.save_edf(epochs)
        
    evaluator = Evaluator(epochs)
    evaluator.evaluate()
    scores = evaluator.get_score()
    print('scores of each epoch: ')
    print(scores[0])
    print('avg score: ')
    print(scores[1])
    print('score of epochs as a whole: ')
    print(scores[2])

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pikachu's EEG Evaluator")

    parser.add_argument('-i', '--input_path', default='input/', type=str,
                        help='Path to input data, must be a directory or folder')
    parser.add_argument('-o', '--output_path', default='output/', type=str,
                        help='Path to output data, must be a directory or folder')
    parser.add_argument('-n', '--input_name', default=None, type=str,
                        help='Enter file name. Please remove the _Ch part')
    parser.add_argument('-t', '--is_test', default=False, type=lambda x: x.lower() in ['true', '1'],
                        help='Whether the input is a test example, which means no .xml file and default to 1024 sample frequency' )
    # process test images
#     parser.add_argument('-r', '--reference', default='normal', type=str,
#                         help='Define reference point. Options are normal, ear, and forehead')
    parser.add_argument('-f', '--input_format', default='txt', type=str,
                        help='Define input file format. Options are txt, edf, and bdf')
    parser.add_argument('--filter', default=True, type=lambda x: x.lower() in ['true', '1'],
                        help='Whether to filter the data' )
    parser.add_argument('--eog', default=True, type=lambda x: x.lower() in ['true', '1'],
                        help='Whether to remove eog patterns' )
    main(parser.parse_args())