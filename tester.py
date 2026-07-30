from pathlib import Path
from transformers import BitsAndBytesConfig
from ai.agent import Agent

import torch
import shutil
import json

model_name = "Qwen/Qwen3.5-4B"
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

class Tester:

    def __init__(self, test_name):

        self.test_name = test_name
        self.base_dir = Path(__file__).resolve().parent
        self.test_dir = self.base_dir / "tests" / test_name

        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()

    def _write_system_prompts(self):

        system_prompts_dir = self.base_dir / "app" / "system_prompts"
        for system_prompt_file in system_prompts_dir.iterdir():
            system_prompt = system_prompt_file.read_text()

            with open(self.test_dir / system_prompt_file.name, "w", encoding="utf-8") as f:
                f.write(system_prompt)

    def _test_and_write_queries(self, queries: list[str]):

        results = []
        size = len(queries)

        for idx, query in enumerate(queries):
            trace = agent.test_query(query=query)
            results.append(trace.as_dict())

            print(f"{idx+1}/{size} queries tested.")

        with open(self.test_dir / "results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)


    def run(self, queries: list[str]):
        self._write_system_prompts()
        self._test_and_write_queries(queries)

queries = [
    "Değişim programına başvurmak için minimum GNO kaç olmalı?",
    "Değişim programına başvuru için dil şartı nedir?",
    "Değişim öğrencileri konaklamayı kendileri mi ayarlamak zorunda?",
    "Bir dönemde alınabilecek maksimum kredi sayısı kaçtır?",
    "Bir dönemde alınabilecek minimum kredi sayısı kaçtır?",
    "Danışman onayıyla kredi yükü kaça kadar düşürülebilir?",
    "BB aldığım bir dersi tekrar alabilir miyim?",
    "Çift ana dal öğrencileri yurtta en fazla kaç yıl kalabilir?",
    "Yüksek lisans öğrencileri yurtta kaç yıl kalabilir?",
    "Doktora öğrencileri yurtta en fazla kaç yıl kalabilir?",
    "Mezun olduktan sonra yurtta kalmaya devam edebilir miyim?",
    "Doktora programında bilimsel hazırlık var mı?",
    "Doktora başvurusu için İngilizce yeterlilik şartı nedir?",
    "İngilizce dışında bir dilde yapılan değişim programında hangi dil belgesi gerekir?",
    "ÇAP yapmak için gereken mezuniyet kredisi ana daldan kaç kredi fazla olmalıdır?"
]

tester = Tester("test_0.5")
tester.run(queries)