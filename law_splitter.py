# 第一章、第二节，通过换行＋空格来区分。这个目前无法处理
import argparse
import logging
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
    print(lines[:header_name_dict['catalog_index']])


if __name__ == '__main__':
    main()