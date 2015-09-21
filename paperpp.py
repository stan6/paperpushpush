from psutil import virtual_memory 
import re, subprocess, multiprocessing, shutil, pwd, os, sys, getopt, platform,urllib.request, pylatex
from pylatex import Document, Section, Subsection, Table, Math, TikZ, Axis, Plot, Figure, Package, Description, MultiColumn, MultiRow, Tabular 
from pylatex.package import Package, Command
from pylatex.numpy import Matrix
from pylatex.utils import italic, escape_latex, dumps_list


defaultname = "our approach"
currdir = os.getcwd()


class SimpleDocument(Document):
	def __init__(self,default_filepath):	
		super().__init__(default_filepath=default_filepath,documentclass=None,data=None)

	def dumps(self):
		"""Represent the document as a string in LaTeX syntax.
		Returns
		-------
		str
		"""
		sstr = super().dumps()
		strarr = sstr.split('\n')[8:]
		strarr = filter(lambda x: not "{document}" in x,strarr)
		return '\n'.join(strarr)


class Table(Figure):
	def __init__(self, position):	
		super().__init__(position=position)


def current_user():
  if pwd:
    return pwd.getpwuid(os.geteuid()).pw_name
  else:
    return getpass.getuser()


def download_doc_class(doclink):  
	if not doclink:
		doclink="http://www.acm.org/sigs/publications/sig-alternate.cls"
	print("Downloading",doclink)
	filename = doclink.split(os.sep)[-1]
	urllib.request.urlretrieve(doclink,filename)
	return filename[0:filename.find('.')]   


def add_paperprefix(doc):
	doc.append(Command('begin', arguments='abstract'))
	if defaultname == "our approach":
		doc.append('We introduce a new approach that')
	else:
		doc.append('We introduce a new approach called \\toolname')
	doc.append(Command('end', arguments='abstract'))
	return doc


def add_section(filename):
	currfile = currdir+ os.sep +filename 
	doc = SimpleDocument(currfile)	
	return (doc,currfile)


def get_processor_info():
	if platform.system() == "Windows":
		return platform.processor()
	elif platform.system() == "Darwin":
		os.environ['PATH'] = os.environ['PATH'] + os.pathsep + '/usr/sbin'
		command ="sysctl -n machdep.cpu.brand_string"
		return subprocess.check_output(command).strip()
	elif platform.system() == "Linux":
		command = "cat /proc/cpuinfo"
		all_info = subprocess.check_output(command, shell=True,universal_newlines=True).strip()
		for line in all_info.split("\n"):
			if "model name" in line:
				return re.sub( ".*model name.*:", "", line,1)
	return ""


def cpu_countstr():
	count = multiprocessing.cpu_count()
	corestr = ""
	if count == 1:
		corestr = "single"
	if count == 2:
		corestr = "dual"
	elif count == 4:
		corestr = "quad"
	elif count == 8:
		corestr = "octa"
	return corestr + "-core"


def get_totmemory():
	mem = virtual_memory()
	mem_gib = mem.total/(1024.**3) 
	return str('%.2f' % mem_gib)

def machine_config():
	machine_desc = "a " 
	(numbit,rest) = platform.architecture()
	machine_desc = str(numbit) + " machine with a"+ cpu_countstr() + " " + get_processor_info()+" processor and "+ get_totmemory() + "GB of memory."
	return machine_desc

def add_evaluation():
	(doc, currfile) = add_section('evaluation')
	doc.append('We perform an evaluation on TODO benchmark by comparing the effectiveness of our \\toolname. To evaluate the effectiveness of our approach, we aim to address the following research questions:')
	with doc.create(Description()) as desc:
		desc.add_item("RQ1", "What is the overall")
		desc.add_item("RQ2", "How many")
		desc.add_item("RQ3", "How many")
	
	doc.append(Subsection('Experimental Setup'))
	doc.append("We evaluate \\toolname\\ on X subjects. Table~\\ref{substat} lists information about these subjects")

	with doc.create(Table(position='!ht')) as wtable:	
		table1 = Tabular('|c|c|c|c|')	
		table1.add_hline()
		table1.add_row(("Subject", "Description", "kLoc", "Tests"))
		table1.add_hline()
		table1.add_row(('x', 2, 1000, 4))
		table1.add_hline()
		table1.add_row(('y', 6, 1000, 8))
		table1.add_hline()
		wtable.append(table1)	
		wtable.add_caption('Subject Program and Their Basic Statistics')
		wtable.append('\\label{substat}')
			#doc.append(table1)
	doc.append("All experiments were performed on "+machine_config())
	doc.generate_tex(currfile)


def add_package(doc):
	doc.packages.append(Package('algorithm2e',options=['ruled','linesnumbered']))
	return doc

def add_text(doc):
	(idoc, introfile) = add_section("introduction")
	idoc.append('Some regular text and some ')
	idoc.generate_tex(introfile)	
	
	(bdoc, backgroundfile) = add_section("background")
	bdoc.append('Some regular text and some ' + italic('italic text. '))
	bdoc.generate_tex(backgroundfile)	
	
	add_evaluation()
	doc.append(Section('Introduction'))
	doc.append(Command('input', arguments='introduction.tex'))
	doc.append(Section('Background'))
	doc.append(Command('input', arguments='background.tex'))
	doc.append(Section('Experiments'))
	doc.append(Command('input', arguments='evaluation.tex'))

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
	paperfile = currdir+ os.sep +"paper"
	macrofile = currdir+ os.sep +"macro.tex" 
	with open(macrofile,"w+") as f:
		f.write("\\newcommand{\\toolname}{"+defaultname+"}")
	
	name = current_user()
	print("Current_user:",name)
	doc = Document(author=name,date='',title='Paper Title',maketitle=True, default_filepath=paperfile, documentclass=documentcls)
	doc.preamble.append(Command('input', arguments='macro.tex'))

	doc = add_package(doc)
	doc = add_paperprefix(doc)
	doc = add_text(doc)
	doc.generate_tex(paperfile)
	shutil.copy2(paperfile+".tex",paperfile+".tex.copy")	
	doc.generate_pdf(paperfile)
	shutil.copy2(paperfile+".tex.copy",paperfile+".tex")	
	os.remove(paperfile+".tex.copy")

if __name__ == "__main__":
    main(sys.argv[1:])
