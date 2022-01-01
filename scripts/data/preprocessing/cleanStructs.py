import argparse
import glob
import json
import multiprocessing as mp
import os
import pickle
import sys
import time
import traceback

import numpy as np


def extractBackbone(filename, outpath, valid_elements=['N', 'CA', 'C', 'O']):
    """
    Given a PDB structure, extract the protein backbone atoms and dump it in a redesigned PDB file
    """
    struct_dict = {}
    valid_entry_lines = []
    with open(filename, 'r') as fp:
        entry_lines = [l for l in fp]

    for line_num, line in enumerate(entry_lines):
        data = line.strip()
        if data == 'TER' or data == 'END':
            valid_entry_lines.append(line_num)
            continue
        try:
            element = data[13:16].strip()
            residue = data[17:20].strip()
            residx = data[22:27].strip()
            chain = data[21]
            x = data[30:38].strip()
            y = data[38:46].strip()
            z = data[46:54].strip()
            coords = [float(coord) for coord in [x, y, z]]
        except Exception as e:
            print(data)
            raise e

        if (chain, residx) not in struct_dict.keys():
            struct_dict[(chain, residx)] = {
                "elements": np.array([False for _ in range(5)]),
                "line_numbers": []
            }

        if element in valid_elements:
            struct_dict[(chain, residx)]["elements"][valid_elements.index(element)] = True
            struct_dict[(chain, residx)]["line_numbers"].append(line_num)
        elif element == 'OXT':
            struct_dict[(chain, residx)]["elements"][-1] = True
            struct_dict[(chain, residx)]["oxt_num"] = line_num

    for struct_vals in struct_dict.values():
        elem_arr = struct_vals["elements"]
        if elem_arr[:4].all():
            # if we have N, CA, C, O, we take those lines
            # and ignore OXT even if present
            valid_entry_lines += struct_vals["line_numbers"]
        elif elem_arr[[0, 1, 2, 4]].all() and not elem_arr[3]:
            # if we have N, CA, C, OXT, but no O
            # we take OXT as O
            assert len(struct_vals["line_numbers"]) == 3, struct_vals["line_numbers"]
            valid_entry_lines += struct_vals["line_numbers"]
            valid_entry_lines.append(struct_vals["oxt_num"])

    valid_entry_lines.sort()

    with open(outpath, 'w') as fp:
        for idx in range(len(valid_entry_lines)):
            cur_line_num = valid_entry_lines[idx]
            prev_line_num = valid_entry_lines[idx - 1] if idx > 0 else valid_entry_lines[0]
            cur_line = entry_lines[cur_line_num]
            prev_line = entry_lines[prev_line_num]
            if prev_line.strip() == 'TER' and cur_line.strip() == 'TER':
                # prevent redundant TER if we filter out a whole section
                continue
            fp.write(cur_line)


def raise_error(error):
    traceback.print_exception(Exception, error, None)


# inner loop we wanna parallize
def dataGen(in_path, out_folder):
    name = os.path.basename(in_path)[:-len(".pdb")]
    data_folder = os.path.join(out_folder, name)
    if not os.path.isdir(data_folder):
        os.mkdir(data_folder)
    out_file = os.path.join(out_folder, name, f"{name}.red.pdb")
    print('out file', out_file)
    try:
        extractBackbone(in_path, out_file)
        assert os.path.exists(out_file)
    except Exception as e:
        print(out_file, file=sys.stderr)
        raise e


# when subprocesses fail you usually don't get an error...
def generateCoordsDir(in_list, out_folder, num_cores=1):
    print('num cores', num_cores)
    print(('warning! it seems that if subprocesses fail right now you don\'t get an error message. '
           'be wary of this if the number of files you\'re getting seems off'))
    # make folder where the dataset files are gonna be placed
    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    # generate absolute paths so i dont have to think about relative references
    out_folder = os.path.abspath(out_folder)

    pool = mp.Pool(num_cores, maxtasksperchild=10)
    for in_file in in_list:
        in_file = os.path.abspath(in_file)
        res = pool.apply_async(dataGen, args=(in_file, out_folder), error_callback=raise_error)

    pool.close()
    pool.join()
    print("Done")


if __name__ == '__main__':
    # idek how to do real parallelism but this should fix the bug of stalling when processes crash
    mp.set_start_method("spawn")  # i should use context managers but low priority change
    parser = argparse.ArgumentParser('Extract backbone from a list of PDB files')
    parser.add_argument('in_list_path',
                        help='file that contains paths to PDB files to clean')
    parser.add_argument('out_folder',
                        help='folder where cleaned .red.pdb files will be placed')
    parser.add_argument('-n',
                        dest='num_cores',
                        help='number of cores to use',
                        default=1,
                        type=int)
    args = parser.parse_args()
    with open(args.in_list_path) as fp:
        in_list = [l.strip() for l in fp]

    generateCoordsDir(in_list, args.out_folder, num_cores=args.num_cores)
