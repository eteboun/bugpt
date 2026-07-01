from transformers import BitsAndBytesConfig
import torch

from app.agent import Agent

model_name = "Qwen/Qwen2.5-7B-Instruct"
model_quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

agent = Agent(
    model_name=model_name,
    model_quantization_config=model_quantization_config,
)