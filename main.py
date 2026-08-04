from ai.agent import Agent
from model_loader import GENERATOR_MODEL, GENERATOR_TOKENIZER, VECTOR_MODEL

agent = Agent(
    generation_model=GENERATOR_MODEL,
    generation_tokenizer=GENERATOR_TOKENIZER,
    embedding_model=VECTOR_MODEL
)

while True:
    prompt = input("> ")
    if prompt == "quit":
        break
    print(
        agent.enter_query(prompt)
    )