from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from menu_tools.menu_tools import MenuTools
import json
import torch

model_name = "Qwen/Qwen2.5-7B-Instruct"

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name,
                                             quantization_config=quant_config,
                                             device_map="auto")

available_tools = {
    "menu": MenuTools.tool_menu,
}

with open("menu_tools/MENU_AGENT_SYSTEM_PROMPT", encoding="utf-8") as f:
    menu_sys_prompt = f.read()

with open("FORMATTER_SYSTEM_PROMPT", encoding="utf-8") as f:
    formatter_sys_prompt = f.read()

def agent(prompt):
    menu_messages = [
        {
            "role": "system",
            "content": menu_sys_prompt,
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    text = tokenizer.apply_chat_template(menu_messages,
                                         tokenize=False,
                                         add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=False,
        )

    input_len = inputs["input_ids"].shape[-1]
    generated_ids = outputs[0][input_len:]

    generated = tokenizer.decode(generated_ids, skip_special_tokens=True)
    print(generated)

    tool_call = json.loads(generated)

    tool = available_tools[tool_call["tool"]]
    args = tool_call["args"]

    tool_result = tool(**args)

    formatter_prompt = f"""
    User request: {prompt},\n
    Tool result: {tool_result},\n
    Answer:\n\n
    """

    formatter_messages = [
        {
            "role": "system",
            "content": formatter_sys_prompt,
        },
        {
            "role": "user",
            "content": formatter_prompt,
        }
    ]

    text = tokenizer.apply_chat_template(formatter_messages,
                                         tokenize=False,
                                         add_generation_prompt=True)
    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=500,
            do_sample=False,
        )

    input_len = inputs["input_ids"].shape[-1]
    generated_ids = outputs[0][input_len:]

    answer = tokenizer.decode(generated_ids, skip_special_tokens=True)
    return answer

while True:
    prompt = input("> ")
    result = agent(prompt)
    print('\n\n\n\n\n')
    print(prompt)
    print('\n')
    print(result)