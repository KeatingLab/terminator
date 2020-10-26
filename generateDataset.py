import numpy as np
import os
import json
import pickle
import argparse
import glob
import multiprocessing as mp
import time

from utils.packageTensors import dumpTrainingTensors

def generateDataset(in_folder, out_folder, cutoff = 50, update = False):
    # make folder where the dataset files are gonna be placed
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    # generate absolute paths so i dont have to think about relative references
    in_folder = os.path.abspath(in_folder)
    out_folder = os.path.abspath(out_folder)

    dataset = []
    os.chdir(in_folder)

    # process folder by folder
    for folder in glob.glob("*"):
        # folders that aren't directories aren't folders!
        if not os.path.isdir(folder):
            continue

        # for every file in the folder
        for file in glob.glob(folder + '/*.dat'):
            name = os.path.splitext(file)[0]
            full_folder_path = os.path.join(out_folder, folder)
            if not os.path.exists(full_folder_path):
                os.mkdir(full_folder_path)

            name = os.path.splitext(file)[0]
            if not update:
                out_file = os.path.join(out_folder, name)
                if os.path.exists(out_file + '.features'):
                    continue
            # i dunno why but if this doesn't exist the worker just dies without saying anything ig
            if not os.path.exists(name + '.red.pdb'):
                print(name + '.red.pdb doesnt exist? skipping')
                continue

            out_file = os.path.join(out_folder, name)
            print('out file', out_file)
            try:
                dumpTrainingTensors(name, out_path = out_file, cutoff = cutoff)
            except Exception as e:
                print(e)
            #output = dumpTrainingTensors(name, out_path = out_file, cutoff = cutoff)
            #dataset.append(output)

    return dataset


# when subprocesses fail you usually don't get an error...
def generateDatasetParallel(in_folder, out_folder, cutoff = 1000, num_cores = 1, update = True):
    print('num cores', num_cores)
    print('warning! it seems that if subprocesses fail right now you don\'t get an error message. be wary of this if the number of files you\'re getting seems off')
    # make folder where the dataset files are gonna be placed
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    # generate absolute paths so i dont have to think about relative references
    in_folder = os.path.abspath(in_folder)
    out_folder = os.path.abspath(out_folder)

    os.chdir(in_folder)

    pool = mp.Pool(num_cores, maxtasksperchild = 10)
    # process folder by folder
    for folder in glob.glob("*"):
        # folders that aren't directories aren't folders!
        if not os.path.isdir(folder):
            continue

        full_folder_path = os.path.join(out_folder, folder)
        if not os.path.exists(full_folder_path):
            os.mkdir(full_folder_path)
            
        for idx, file in enumerate(glob.glob(folder+'/*.dat')):
            name = os.path.splitext(file)[0]
            if not update:
                out_file = os.path.join(out_folder, name)
                if os.path.exists(out_file + '.features'):
                    continue
            # i dunno why but if this doesn't exist the worker just dies without saying anything ig
            if not os.path.exists(name + '.red.pdb'):
                print(name + '.red.pdb doesnt exist? skipping')
                continue
            res = pool.apply_async(dataGen, args=(file, folder, out_folder, cutoff), error_callback = raise_error)

    pool.close()
    pool.join()

def raise_error(error):
    raise error

# inner loop we wanna parallize
def dataGen(file, folder, out_folder, cutoff):
    name = os.path.splitext(file)[0]
    out_file = os.path.join(out_folder, name)
    print('out file', out_file)
    #print('red.pdb exists:', os.path.exists(name + '.red.pdb'))
    dumpTrainingTensors(name, out_path = out_file, cutoff = cutoff)





if __name__ == '__main__':
    parser = argparse.ArgumentParser('Generate features data files from dTERMen .dat files')
    parser.add_argument('in_folder', help = 'input folder containing .dat files in proper directory structure', default='dTERMen_data')
    parser.add_argument('out_folder', help = 'folder where features will be placed', default='features')
    parser.add_argument('--cutoff', dest='cutoff', help = 'max number of MSA entries per TERM', default = 50, type=int)
    parser.add_argument('-n', dest='num_cores', help = 'number of cores to use', default = 1, type = int)
    parser.add_argument('-u', dest='update', help = 'if added, update existing files. else, files that already exist will not be overwritten', default=False, action='store_true')
    args = parser.parse_args()
    if args.num_cores > 1:
        generateDatasetParallel(args.in_folder, args.out_folder, cutoff = args.cutoff, num_cores = args.num_cores, update = args.update)
    else:
        generateDataset(args.in_folder, args.out_folder, cutoff = args.cutoff, update = args.update)
