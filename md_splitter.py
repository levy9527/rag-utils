import argparse
import logging
import os
import sys
from typing import Dict

from utils import num_tokens_from_string, get_hash, get_chroma, get_collection
from langchain.text_splitter import MarkdownHeaderTextSplitter

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

  args = parser.parse_args()
  filename = args.filename

  logging.info('opening file...')
  with open(filename, 'r', encoding='utf-8') as f:
    #lines = f.readlines()
    #chunks = lines

    content = f.read()

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    docs = markdown_splitter.split_text(content)
    chunks = convert_doc_to_chunks(docs)
    doc_headers = [doc.metadata for doc in docs]

    logging.info("begin chunking")

    client = get_chroma()
    collection = get_collection(client)

    # TODO need solution to work around this: what if exceed token limit?
    for index, chunk in enumerate(chunks):
      #num = num_tokens_from_string(chunk)  fuck? not working
      num = len(chunk)

      # check token
      if num > MAX_TOKENS:
        print(chunk)
        logging.info(f"strlen exceed token limit: {num}")
        sys.exit(1)
      else:
        logging.info('put data into chroma...')

        # 为什么用 uuid? 因为不能批量操作（数据太多），则必须考虑失败重试、重复插入的情况，此时 hash 生成的 id 是稳定的。
        # 当然，这也引入了 hash 冲突的风险，sha224 概率上足够了，如果冲突了，把无法插入的文本修改一下，再重新插入。
        collection.upsert(
          documents=[chunk],
          metadatas=[{"source": os.path.splitext(filename)[0],
                      'index': index,
                      'is_keyword_search': 'false',
                      'header': convert_metadata_to_string(doc_headers[index])
                    }],
          ids=[get_hash(chunk)]
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

