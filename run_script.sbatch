#!/bin/bash
#SBATCH -p pehlevan_gpu
#SBATCH -n 1
#SBATCH --gres=gpu:1
#SBATCH --mem 60000
#SBATCH -t 7-00:00
#SBATCH --mail-type ALL
#SBATCH -o myoutput_%j.out  # File to which STDOUT will be written, %j inserts jobid
#SBATCH -e myerrors_%j.err  # File to which STDERR will be written, %j inserts jobid
#SBATCH --mail-user yibo_jiang@g.harvard.edu

source activate pytorch
python3 auto_encoder_gd.py --input_dim $inputDim --nb_fixed_point $nbFixedPoint --nb_layer $nbLayer --hidden_dim $hiddenDim --dir $Dir --act $Act