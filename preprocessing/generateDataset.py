import numpy as np
import os
import json
import pickle
import argparse
from scipy.linalg import block_diag
from parseTERM import parseTERMdata
from parseEtab import parseEtab
import glob


def dumpTrainingTensors(in_path, out_path = None, cutoff = 1000, save=True):
    data = parseTERMdata(in_path + '.dat')
    etab, self_etab = parseEtab(in_path + '.etab', save=False)

    selection = data['selection']

    term_msas = []
    term_features = []
    term_focuses = []
    term_lens = []
    for term_data in data['terms']:
        focus = term_data['focus']
        # only take data for residues that are in the selection
        take = [i for i in range(len(focus)) if focus[i] in selection]

        # cutoff MSAs at top N
        msa = term_data['labels'][:cutoff]
        # apply take
        term_msas.append(np.take(msa, take, axis=-1))

        # add focus
        focus_take = [item for item in focus if item in selection]
        term_focuses += focus_take
        # append term len, the len of the focus
        term_lens.append(len(focus_take))

        # cutoff ppoe at top N
        ppoe = term_data['ppoe'][:cutoff]
        # apply take
        ppoe = np.take(ppoe, take, axis=-1)

        term_len = ppoe.shape[0]
        num_alignments = ppoe.shape[2]
        # cutoff rmsd at top N
        rmsd = np.expand_dims(term_data['rmsds'][:cutoff], 1)
        rmsd_arr = np.concatenate([rmsd for _ in range(num_alignments)], axis=1)
        rmsd_arr = np.expand_dims(rmsd_arr, 1)
        term_len_arr = np.zeros((term_len, num_alignments))
        term_len_arr = np.expand_dims(term_len_arr, 1)
        term_len_arr += term_len
        num_alignments_arr = np.zeros((term_len, num_alignments))
        num_alignments_arr = np.expand_dims(num_alignments_arr, 1)
        num_alignments_arr += num_alignments
        features = np.concatenate([ppoe, rmsd_arr, term_len_arr, num_alignments_arr], axis=1)

        # pytorch does row vector computation
        # swap rows and columns
        features = features.transpose(0, 2, 1)
        term_features.append(features)

    msa_tensor = np.concatenate(term_msas, axis = -1)

    features_tensor = np.concatenate(term_features, axis = 1)

    len_tensor = np.array(term_lens)
    term_focuses = np.array(term_focuses)

    # check that sum of term lens is as long as the feature tensor
    assert sum(len_tensor) == features_tensor.shape[1]

    # create attn mask for transformer
    blocks = [np.ones((i,i)) for i in term_lens]
    # create a block diagonal matrix mask
    src_mask = block_diag(*blocks)
    # note: masks need to be inverted upon use.
    # they're stored this way so padding is easier later

    output = {
        'features': features_tensor,
        'msas': msa_tensor,
        'focuses': term_focuses,
        'mask': src_mask,
        'term_lens': len_tensor,
        'sequence': data['sequence'],
        'seq_len': len(data['selection']),
        'etab': etab,
        'selfE': self_etab
    }


    if save:
        if not out_path:
            out_path = ''

        name = in_path.strip().split('/')[-1]
        with open(out_path + name[:-4] + '.features', 'wb') as fp:
            pickle.dump(output, fp)

    return output

def generateDataset(in_folder, out_folder, cutoff = 1000):
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
            out_file = os.path.join(out_folder, name)
            print('out file', out_file)
            output = dumpTrainingTensors(name, out_path = out_file, cutoff = cutoff)
            dataset.append(output)


    os.chdir(out_folder)
    # place the full dataset in the out_folder
    with open('full.dataset', 'wb') as fp:
        pickle.dump(dataset, fp)

    return dataset

if __name__ == '__main__':
    generateDataset('dTERMen_data', 'features', cutoff = 50)