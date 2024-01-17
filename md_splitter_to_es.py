import argparse
import logging
import sys
from typing import Dict

from dotenv import load_dotenv
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from llama_index import SimpleDirectoryReader, PromptTemplate
from llama_index.evaluation import DatasetGenerator

load_dotenv()

TRUE = 'true'


MAX_TOKENS = 4096

headers_to_split_on = [
  ("#", "H1"),
  ("##", "H2"),
  ("###", "H3"),
  ("####", "H4"),
  ("#####", "H5"),
  ("######", "H6"),
]

def main():
  logging.basicConfig(level=logging.INFO)

  parser = argparse.ArgumentParser()
  # Add the positional argument for the filename (required)
  parser.add_argument("filename", help="markdown file to be split")
  # Add the optional argument for the delimiter
  parser.add_argument("--collection", help="collection name to store embeddings")

  args = parser.parse_args()
  filename = args.filename

  logging.info('opening file...')
  with open(filename, 'r', encoding='utf-8') as f:
    #lines = f.readlines()
    #chunks = lines

    content = f.read()

    logging.info("begin chunking")
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    markdown_docs = markdown_splitter.split_text(content)

    chunk_size = 512
    chunk_overlap = 50
    text_splitter = RecursiveCharacterTextSplitter(
      chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    docs = text_splitter.split_documents(markdown_docs)

    from langchain_community.vectorstores.elasticsearch import ElasticsearchStore
    embedding = OpenAIEmbeddings()
    index_name = 'index_car'
    store = ElasticsearchStore(
      es_params = {
        'timeout': 600,
      },
      embedding=embedding,
      es_url="http://10.201.2.194:9200",
      index_name=index_name,
    )
    #store.client.indices.delete(index=index_name)
    #store.client.indices.create(index=index_name)

    store.add_documents(docs)

    query = "这是一篇关于什么的文档"
    results = store.similarity_search(query)
    print(results)




def get_last_header(str):
  header = str.split(',')[-1]
  logging.info(f'header as keyword: {header}')
  return header

def convert_metadata_to_string(metadata: Dict, separator = ' '):
  # markdown header
  return separator.join([metadata[key] for key in sorted(metadata)])
def convert_doc_to_chunks(docs):
  # pre append header info
  return list(map(lambda doc: convert_metadata_to_string(doc.metadata) + '\n' + doc.page_content, docs))

if __name__ == '__main__':
  main()

