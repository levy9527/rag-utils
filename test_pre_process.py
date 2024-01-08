import pre_process

def test_parse_headers():
  input_string = '3.2.3分析店铺内部现象3.2.3.1分组'
  result = pre_process.parse_headers(input_string)
  assert 2 == len(result)