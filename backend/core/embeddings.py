import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

load_dotenv("config/.env")

def get_embeddings():
    """返回硅基流动的 Embedding 实例"""
    return OpenAIEmbeddings(
        api_key=os.getenv("SILICONFLOW_API_KEY"),
        base_url="https://api.siliconflow.cn/v1",
        model="BAAI/bge-large-zh-v1.5"
    )