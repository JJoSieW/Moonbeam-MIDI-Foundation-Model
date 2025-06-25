#!/bin/bash

export CUDA_LAUNCH_BLOCKING=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

torchrun --nproc_per_node 1 --master_port 29501 recipes/inference/custom_music_generation/conditional_music_generation_batch.py \
  --csv_file dataset/commu/commu_meta.csv \
  --top_p 0.6 \
  --temperature 0.7 \
  --model_config_path src/llama_recipes/configs/model_config_commu_con_gen.json \
  --ckpt_dir checkpoints/moonbeam_839M.pt \
  --finetuned_PEFT_weight_path results/contour_june24_v1/0-120.safetensors \
  --additional_token_dict_path dataset/preprocessed/commu_selected_metadata/indexed_tokens_dict.json \
  --tokenizer_path tokenizer.model \
  --max_seq_len 600 \
  --max_gen_len 600 \
  --max_batch_size 4 \
  --if_add_chords_in_transformer False \
  --if_add_metadata_in_transformer True

# torchrun --nproc_per_node 1 recipes/inference/custom_music_generation/conditional_music_generation_batch.py \
#   --csv_file dataset/commu/commu_meta.csv \
#   --top_p 0.6 \
#   --temperature 0.7 \
#   --model_config_path src/llama_recipes/configs/model_config_commu_con_gen.json \
#   --ckpt_dir checkpoints/moonbeam_839M.pt \
#   --finetuned_PEFT_weight_path checkpoints/conditional \
#   --additional_token_dict_path dataset/preprocessed/commu/indexed_tokens_dict.json \
#   --tokenizer_path tokenizer.model \
#   --max_seq_len 600 \
#   --max_gen_len 600 \
#   --max_batch_size 4 \
#   --if_add_chords_in_transformer True \
#   --if_add_metadata_in_transformer True