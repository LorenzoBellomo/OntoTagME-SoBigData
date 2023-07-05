import json
from   pathlib import Path
from collections import defaultdict

path_to = "/opt/multi-tagme-master_final/converters"

# pages and redirects
pages_dict = {}
redirect_dict = {}
pages_csv = open("{}/page.csv".format(path_to), "r")
for line in pages_csv.read().split("\n"):
  if not line:
    continue
  info = line.split("\t")
  if len(info) == 2:
    pages_dict[info[1]] = info[0]
  elif len(info) == 3:
    if info[1] not in redirect_dict:
      redirect_dict[info[1]] = set()
    redirect_dict[info[1]].add(info[0])

rev_page = {v: k for k, v in pages_dict.items()}
rev_redir = {}
for k, v in redirect_dict.items():
  for x in v:
    rev_redir[x] = k

# pagelinks
new_pagelinks = defaultdict(list)
pagelinks_csv = open("{}/pagelinks.csv".format(path_to), "r")
for line in pagelinks_csv.read().split("\n"):
    link_components = line.split("\t")
    if len(link_components) == 2:
        _from, to_ = link_components
        new_pagelinks[_from].append(to_)
pagelinks_dict = dict(new_pagelinks)

tagme_dict = dict()
autoincrement = 0

for k, p in pages_dict.items():
  if p not in tagme_dict:
    tagme_dict[p] = autoincrement
    autoincrement += 1

for id_, redirs in redirect_dict.items():
  for p in redirs: # titles
    if p not in tagme_dict:
      tagme_dict[p] = autoincrement
      autoincrement += 1

# categories
write_cats = []
categories_csv = open("{}/category.csv".format(path_to), "r")
categories_csv_write = open("{}/tagme_category.csv".format(path_to), "w")
for line in categories_csv.read().split("\n"):
  cat_components = line.split("\t")
  if len(cat_components) == 3:
    title, _, category = cat_components
    if title in tagme_dict:
      categories_csv_write.write("{}\t{}\t{}\n".format(title, tagme_dict[title], category))

print("NUMBER OF PAGES = ", len(pages_dict))
print("NUMBER OF REDIRECTS = ", len(redirect_dict))
print("NUMBER OF PAGELINKS = ", len(pagelinks_dict))

page_sql      = "\nINSERT INTO `page` VALUES "
pagelinks_sql = "\nINSERT INTO `pagelinks` VALUES "
redirects_sql = "\nINSERT INTO `redirect` VALUES "

articles = """
<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" version="0.10" xml:lang="en">
  <siteinfo>
    <sitename>Wikipedia</sitename>
    <dbname>enwiki</dbname>
    <base>https://en.wikipedia.org/wiki/Main_Page</base>
    <generator>MediaWiki 1.33.0-wmf.4</generator>
    <case>first-letter</case>
    <namespaces>
      <namespace key="-2" case="first-letter">Media</namespace>
      <namespace key="-1" case="first-letter">Special</namespace>
      <namespace key="0" case="first-letter" />
      <namespace key="1" case="first-letter">Talk</namespace>
      <namespace key="2" case="first-letter">User</namespace>
      <namespace key="3" case="first-letter">User talk</namespace>
      <namespace key="4" case="first-letter">Wikipedia</namespace>
      <namespace key="5" case="first-letter">Wikipedia talk</namespace>
      <namespace key="6" case="first-letter">File</namespace>
      <namespace key="7" case="first-letter">File talk</namespace>
      <namespace key="8" case="first-letter">MediaWiki</namespace>
      <namespace key="9" case="first-letter">MediaWiki talk</namespace>
      <namespace key="10" case="first-letter">Template</namespace>
      <namespace key="11" case="first-letter">Template talk</namespace>
      <namespace key="12" case="first-letter">Help</namespace>
      <namespace key="13" case="first-letter">Help talk</namespace>
      <namespace key="14" case="first-letter">Category</namespace>
      <namespace key="15" case="first-letter">Category talk</namespace>
      <namespace key="100" case="first-letter">Portal</namespace>
      <namespace key="101" case="first-letter">Portal talk</namespace>
      <namespace key="108" case="first-letter">Book</namespace>
      <namespace key="109" case="first-letter">Book talk</namespace>
      <namespace key="118" case="first-letter">Draft</namespace>
      <namespace key="119" case="first-letter">Draft talk</namespace>
      <namespace key="710" case="first-letter">TimedText</namespace>
      <namespace key="711" case="first-letter">TimedText talk</namespace>
      <namespace key="828" case="first-letter">Module</namespace>
      <namespace key="829" case="first-letter">Module talk</namespace>
      <namespace key="2300" case="first-letter">Gadget</namespace>
      <namespace key="2301" case="first-letter">Gadget talk</namespace>
      <namespace key="2302" case="case-sensitive">Gadget definition</namespace>
      <namespace key="2303" case="case-sensitive">Gadget definition talk</namespace>
    </namespaces>
  </siteinfo>
"""

