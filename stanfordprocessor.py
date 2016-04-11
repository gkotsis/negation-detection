import hashlib
import pickle
import os

import json
import tempfile

curdir = os.path.dirname(os.path.realpath(__file__)) + "/"

try:
	f = open(curdir + 'settings.json')
	data = json.load(f)
	f.close()
	if 'CACHEDIR' in data.keys():
		CACHEDIR = data['CACHEDIR']
	else:
		CACHEDIR = tempfile.gettempdir() + "/"
	CORENLP_JARS_DIR = data['corenlp_jars']
except Exception:
	print "CRITICAL ERROR: NO CORENLP JARS DIR FOUND IN SETTINGS.\nEDIT *settings.json*"
	raise ImportError


def getProcessor():
	from stanford_corenlp_pywrapper import CoreNLP
	class Processor(CoreNLP, object):
		
		def __init__(self):
			global CACHEDIR
			CoreNLP.__init__(self, "parse", corenlp_jars=[CORENLP_JARS_DIR + "*"])


		def fetchFromCache(self, st):
			fname = hashlib.sha224(st.encode('utf-8')).hexdigest()
			if os.path.isfile(CACHEDIR + fname + ".pickle"):
				rs = pickle.load(open(CACHEDIR + fname + ".pickle", "r"))
				return rs
			else:
				return None


		def parse_doc(self, st):
			tmp = self.fetchFromCache(st)
			if tmp is None:
				rs = super(Processor, self).parse_doc(st)
				fname = hashlib.sha224(st.encode('utf-8')).hexdigest()
				import pickle
				pickle.dump(rs, open(CACHEDIR + fname + ".pickle", "w"))
				return rs
			else:
				return tmp

	proc = Processor()
	return proc



proc = getProcessor()