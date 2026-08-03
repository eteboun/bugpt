from ai.agent import Agent
from model_loader import GENERATOR_MODEL, GENERATOR_TOKENIZER

agent = Agent(
    model=GENERATOR_MODEL,
    tokenizer=GENERATOR_TOKENIZER
)

while True:
    prompt = input("> ")
    if prompt == "quit":
        break
    print(
        agent.enter_query(prompt)
    )