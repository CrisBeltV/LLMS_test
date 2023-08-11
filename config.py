import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(".env"))

OPENAI_API_KEY:str= os.getenv("OPENAI_API_KEY")
LLAMA_REPLICATE_API_KEY:str = os.getenv("LLAMA_REPLICATE_API_KEY")




