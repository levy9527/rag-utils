import argparse
import logging
import sys

import requests
from bs4 import BeautifulSoup

def main():
  logging.basicConfig(level=logging.INFO)

  parser = argparse.ArgumentParser()
  # Add the positional argument for the filename (required)
  parser.add_argument("url", help="html url")
  args = parser.parse_args()

  response = requests.get(args.url)

  if response.status_code != 200:
    raise requests.HTTPError(f"Request failed with status code {response.status_code}")

  html_content = response.text

  # Create BeautifulSoup object
  soup = BeautifulSoup(html_content, 'html.parser')

  # Perform operations on the parsed HTML
  title_element = soup.find('title')
  title = title_element.get_text(strip=True)
  if not title_element:
    logging.error('html title not found!')
    sys.exit(1)

  # TODO 针对不同 html 的特定代码, 无法复用
  wrapper = soup.find(class_= 'anchor-list')
  markdown = ''
  for item in wrapper.find_all('div', recursive=False):
    header = item.find('h2').get_text()

    texts = item.find_all('p', recursive=False)
    content = '\n'.join([text.get_text() for text in texts])

    markdown += f'# {header}\n{content}\n'

  ouput_file = f'{title}.md'
  with open(ouput_file, 'w', encoding='utf-8') as file:
    file.write(''.join(markdown))

  logging.info(f'markdown generated: {ouput_file}')

if __name__ == '__main__':
  main()