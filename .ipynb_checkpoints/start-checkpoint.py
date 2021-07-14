import argparse
from tqdm import tqdm
import os, sys
from evaluator import Evaluator

def main(args):
    files = os.listdir(args.input_path)
    save_folder = args.save_folder
    os.makedirs(save_folder, exist_ok=True)
    
    input_list = []
    for i in files:
        #todo
        if '2019-12-26_170147' in i:
            input_list.append(i)
    
    ch_num = len(input_list)
        
    # load data 
    evaluator = Evaluator(args, input_list)
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pikachu's EEG Evaluator")

    parser.add_argument('-i', '--input_path', default='input_txt/', type=str,
                        help='path to the test data, can be image folder, image path, image list, video')
    parser.add_argument('-s', '--save_folder', default='output_score/', type=str,
                        help='path to the output directory, where results(obj, txt files) will be stored.')
    parser.add_argument('-n', '--input_name', default=None, type=str,
                        help='Enter file name. Please remove the _Ch part')
    # process test images
    parser.add_argument('-r', '--reference', default='Normal', type=str,
                        help='Define reference point. Options are normal, ear, and forehead')
    parser.add_argument('-f', '--input_format', default='txt', type=str,
                        help='Define input file format. Options are txt and edf')
    main(parser.parse_args())