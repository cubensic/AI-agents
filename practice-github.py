from google.colab import userdata
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer, BitsAndBytesConfig
import torch

hf_token = userdata.get("hf_token")
login(token=hf_token, add_to_git_credential=True)

LLAMA = "meta-llama/Meta-Llama-3-8B-Instruct"
PHI3 = "microsoft/phi-3-mini"
GEMMA2 = "google/gemma-2-9b-it"
QWEN2 = "Qwen/Qwen2-72B-Instruct"
MIXTRAL = "mistralai/Mistral-7B-v0.1"

# ------------------------------------------------------------

messages = [
    {"role": "system", "content": "You are a helpful assistant that can answer questions and help with tasks."},
    {"role": "user", "content": "What is the capital of the moon?"}
]

# ------------------------------------------------------------

print(messages)
