from huggingface_hub import login
import os

hf_token = os.environ.get('HUGGINGFACE_TOKEN')
# Actually log in with your token
if hf_token:
    login(token=hf_token)
else:
    print("Warning: HUGGINGFACE_TOKEN environment variable not found. You may encounter issues accessing gated models.")

# -------------------------------------------------------------------------------------------------------------------

import torch
from transformers import pipeline
from diffusers import FluxPipeline, DiffusionPipeline
from datasets import load_dataset
import soundfile as sf
from IPython.display import Audio

# -------------------------------------------------------------------------------------------------------------------

my_pipeline = pipeline("sentiment-analysis", device="cuda")

result = my_pipeline("I've been waiting for a Hugging Face course my whole life.")

# -------------------------------------------------------------------------------------------------------------------

classifier = pipeline("sentiment-analysis", device="cuda")
result = classifier("I've been waiting for a Hugging Face course my whole life.")
print(result)

# -------------------------------------------------------------------------------------------------------------------


