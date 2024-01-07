import logging
from qa_splitter import regroup_by_delimiter

def test_regroup_array():
  array = ['1', '2', '1', '2', '2', '1', '3']
  subgroups = regroup_by_delimiter(list(array), '1')
  logging.info(subgroups)
  assert 3 == len(subgroups)

def test_regroup_first_not_match():
  array = ['0', '1', '2', '1', '2', '2', '1', '3']
  subgroups = regroup_by_delimiter(list(array), '1')
  logging.info(subgroups)
  assert 4 == len(subgroups)
