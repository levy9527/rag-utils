def is_empty_line(line):
  return line.strip() == '' or \
    line.strip() == '\n' or \
    line.strip() == '\r' or \
    line.strip() == '\r\n' or \
    line.strip() == '\t'

def remove_white_space(line):
  return "".join(line.split(' '))
