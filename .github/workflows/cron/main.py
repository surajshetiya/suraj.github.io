import json
from scholarly import scholarly, ProxyGenerator
import os


class Author:

  def __init__(self, author_name, file_name):
    self.author_name = author_name
    self.file_name = file_name
    self_author_info = {}

  def get_author_info(self):
    search_query = scholarly.search_author(self.author_name)
    first_author_result = next(search_query)
    # scholarly.pprint(first_author_result)
    author = scholarly.fill(first_author_result)
    pubs = len(author['publications'])
    for i in range(pubs):
      author['publications'][i] = scholarly.fill(author['publications'][i])
    self.author_info = author

  def store_info(self):
    with open(self.file_name, "w") as out_file:
      out_file.write(json.dumps(self.author_info))
    print("Commited file!")


if __name__ == "__main__":
  levels = int(os.environ["LEVELS"])
  level_up = [".."]*levels
  path = os.path.join(*level_up, "publications.json")
  print(path)
  auth = Author("Suraj Shetiya", path)
  auth.get_author_info()
  auth.store_info()
  print(os.path.abspath(os.path.join(*level_up)))
  print(os.listdir(os.path.join(*level_up)))
