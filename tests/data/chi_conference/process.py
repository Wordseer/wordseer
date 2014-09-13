from bibtexparser.bparser import BibTexParser
import codecs

out_dir = "xml"
in_file = "html/master.bib"

with open(in_file, 'r') as bibfile:
    bp = BibTexParser(bibfile)
    for i, article in enumerate(bp.get_entry_list()):
   		out_file_name = ("xml/%05d.xml" % i )
   		f = codecs.open(out_file_name, 'w', 'utf-8')
   		f.write("<article>\n")
   		f.write("<year>%s</year>\n" % (article['year']))
   		f.write("<title>%s</title>\n" % (article['title']))
   		if 'author' in article:
	   		authors = article['author'].split(" and ")
   			for author in authors:
   				f.write("<author>%s</author>\n" % (author))
   		if 'keyword' in article:
	   		keywords = article['keyword'].split(", ")
   			for keyword in keywords:
   				f.write("<keyword>%s</keyword>\n" % (keyword))
   		f.write("<abstract>%s</abstract>\n" % (article['abstract']))
   		f.write("<article>\n")
   		f.close()