Path("sql_tagme").mkdir(parents=True, exist_ok=True)
pg_sql       = open("sql_tagme/enwiki-latest-page.sql", "w+")
pglinks_sql  = open("sql_tagme/enwiki-latest-pagelinks.sql", "w+")
rd_sql       = open("sql_tagme/enwiki-latest-redirect.sql", "w+")
articles_xml = open("sql_tagme/enwiki-latest-pages-articles.xml", "w+")

pg_sql.write(page_sql)
pglinks_sql.write(pagelinks_sql)
rd_sql.write(redirects_sql)
articles_xml.write(articles)


# PAGE SAVING
for id_, title in pages_dict.items():
  id_pg    = str(tagme_dict[title])
  pg_title = title.replace('"', "''").replace("'", "\\'")
  pg_sql.write("(" + id_pg + ",0,'" + pg_title + "','',0,0,0,0,'0','0',0,0,'wikitext',NULL),")


# REDIRECT SAVING
for id_, redirs in redirect_dict.items():
  # PAGE ID
  redir_id    = str(tagme_dict[pages_dict[id_]])
  redir_title = pages_dict[id_].replace('"', "''").replace("'", "\\'")
  for page_title in redirs:
    # REDIRECT ID
    page_id    = str(tagme_dict[page_title])
    page_title = page_title.replace('"', "''").replace("'", "\\'")
    pg_sql.write("(" + page_id + ",0,'" + page_title + "','',0,1,0,0,'0','0',0,0,'wikitext',NULL),")
    rd_sql.write("(" + page_id + ",0,'" + redir_title + "','',''),")

# PAGELINK SAVING
for title_from, title_list_to in pagelinks_dict.items():
  if title_from in tagme_dict:
    tagme_id = str(tagme_dict[title_from])
    for j in title_list_to:
      pglinks_sql.write("(" + tagme_id + ",0,'" + j.replace('"', "''").replace("'", "\\'")+"',0),")


for id_, title in pages_dict.items():
  links = ""
  if id_ in pagelinks_dict:
    for j in pagelinks_dict[id_]:
      links += "[[" + j + "]]\n        "


  tagme_id = str(tagme_dict[pages_dict[id_]])
  title = title.replace('"', "''").replace("'", "\\'")
  articles_xml.write("""
  <page>
    <title>""" + title + """</title>
    <ns>0</ns>
    <id>""" + tagme_id + """</id>
    <revision>
      <text xml:space="preserve">
      Description: """ + title + """

      """+links+"""
      </text>
    </revision>
  </page>
  """)


# redi = "1"
for id_, redirs in redirect_dict.items():
  for j in redirs:
    # tagme_id = str(tagme_dict[pages_dict[i['_id']]])
    tagme_id    = str(tagme_dict[j])
    page_title  = j.replace('"', "''").replace("'", "\\'")
    redi        = pages_dict[id_].replace('"', "''").replace("'", "\\'")
    articles_xml.write("""
    <page>
      <title>""" + page_title + """</title>
      <ns>0</ns>
      <id>"""+tagme_id+"""</id>
      <revision>
        <text xml:space="preserve">
        #REDIRECT [["""+redi+"""]]
        </text>
      </revision>
    </page>
    """)

articles_xml.write("\n</mediawiki>")

pg_sql.close()
pglinks_sql.close()
rd_sql.close()
articles_xml.close()
