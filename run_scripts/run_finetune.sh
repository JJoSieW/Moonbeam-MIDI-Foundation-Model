export CUDA_LAUNCH_BLOCKING=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

torchrun --nnodes 1 --nproc_per_node 1 --master_port 29500 recipes/finetuning/real_finetuning_con_gen.py \
  --lr 3e-4 \
  --val_batch_size 4 \
  --run_validation True \
  --validation_interval 120 \
  --save_metrics True \
  --dist_checkpoint_root_folder checkpoints/contour_v1 \
  --dist_checkpoint_folder ddp \
  --trained_checkpoint_path checkpoints/moonbeam_839M.pt \
  --pure_bf16 True \
  --enable_ddp True \
  --use_peft True \
  --peft_method lora \
  --quantization False \
  --model_name commu_con_gen \
  --dataset commu_con_gen_dataset \
  --output_dir results/contour_v1 \
  --batch_size_training 4 \
  --context_length 848 \
  --num_epochs 2 \
  --use_wandb False