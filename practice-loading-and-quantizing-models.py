from google.colab import userdata
from huggingface_hub import login
from transformers import AutoTokenizer, AutoModelForCausalLM, TextStreamer, BitsAndBytesConfig
import torch

hf_token = userdata.get("HF_TOKEN")
login(token=hf_token, add_to_git_credential=True)

LLAMA = "meta-llama/Meta-Llama-3.1-8B-Instruct"
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

quant_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_quant_type="nf4"
)

# This quantizes the model to 4-bit precision, which is faster and uses less memory.
# "use doublee quant" is used to reduce the precision EVEN MORE.

# ------------------------------------------------------------

tokenizer = AutoTokenizer.from_pretrained(LLAMA)
tokenizer.pad_token = tokenizer.eos_token
# pad token is the token used to add a special token to the end of the sequence.
inputs = tokenizer.apply_chat_template(messages, return_tensors="pt").to("cuda")

# ------------------------------------------------------------

model = AutoModelForCausalLM.from_pretrained(
    # making the model with the pretrained weights
    # causal lm is used for chat models
    LLAMA,
    device_map="auto",
    quantization_config=quant_config,
)

# when you run this, it downloads all the model weights and puts it locally in a cache folder.
# the model is then temporarily loaded onto the GPU.

# ------------------------------------------------------------

memory = model.get_memory_footprint() / 1e6
print(f"Model memory footprint: {memory:.1f} MB")

# ------------------------------------------------------------

model