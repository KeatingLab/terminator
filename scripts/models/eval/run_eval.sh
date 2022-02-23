#!/bin/bash
#SBATCH -N 1
#SBATCH --mincpu=40
#SBATCH --gres=gpu:volta:2
#SBATCH --time=2:00:00
#SBATCH --exclusive
#SBATCH -o OUTPUTDIR/eval-output.out
#SBATCH -e OUTPUTDIR/eval-error.out

CONDA_ROOT=/state/partition1/llgrid/pkg/anaconda/anaconda3-2019b/
source ${CONDA_ROOT}/etc/profile.d/conda.sh
conda activate terminator
ulimit -s unlimited

python eval.py \
    --dataset=DATASET \
    --model_dir=MODELDIR \
    --output_dir=OUTPUTDIR \
    --subset=SUBSET
