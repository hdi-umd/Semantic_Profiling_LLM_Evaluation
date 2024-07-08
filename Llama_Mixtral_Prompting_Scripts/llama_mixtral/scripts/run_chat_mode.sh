#!/bin/bash
DATE=$(date "+%m%d%y_%H_%M_%S")
module load cuda/11.7.0 cudnn/v8.8.0 gitlfs/2.10.0 
conda init bash
source /fs/nexus-scratch/kcobbina/miniconda3/bin/activate /fs/nexus-scratch/kcobbina/miniconda3/envs/aae/
python --version
nvidia-smi
module list

# python new/src/generator.py \
#     --model_name_or_path mistralai/Mistral-7B-Instruct-v0.2 \
#     --template mistral \
#     --finetuning_type lora

# python new/src/generator.py \
#     --model_name_or_path mistralai/Mixtral-8x7B-v0.1 \
#     --template mistral \

# python new/src/generator_2.py \
#     --model_name_or_path mistralai/Mixtral-8x7B-Instruct-v0.1 \
#     --template mistral \
#     --flash_attn True \
#     --quantization_bit 8 

# python new/src/generator.py \
#     --model_name_or_path meta-llama/Llama-2-7b-chat-hf \
#     --template llama2 

# python new/src/generator.py \
#     --model_name_or_path meta-llama/Llama-2-13b-chat-hf \
#     --template llama2 \ 

# python new/src/generator.py \
#     --model_name_or_path meta-llama/Llama-2-70b-chat-hf \
#     --template llama2 \
#     --flash_attn True \
#     --quantization_bit 8 

python src/gen_for_coraal.py \
    --model_name_or_path meta-llama/Llama-3-70b-chat-hf \
    --template llama2 \
    --flash_attn True \
    --quantization_bit 8 
