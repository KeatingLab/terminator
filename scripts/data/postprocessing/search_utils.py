"""Functions for searching directories of PDB files and dTERMen runs."""

import glob
import os


def find_pdb_path(pdb, root):
    """Given a PDB ID and a directory of databaseCreator-organized folder of PDBs,
    return the path to the PDB file.

    Args
    ====
    pdb : str
        ID of the queried PDB file
    root : str
        Path to directory of PDB databases

    Returns
    =======
    str
        Path to PDB file

    Raises
    ======
    ValueError
        If the PDB file is not found
    """
    pattern = os.path.join(root, "*", "PDB", pdb[1:3].lower(), f"{pdb}.pdb")
    for pdb_path in glob.glob(pattern):
        if os.path.exists(pdb_path):
            return pdb_path
    raise ValueError(f"{pdb} not found in $RAW_DATA")


def find_dtermen_folder(pdb, root):
    """Given a PDB ID and a directory of dTERMen runs,
    return the path to the dTERMen run.

    Args
    ====
    pdb : str
        ID of the queried PDB file
    root : str
        Path to directory of folders of dTERMen runs

    Returns
    =======
    str
        Path to dTERMen run folder

    Raises
    ======
    ValueError
        If the dTERMen run folder is not found
    """
    for dataDir in glob.glob(os.path.join(root, "*")):
        pdb_folder = os.path.join(dataDir, pdb)
        if os.path.isdir(pdb_folder):
            return pdb_folder
    raise ValueError(f"{pdb} not found in $INPUT_DATA")
