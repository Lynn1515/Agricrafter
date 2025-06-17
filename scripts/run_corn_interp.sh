version=$1 ##1024, 512, 256
seed=123
#name=dynamicrafter_$1_seed${seed}

ckpt=/home/cx_wchn/lnwang/DynamiCrafter-main/main/output/training_512crop_filter_v1.4/checkpoints/trainstep_checkpoints/epoch=23-step=40000.ckpt
config=configs/inference_512_v1.0.yaml

name=merge_2
prompt_dir=prompts/agri_test/
res_dir="results"
mp4_dir=$res_dir/$name/samples_separate
interp_input=prompts/raw_video_merge2

merge_dir=results/merge_2

if [ "$1" == "256" ]; then
    H=256
    FS=3  ## This model adopts frame stride=3, range recommended: 1-6 (larger value -> larger motion)
elif [ "$1" == "512" ]; then
    H=320
    FS=30 ## This model adopts FPS=24, range recommended: 15-30 (smaller value -> larger motion)
elif [ "$1" == "1024" ]; then
    H=576
    FS=10 ## This model adopts FPS=10, range recommended: 15-5 (smaller value -> larger motion)
else
    echo "Invalid input. Please enter 256, 512, or 1024."
    exit 1
fi

python3 scripts/evaluation/inference.py \
--seed ${seed} \
--ckpt_path $ckpt \
--config $config \
--savedir $res_dir/$name \
--n_samples 1 \
--bs 1 --height ${H} --width $1 \
--unconditional_guidance_scale 7.5 \
--ddim_steps 50 \
--ddim_eta 1.0 \
--prompt_dir $prompt_dir \
--text_input \
--video_length 16 \
--frame_stride ${FS} \
--timestep_spacing 'uniform_trailing' --guidance_rescale 0.7 --perframe_ae

# 1. 拆分视频为帧
echo "=== 开始拆分视频为帧 ==="
python3 interp_raw.py --mode 'interp_prep' --input "$mp4_dir" --output "$interp_input"
echo "=== 视频帧拆分完成 ==="

seed2=12306
ckpt2=/home/cx_wchn/lnwang/DynamiCrafter-main/main/interp_output/training_512_v1.0_interp/checkpoints/trainstep_checkpoints/epoch=178-step=60000.ckpt
name_int=merge_2_interp_$1_seed${seed2}
interp_out=$res_dir/$name_int/samples_separate

python3 scripts/evaluation/inference.py \
--seed ${seed2} \
--ckpt_path $ckpt2 \
--config $config \
--savedir $res_dir/$name_int \
--n_samples 1 \
--bs 1 --height 320 --width 512 \
--unconditional_guidance_scale 7.5 \
--ddim_steps 50 \
--ddim_eta 1.0 \
--prompt_dir $interp_input \
--text_input \
--video_length 16 \
--frame_stride 5 \
--timestep_spacing 'uniform_trailing' --guidance_rescale 0.7 --perframe_ae --interp

# 3. 合并视频片段
echo "=== 开始合并视频片段 ==="
python3 interp_raw.py --mode 'merge' --input "$interp_out" --output "$merge_dir"
echo "=== 视频片段合并完成 ==="

## multi-cond CFG: the <unconditional_guidance_scale> is s_txt, <cfg_img> is s_img
#--multiple_cond_cfg --cfg_img 7.5
#--loop