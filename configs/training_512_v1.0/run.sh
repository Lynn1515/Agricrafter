# NCCL configuration
# export NCCL_DEBUG=INFO
# export NCCL_IB_DISABLE=0
# export NCCL_IB_GID_INDEX=3
# export NCCL_NET_GDR_LEVEL=3
# export NCCL_TOPO_FILE=/tmp/topo.txt

# args
name="training_512crop_filter_v1.4"
config_file=configs/training_512_v1.0/config_finetune.yaml

# save root dir for logs, checkpoints, tensorboard record, etc.
save_root="output"

mkdir -p $save_root/$name
## run
# CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python3 -m torch.distributed.launch \
# --nproc_per_node=$HOST_GPU_NUM --nnodes=1 --master_addr=127.0.0.1 --master_port=12352 --node_rank=0 \
# ./main/trainer.py \
# --base $config_file \
# --train \
# --name $name \
# --logdir $save_root \
# --devices $HOST_GPU_NUM \
# lightning.trainer.num_nodes=1

# debugging
# python3 -m torch.distributed.launch \
# --nproc_per_node=2 --nnodes=1 --master_addr=127.0.0.1 --master_port=12352 --node_rank=0 \
# ./main/trainer.py \
# --base $config_file \
# --train \
# --name $name \
# --logdir $save_root \
# --devices 2 \
# lightning.trainer.num_nodes=1

srun python3 -m torch.distributed.launch \
--nproc_per_node=1 --master_addr=127.0.0.1 --master_port=12345 \
./main/trainer.py \
--base $config_file \
--train \
--name $name \
--logdir $save_root \
--devices 1 \
lightning.trainer.num_nodes=1