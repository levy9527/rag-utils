import argparse
import logging
import os
import re
import subprocess
import sys

import docx2txt

from pre_process import is_empty_line, remove_white_space

HIDDEN_DIR = '.docx_to_md'

'''
  暂不处理 table/图片
'''
def main():
  logging.basicConfig(level=logging.INFO)

  parser = argparse.ArgumentParser()
  # Add the positional argument for the filename (required)
  parser.add_argument("filename", help="docx filename to be convert to markdown")

  args = parser.parse_args()
  path = args.filename

  # extract text and write images in /tmp/img_dir
  text = docx2txt.process(path)
  lines = text.split('\n')
  header_name_dict = get_header_dict(lines)

  make_hidden_dir()
  tmp_path = f'./{HIDDEN_DIR}/tmp_{get_filename_by_path(path)}.md'

  # attention: img link might be like this
  # <img \n style> or ![]()

  #docx_to_md_cmd = f'pandoc -s {path} -t gfm -o {tmp_path}'
  #subprocess.check_output(docx_to_md_cmd, shell=True).decode().strip()

  #with open(tmp_path, 'r', encoding='utf-8') as f:
    #lines = f.readlines()
    #logging.info(lines)

  file_content = ''
  has_empty_line = False
  for i, line in enumerate(lines[header_name_dict['content_index']:]):
    if is_meaningless_line(line):
      continue

    # skip continuous empty lines
    if is_empty_line(line):
      if has_empty_line:
        continue
      else:
        has_empty_line = True
    else:
      has_empty_line = False

    # TODO 透过现象看本质.docx 特殊处理：这里最后是表格，所以跳过
    if '附录' in line:
      break

    compatible_line = remove_white_space(line)

    header = header_name_dict.get(compatible_line)
    if header:
      header_mark = "".join(list(map(lambda x: '#', range(header.get('level')))))
      compatible_line = f'{header_mark} {compatible_line}'

    file_content += f'{compatible_line}\n'

  logging.info('准备输出 markdown 文件')
  output_path = f'./{HIDDEN_DIR}/{get_filename_by_path(path)}.md'
  with open(output_path, 'w', encoding='utf-8') as file:
    file.write(file_content)

  logging.info('Job done!')


def is_meaningless_line(line):
  strip = line.strip()
  return len(strip) == 1 and strip in ['·', '□']

def get_header_dict(lines):
  ''' item = {"name": name, "level": level, }
  '''
  if not has_catalog(lines):
    print(lines[:100])
    logging.error('请为文档添加目录（目录必须在文档顶部）！')
    sys.exit(1)

  logging.info('准备提取目录')

  headers = []
  found_first_header = False
  content_index = 0
  for i, line in enumerate(lines):
    if not found_first_header and not is_first_header(line): continue
    found_first_header = True

    header = remove_white_space(line)
    if header:
      if len(headers) and headers[0] == header:
        logging.info('匹配目录完成')
        content_index = i
        break
      headers.append(header)

  headers_with_level = parse_headers("\n".join(headers))
  result = {item['name']: item for item in headers_with_level}
  result['content_index'] = content_index

  logging.info('完成提取目录')
  return result


def parse_headers(catalog_text):
  pattern = r'(\d+(\.\d+)*)?(.+?)(?=(\d+(\.\d+)*|$))'
  headers = []

  for line in catalog_text.split("\n"):
    matches = re.finditer(pattern, line.strip())
    for match in matches:
      level = match.group(1).count(".") + 1 if match.group(1) else 1
      name = match.group(1) + match.group(3) if match.group(1) else match.group(3)
      item = {"name": name, "level": level, }

      # 简单为主，直接一维数组，反正消费数据时，可以根据 level 来渲染
      headers.append(item)

  #logging.info(headers)
  return headers

def is_first_header(line):
  if '1' in line or '一' in line: return True
  return False

def make_hidden_dir():
  try:
    os.mkdir(HIDDEN_DIR)
    logging.info(f'making hidden dir: {HIDDEN_DIR}')
  except FileExistsError:
    print(f'hidden dir {HIDDEN_DIR} already exists')

def get_filename_by_path(file_path):
  basename = os.path.basename(file_path)
  filename, _ = os.path.splitext(basename)
  return filename

def has_catalog(lines):
  return '目录' in lines[0]


if __name__ == '__main__':
  main()
