import json
import os
from hugchat import hugchat
from hugchat.login import Login
from dotenv import load_dotenv

load_dotenv()
email = os.environ.get("HF_CHAT_MODEL_CONFIG_USERNAME")
passwd = os.environ.get("HF_CHAT_MODEL_CONFIG_KEY")
cookie_path_dir="hf_cookies"
print(email, passwd)
sign = Login(email, passwd)
cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

# Get the available models (not hardcore)
models = chatbot.get_available_llm_models()

for model in models:
    print(model)
