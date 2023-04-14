import json
from scholarly import scholarly, ProxyGenerator
import os
import dblp


class Author:

  def __init__(self, author_name, file_name, backup_file_name):
    self.author_name = author_name
    self.file_name = file_name
    self.backup_file_name = backup_file_name
    self.author_info = {}

  def google_scholar_get_author_info(self):
    search_query = scholarly.search_author(self.author_name)
    first_author_result = next(search_query)
    # scholarly.pprint(first_author_result)
    author = scholarly.fill(first_author_result)
    pubs = len(author['publications'])
    for i in range(pubs):
      author['publications'][i] = scholarly.fill(author['publications'][i])
    self.author_info['google_scholar'] = author

  def dblp_get_author_info(self):
    authors = dblp.search(self.author_name)
    # Assume first author
    auth = authors[0]
    auth.load_data()
    data = {}
    data['homepage'] = auth.data['homepages'][0]
    data['name'] = auth.data['name']
    data['publications'] = []
    for index in range(len(auth.publications)):
      auth.data["publications"][index].load_data()
      data['publications'].append(auth.data["publications"][index].data)
    self.author_info['dblp'] = data

  def get_author_info(self):
    self.google_scholar_get_author_info()
    self.dblp_get_author_info()

  def store_info(self):
    with open(self.file_name, "w") as out_file:
      out_file.write(json.dumps(self.author_info))
    print("Commited file!")
  
  def generate_backup_file(self):
    data = self.author_info['google_scholar']
    dblp_data = self.author_info['dblp']
    # create Hashmap of titles
    title_data_hm = {}
    for pub in dblp_data["publications"]:
      title_data_hm[pub['title'].lower()] = pub
    # Sort by year - descending
    data['publications'].sort(key=lambda x:x['bib']['pub_year'], reverse=True)
    with open(self.backup_file_name, "w") as out_file:
      out_file.write("<html>\n")
      out_file.write("<body>\n")
      out_file.write("<div>\n")
      # Write the output in chronological order
      cur_year = -1
      for pub in data['publications']:
        bib = pub["bib"]
        if bib["pub_year"] != cur_year:
          cur_year = bib["pub_year"]
          out_file.write("<h1>" + str(cur_year) + "</h1>\n")
        out_file.write("<p>")
        # Trial code
        bib_title_dblp = bib['title'].lower() + "."
        if bib_title_dblp in title_data_hm:
          # Found title
          dblp_bib = title_data_hm[bib_title_dblp]
          if "pages" in dblp_bib:
            page_count = dblp_bib['pages']
            page_count = page_count.split("-")
            if len(page_count) == 2:
              # Looks valid
              try:
                page_start = int(page_count[0])
                page_end = int(page_count[0])
                if page_end - page_start <= 4:
                  # Demp paper
                  out_file.write("(Demo paper)")
                else:
                  # Need to classify more
                  # For now classify it as full paper
                  out_file.write("(Full paper)")
              except:
                # Something went wrong with parsing
                pass
        out_file.write(", ".join(bib["author"].split(" and ")))
        out_file.write("<b>")
        # Trial code
        a_tag_set = False
        if bib_title_dblp in title_data_hm:
          # Found title
          dblp_bib = title_data_hm[bib_title_dblp]
          if "ee" in dblp_bib and len(dblp_bib["ee"]) > 0:
            out_file.write('<a href="' + str(dblp_bib["ee"]) + '">')
            a_tag_set = True
        out_file.write(bib["title"])
        if a_tag_set:
          out_file.write("</a>")
        out_file.write("</b>")
        out_file.write(bib["citation"])
        out_file.write("</p>\n")
      out_file.write("</div>\n")
      out_file.write("</body>\n")
      out_file.write("</html>\n")


if __name__ == "__main__":
  # No need to use LEVELS as working directory is the root level of github repo
  # So, need to pass publications.json
  # levels = int(os.environ["LEVELS"])
  # level_up = [".."]*levels
  # path = os.path.join(*level_up, "publications.json")
  auth = Author("Suraj Shetiya", "publications.json", "publications_backup.html")
  auth.get_author_info()
  auth.store_info()
  auth.generate_backup_file()
