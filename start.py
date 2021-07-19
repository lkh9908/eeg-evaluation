import argparse
from tqdm import tqdm
import os, sys
from evaluator import Evaluator

def main(args):
    files = os.listdir(args.input_path)
    save_folder = args.save_folder
    os.makedirs(save_folder, exist_ok=True)
    
    if args.input_name == None:        
        print('please input a file name with --input_name')
        exit()
            
    input_list = []
    for i in files:
        #todo
        if args.input_name in i:
            input_list.append(i)
    
    ch_num = len(input_list)
        
    # load data 
    evaluator = Evaluator(args, input_list)
    evaluator.file_setup()
    evaluator.into_epochs()
    if args.filter:
        evaluator.filter_by_freq(low=0.5, high=30)

    if args.eog:
        ch_name = input("Enter a channel for eog detection. Best if the channel is near eyes, like Fp1 and Fp2. If your input is txt file, all channels will be named like 'ch1': ")
        evaluator.eog_removal(ch_name)
    
    save_fif = str.lower(input("Do you want to save the processed data as a .fif? (y/n) "))
    
    if save_fif == 'yes' or save_fif == 'ye' or save_fif == 'y':
        evaluator.save_epochs_fif()
        
    save_edf = str.lower(input("Do you want to save the processed data as a .edf? (y/n) "))
    
    if save_edf == 'yes' or save_edf == 'ye' or save_edf == 'y':
        evaluator.save_epochs_edf()
    evaluator.evaluate()
    scores = evaluator.get_score()
    print('scores of each epoch: ')
    print(scores[0])
    print('avg score: ')
    print(scores[1])

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pikachu's EEG Evaluator")

    parser.add_argument('-i', '--input_path', default='input_txt/', type=str,
                        help='Path to the test data, can be image folder, image path, image list, video')
    parser.add_argument('-n', '--input_name', default=None, type=str,
                        help='Enter file name. Please remove the _Ch part')
    # process test images
    parser.add_argument('-r', '--reference', default='normal', type=str,
                        help='Define reference point. Options are normal, ear, and forehead')
    parser.add_argument('-f', '--input_format', default='txt', type=str,
                        help='Define input file format. Options are txt and edf')
    parser.add_argument('--filter', default=True, type=lambda x: x.lower() in ['true', '1'],
                        help='Whether to filter the data' )
    parser.add_argument('--eog', default=True, type=lambda x: x.lower() in ['true', '1'],
                        help='Whether to remove eog patterns' )
    main(parser.parse_args())