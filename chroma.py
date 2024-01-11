import hashlib
import logging
import os
import re
import sys
import uuid
from datetime import datetime

import chromadb
import tiktoken
import openai
from chromadb import Settings
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

DEFAULT_COLLECTION = "collection_name"

load_dotenv()

MAX_LENGTH = 4096
AZURE_API_VERSION = '2023-07-01-preview'
OPENAI_API_TYPE = 'azure'
OPENAI_API_BASE = os.getenv("AZURE_OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("AZURE_OPENAI_KEY")


def get_chroma(host="10.201.0.32", port="8080"):
  return chromadb.HttpClient(host, port, settings=Settings(allow_reset=True))

def get_collection(client, name = DEFAULT_COLLECTION):
  metadata = {
    "creator": "levy",
    "create_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  }
  collection = client.get_or_create_collection(name, metadata=metadata,
                                               embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                                                 api_key=OPENAI_API_KEY,
                                                 api_base=OPENAI_API_BASE,
                                                 api_type="azure",
                                                 api_version=AZURE_API_VERSION,
                                                 model_name="text-embedding-ada-002")
                                               )
  logging.info(collection)
  return collection


def put_into_vector_store(collection, chunks, filename, is_keyword_search='false', upsert_func=None):
  logging.info('checking chunking length...')
  for index, chunk in enumerate(chunks):
    num = len(chunk)
    # TODO need solution to work around this: what if exceed token limit?
    if num > MAX_LENGTH:
      logging.info(chunk)
      logging.error(f"strlen {num} exceed size limit: {MAX_LENGTH}")
      sys.exit(1)


  for index, chunk in enumerate(chunks):
    logging.info('put data into chroma...')

    if upsert_func is not None:
      logging.info('using customize upsert_func')
      upsert_func(index, chunk)
      continue

    # 为什么不用 uuid? 因为分批操作（数据太多），则必须考虑失败重试、重复插入的情况，此时 hash 生成的 id 是稳定的。
    # 当然，这也引入了 hash 冲突的风险，sha224 概率上足够了，如果冲突了，把无法插入的文本修改一下，再重新插入。
    collection.upsert(
      documents=[chunk],
      metadatas=[{"source": os.path.splitext(filename)[0],
                  'index': index,
                  'is_keyword_search': is_keyword_search,
                  }],
      ids=[get_hash(chunk)]
    )

def get_embedding(text, model="text-embedding-ada-002"):
  logging.info('getting embeddings...')
  openai.api_type = OPENAI_API_TYPE
  openai.api_version = AZURE_API_VERSION
  openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  # Your Azure OpenAI resource's endpoint value.
  openai.api_key = os.getenv("AZURE_OPENAI_KEY")

  text = text.replace("\n", " ")
  return openai.embeddings.create(input = [text], model=model).data[0].embedding

def trim(s, delimiter):
  '''
  remove delimiter and line feed
  '''
  sub = re.sub(delimiter, '', s)
  return sub.replace('\n', '').strip()


def num_tokens_from_string(string: str, encoding_name="cl100k_base") -> int:
  """Returns the number of tokens in a text string."""
  encoding = tiktoken.get_encoding(encoding_name)
  num_tokens = len(encoding.encode(string))
  logging.info(f"Token count: {num_tokens}")
  return num_tokens
def get_uuid():
  random_uuid = uuid.uuid4()
  return str(random_uuid)

def get_hash(content):
  # FIXME just for be compatible
  return get_uuid()
  hash_object = hashlib.sha224()

  # Convert the content to bytes and update the hash object
  hash_object.update(content.encode('utf-8'))

  # Get the hexadecimal representation of the hash
  hash_value = hash_object.hexdigest()

  return hash_value

