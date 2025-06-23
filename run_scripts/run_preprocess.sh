#!/bin/bash

# python data_preprocess.py \
#   --dataset_name commu_con_gen \
#   --dataset_folder /import/c4dm-datasets/URMP/Dataset \
#   --output_folder ./dataset/preprocessed/URMP \
#   --model_config src/llama_recipes/configs/model_config.json \
#   --train_test_split_file None \
#   --train_ratio 0.9 \
#   --ts_threshold None
  
python data_preprocess.py \
--dataset_name commu_con_gen \
--dataset_folder dataset/commu/commu_midi \
--output_folder dataset/preprocessed/commu \
--model_config src/llama_recipes/configs/model_config_commu_con_gen.json \
--train_test_split_file dataset/commu/commu_meta.csv \
--train_ratio None \
--ts_threshold None

  #   python data_preprocess.py \
  # --dataset_name commu_con_gen \
  # --dataset_folder /import/c4dm-datasets/URMP/Dataset \
  # --output_folder dataset/preprocessed/URMP \
  # --model_config src/llama_recipes/configs/model_config.json \
  # --train_test_split_file None \
  # --train_ratio 0.9 \
  # --ts_threshold None