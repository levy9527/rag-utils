from law_splitter import is_rule


def test_is_rule():
  str = '　　第一百一十四条'
  with_zero = '　　第一百零一条'
  assert True == is_rule(str)
  assert True == is_rule(with_zero)