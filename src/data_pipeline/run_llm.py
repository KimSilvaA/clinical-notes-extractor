import json
from openai import OpenAI
from dotenv import load_dotenv
from prompt_builder import build_messages
from pathlib import Path 
import os

project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])  

with open("processed_patient.json", "r", encoding="utf-8") as file:
    patient_record = json.load(file)

response = client.chat.completions.create(
    model="gpt-5.6-terra",
    messages=build_messages(patient_record),
    max_completion_tokens=8192,
    response_format={"type": "json_object"},
)

llm_output = json.loads(response.choices[0].message.content)

print(json.dumps(llm_output, indent=2, ensure_ascii=False))