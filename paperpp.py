import os, sys, getopt, platform,urllib.request

from pylatex import Document, Section, Subsection, Table, Math, TikZ, Axis, \
    Plot, Figure, Package
from pylatex.package import Package, Command
from pylatex.numpy import Matrix
from pylatex.utils import italic, escape_latex



def download_doc_class(doclink):  
	if not doclink:
		doclink="http://www.acm.org/sigs/publications/sig-alternate.cls"
	print("Downloading",doclink)
	filename = doclink.split(os.sep)[-1]
	urllib.request.urlretrieve(doclink,filename)
	return filename[0:filename.find('.')]   


def add_package(doc):
	doc.packages.append(Package('geometry', options=['tmargin=1cm','lmargin=10cm']))
	doc.packages.append(Package('algorithm2e',options=['ruled','linesnumbered']))
	return doc

def add_text(doc):
	with doc.create(Section('Introduction')):
		doc.append('Some regular text and some ' + italic('italic text. '))
		doc.append(escape_latex('\nAlso some crazy characters: $&#{}'))
	return doc


def main(argv):
	doclink = ''
	outputfile = ''
	try:
		opts, args = getopt.getopt(argv,"hl:o:",["doclink=","output="])
	except getopt.GetoptError:
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print("test.py -l <doclink> -o <outputfile>")
			sys.exit()
		elif opt in ("-l", "--doclink"):
			doclink = arg
		elif opt in ("-o", "--output"):
			outputfile = arg 
	documentcls=download_doc_class(doclink)
	print("Initialize docclass:",documentcls)
	currdir = os.getcwd()
	paperfile = currdir+ os.sep +"paper"
	doc = Document(paperfile,documentcls,"","",False,None)
	doc = add_package(doc)
	doc.append(Command('title', arguments='Paper Title'))
	doc = add_text(doc)
	doc.generate_tex(paperfile)
	doc.generate_pdf(paperfile)



if __name__ == "__main__":
    main(sys.argv[1:])
