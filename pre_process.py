import logging
import re
import sys

def get_header_dict(lines):
  ''' item = {"name": name, "level": level, content-index: 1}
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

def has_catalog(lines):
  return '目录' in lines[0]

def is_first_header(line):
  if '1' in line or '一' in line: return True
  return False

# TODO 缺少测试用例
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

def is_empty_line(line):
  return line.strip() == '' or \
    line.strip() == '\n' or \
    line.strip() == '\r' or \
    line.strip() == '\r\n' or \
    line.strip() == '\t'

def remove_white_space(line):
  return "".join(line.split(' '))