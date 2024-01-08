import argparse
import logging
import os

import docx2txt

from pre_process import is_empty_line, remove_white_space, get_header_dict

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

  logging.info(f'markdown generated: {output_path}')


def is_meaningless_line(line):
  strip = line.strip()
  return len(strip) == 1 and strip in ['·', '□']



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


if __name__ == '__main__':
  main()
