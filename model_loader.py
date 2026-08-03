from sentence_transformers import SentenceTransformer
from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM
from config.model_config import GENERATOR_MODEL_NAME, VECTOR_MODEL_NAME
import torch

VECTOR_MODEL = SentenceTransformer(
    VECTOR_MODEL_NAME,
    device="cuda"
)

GENERATOR_MODEL_QUANT_CONFIG = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)
GENERATOR_TOKENIZER = AutoTokenizer.from_pretrained(GENERATOR_MODEL_NAME)
GENERATOR_MODEL = AutoModelForCausalLM.from_pretrained(
    GENERATOR_MODEL_NAME,
    device_map="auto",
    quantization_config=GENERATOR_MODEL_QUANT_CONFIG,
    torch_dtype=torch.float16,
)