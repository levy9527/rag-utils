# 第一章、第二节，通过换行＋空格来区分。这个目前无法处理
import argparse
import logging
import re

from pre_process import is_empty_line, get_header_dict


def main():
  logging.basicConfig(level=logging.INFO)
  parser = argparse.ArgumentParser()
  # Add the positional argument for the filename (required)
  parser.add_argument("filename", help="law filename to be processed")

  args = parser.parse_args()
  
  logging.info('opening file...')
  with open(args.filename, 'r', encoding='utf-8') as f:
    lines = list(filter(lambda line: not is_empty_line(line), f.readlines()))
    
    header_name_dict = get_header_dict(lines)
    prefaces = lines[:header_name_dict['catalog_index']]
    preface = ''.join(x for x in prefaces)
    
    contents = lines[header_name_dict['content_index']:]
    chunks = [preface]
    rule = ''
    for i, line in enumerate(contents):
      # 先章节，只记录法条
      if is_rule(line):
        chunks.append(rule)
        rule = line
      else:
        rule += line
        
    # 最后一条
    chunks.append(rule)
    
    for i, line in enumerate(chunks):
      logging.info(line)
      

def is_rule(line: str):
  pattern = r'第[零一二三四五六七八九十百千]+条'
  found = re.search(pattern, line)
  return bool(found)

if __name__ == '__main__':
    main()