import argparse
import logging
import re

from chroma import get_chroma, get_collection, put_into_vector_store
from pre_process import is_empty_line, get_header_dict


def main():
  logging.basicConfig(level=logging.INFO)
  parser = argparse.ArgumentParser()
  # Add the positional argument for the filename (required)
  parser.add_argument("filename", help="law filename to be processed")
  # Add the optional argument for the delimiter
  parser.add_argument("--collection", help="collection name to store embeddings")

  args = parser.parse_args()
  
  logging.info('opening file...')
  with open(args.filename, 'r', encoding='utf-8') as f:
    lines = list(filter(lambda line: not is_empty_line(line), f.readlines()))

    # TODO 第一章、第二节，通过换行＋空格来区分。这个目前无法处理
    header_name_dict = get_header_dict(lines)
    prefaces = lines[:header_name_dict['catalog_index']]
    preface = ''.join(x for x in prefaces)
    
    contents = lines[header_name_dict['content_index']:]
    chunks = [preface]
    rule = ''
    for i, line in enumerate(contents):
      # 先忽略章节，只记录法条
      if is_rule(line):
        chunks.append(rule)
        rule = line
      else:
        rule += line
        
    # 最后一条
    chunks.append(rule)

    client = get_chroma()
    collection = get_collection(client, args.collection)
    put_into_vector_store(collection, chunks, args.filename)

    logging.info("job done!")

def is_rule(line: str):
  pattern = r'第[零一二三四五六七八九十百千]+条'
  found = re.search(pattern, line)
  return bool(found)

if __name__ == '__main__':
    main()