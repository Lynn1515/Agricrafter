#!/bin/bash

#SBATCH --job-name=dynamicrafter
#SBATCH --nodes=1                     # This needs to match Trainer(num_nodes=...)
#SBATCH --ntasks-per-node=1           # This needs to match Trainer(devices=...)
#SBATCH --output=runout/%j.out
#SBATCH --error=runout/%j.err
#SBATCH --partition=gpu-a100
#SBATCH --gres=gpu:1
#SBATCH --nodelist=gpu1
#SBATCH --cpus-per-task=16
#SBATCH --comment=yhx_team
export NCCL_P2P_DISABLE=1
export DETECTRON2_DATASETS=/users/cx_xchen/DATASETS/
export MODULEPATH="/opt/app/spack/share/spack/modules/linux-centos7-haswell:/opt/app/spack/share/spack/modules/linux-centos7-cascadelake:/usr/share/Modules/modulefiles:/etc/modulefiles:/opt/app/modulefiles"
source /etc/profile
source /etc/bashrc

source /users/cx_xchen/.bashrc
source /home/cx_wchn/anaconda3/bin/activate

source activate dynamicrafter

cd /home/cx_wchn/lnwang/DynamiCrafter-main

#sh configs/training_512_v1.0/run.sh ## fine-tune DynamiCrafter1024
sh configs/training_512_v1.0/run_interp.sh ## fine-tune interp

