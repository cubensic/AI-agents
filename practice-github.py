!pip install -q requests torch bitsandbytes transformers sentencepiece accelerate

from google.colab import userdata
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer, BitsAndBytesConfig
import torch

hf_token = userdata.get("hf_token")
login(token=hf_token, add_to_git_credential=True)

