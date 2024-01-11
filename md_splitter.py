import argparse
import logging
import os
import sys
from typing import Dict

from chroma import num_tokens_from_string, get_hash, get_chroma, get_collection, put_into_vector_store
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

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

    chunks = convert_doc_to_chunks(docs)
    doc_headers = [doc.metadata for doc in docs]

    client = get_chroma()
    collection = get_collection(client, args.collection)
    put_into_vector_store(collection, chunks, filename, upsert_func=lambda index, chunk:
                            collection.upsert(
                              documents=[chunk],
                              metadatas=[{"source": os.path.splitext(filename)[0],
                                          'index': index,
                                          'is_keyword_search': 'false',
                                          'header': convert_metadata_to_string(doc_headers[index])
                                          }],
                              ids=[get_hash(chunk)]
                            )
                          )
    logging.info("job done!")

def convert_metadata_to_string(metadata: Dict, separator = ' '):
  # markdown header
  return separator.join([metadata[key] for key in sorted(metadata)])
def convert_doc_to_chunks(docs):
  # pre append header info
  return list(map(lambda doc: convert_metadata_to_string(doc.metadata) + '\n' + doc.page_content, docs))

if __name__ == '__main__':
  main()

