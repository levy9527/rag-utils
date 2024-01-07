# 目录兼容两个事：1.目录两字中间有空格　2.目录前面还有前言
import argparse
import logging
from pre_process import is_empty_line

def main():
  logging.basicConfig(level=logging.INFO)
  parser = argparse.ArgumentParser()
  # Add the positional argument for the filename (required)
  parser.add_argument("filename", help="law filename to be processed")

  args = parser.parse_args()
  
  logging.info('opening file...')
  with open(args.filename, 'r', encoding='utf-8') as f:
    lines = list(filter(lambda line: not is_empty_line(line), f.readlines()))
    
    
    print(lines)


if __name__ == '__main__':
    main()