from stanfordprocessor import *

NEGATION_ADVERBS = ["no", "without", "nil","not", "n't", "never", "none", "neith", "nor", "non"]
NEGATION_VERBS = ["deny", "reject", "refuse", "subside", "retract", "non"]

def _stem_(s):
	from nltk.stem.lancaster import LancasterStemmer
	rs = LancasterStemmer()
	rs = rs.stem(s)
	return rs

def _lemma_(token):

	if isinstance(token, str):
		return _stem_(token)
	if isinstance(token, unicode):
		return _stem_(token)
	from nltk.corpus import wordnet

	def get_wordnet_pos(treebank_tag):

		if treebank_tag.startswith('J'):
			return wordnet.ADJ
		elif treebank_tag.startswith('V'):
			return wordnet.VERB
		elif treebank_tag.startswith('N'):
			return wordnet.NOUN
		elif treebank_tag.startswith('R'):
			return wordnet.ADV
		else:
			return ''

	from nltk.stem import WordNetLemmatizer
	wordnet_lemmatizer = WordNetLemmatizer()
	p = get_wordnet_pos(token.pos()[0][1])
	if p!=wordnet.VERB:
		return _stem_(token[0])
	rs = wordnet_lemmatizer.lemmatize(token[0], pos=p)
	return rs

def isNegationWord(token):
	import nltk
	if not isinstance(token, nltk.tree.ParentedTree):
		print "something went terribly wrong with", token
		return None
	if (token.label().startswith("V")) or (token.label().startswith("J")):
		word = token[0]
		if not isinstance(word, unicode):
			return False
		word = word.lower()
		word = _stem_(word)
		stemmed_negation_verbs = [_stem_(verb) for verb in NEGATION_VERBS]
		return word in stemmed_negation_verbs
	word = token[0]
	if not isinstance(word, unicode):
		return False
	word = word.lower()
	word = _stem_(word)
	return word in NEGATION_ADVERBS

def breakWithOutWhiteSpace(sentence):
	import re
	r = "\.\w+"
	sentences = []
	tmp = re.findall(r, sentence, re.X)
	places = [0]
	if len(tmp)>0:
		import enchant
		d = enchant.Dict("en_UK")
		for item in tmp:
			word = item[1:]
			if len(word)<2:
				if word.lower() in ['i','a']:
					places.extend([m.start() for m in re.finditer(item, sentence)])
			else:
				if d.check(item[1:]):
					places.extend([m.start() for m in re.finditer(item, sentence)])

	places = sorted(set(places))
	places.append(len(sentence)-1)
	i = 0
	if len(places)==2:
		return [sentence]

	start = 0
	while True:
		start = places[i]
		if start>0:
			start +=1
		end = places[i+1] + 1
		if end>len(sentence):
			end = len(sentence)-1
		sentences.append(sentence[start:end])
		i +=1
		if len(sentences)==len(places)-1:
			break

	return sentences


def preprocess(sentence, keyword):
	sentence = sentence.replace('NAD ', 'no ')
	stemmed = _stem_(keyword)

	sentence = sentence.replace("\n\n", ".\n\n")
	sentence = sentence.replace("\r\r", ".\n\n")
	sentence = sentence.replace("/suicid", ", suicid")
	sentence = sentence.replace("suicidal/", "suicidal /")
	sentence = sentence.replace("suicide/", "suicide /")
	sentence = sentence.replace("Nosuicid", "No suicid")
	sentence = sentence.replace("nosuicid", "no suicid")
	sentence = sentence.replace("`` t", "'t")
	sentence = sentence.replace("\"", "'")
	sentence = sentence.replace(" 't", "'t")
	sentence = sentence.replace("DSH", "deliberate self harm")
	sentence = sentence.replace("dsh", "deliberate self harm")
	sentence = sentence.replace("wkd", "weekend")
	sentence = sentence.replace(" re ", " regarding ")
	sentence = sentence.replace("\n", " ")
	sentence = sentence.replace(" ,", ",")

	# remove signature, this is nededed for CRIS records...you may have to comment this out
	sentence = sentence.strip()
	try:
		if sentence.startswith('-----'):
			sentence = sentence[sentence.index('-----'):len(sentence)]
			while sentence.startswith('-'):
					sentence = sentence[1:len(sentence)]
		else:
			sentence = sentence[0: sentence.rindex('-----')]
			while sentence.endswith('-'):
				sentence = sentence[0:len(sentence)-1]
	except Exception:
		pass
	
	# break into periods followed by an english word
	sentences = breakWithOutWhiteSpace(sentence)

	# now do the actual chunking
	# return sentence
	if sentences:
		tmp = sentences
	else:
		tmp = [sentence]

	sentences = []
	for s in tmp:
		rs = proc.parse_doc(s)
		for e in rs['sentences']:
			newS = ""
			lastI = 0
			for a, t in zip(e['char_offsets'], e['tokens']):
				if a[0]==lastI:
					newS = newS + t
				else:
					if len(newS)==0:
						newS = t
					else:
						newS = newS + " " + t
				lastI = a[1]
			sentences.append(newS)

	# now do the filtering
	newSentences = []
	for sentence in sentences:
		rs = proc.parse_doc(sentence)
		words = rs['sentences'][0]['tokens']
		stemmedWords = [_stem_(word) for word in words]
		if stemmed in stemmedWords:
			newSentences.append(sentence)

	sentences = newSentences
	return " ".join(sentences)
	if sentences:
		sentence = sentences[0]


	return sentence

def findSentencePTreeToken(sentence, keyword):
	import nltk
	from nltk.tree import ParentedTree
	stemmed = _lemma_(keyword)

	tmp = proc.parse_doc(sentence)
	i = 0
	numSentences = len(tmp['sentences'])
	rs = []
	for i in range(0, numSentences):
		p = tmp['sentences'][i]['parse']
		ptree = ParentedTree.fromstring(p)

		# rs = []
		for i in range(0, len(ptree.leaves())):
			tree_position = ptree.leaf_treeposition(i)

			node = ptree[tree_position]

			if _stem_(node)==stemmed:
				tree_position = tree_position[0:len(tree_position)-1]
				rs.append(ptree[tree_position])
		# if len(rs)>0:
		# 	return rs
	return rs

def getLeaves(ptree):
	import nltk
	rs = []
	if isinstance(ptree, nltk.tree.ParentedTree):
		if len(ptree)>0:
			if  isinstance(ptree[0], unicode):
				rs.append(ptree)
	for node in ptree:
		if isinstance(node, nltk.tree.ParentedTree):
			if len(node)>0:
				if  isinstance(node[0], unicode):
					rs.append(node)
				else:
					rs.extend(getLeaves(node))
	return rs

def reRoot(token, keyword):
	node = token
	parent = token.parent()
	if parent is None:
		return token
	while True:
		parent = node.parent()
		if parent is None:
			break
		if parent.label()=='SBAR':
			node = parent
			break
		if node.parent() is None:
			break


		node = node.parent()
	
	leaves = getLeaves(node)
	sentence = " ".join([t[0] for t in leaves])
	tokens = findSentencePTreeToken(sentence, keyword)
	return tokens[0]

def findTopPhrase(token):
	while True:
		if token.parent() is None:
			break
		if token.parent().label() in ['NP', 'PP', 'VP', 'ADVP', 'ADJP', 'SBAR', 'WHNP']:
			token = token.parent()
		else:
			break
	return token

def getNegations(token):
	leaves = getLeaves(token)
	negations = []
	for leaf in leaves:
		if isNegationWord(leaf):
			negations.append(leaf)
	return negations

def findRelativePosition(root, A, B):
	i = 0
	posA = -1
	posB = -1
	tokens = getLeaves(root)
	for token in tokens:
		if token is A:
			return "L"
		if token is B:
			return "R"

	return "R"
	for i in range(len(tokens)):
		if tokens[i]==A:
			posA = i
		if tokens[i]==B:
			posB = i

	if posA==-1:
		return None
	if posB==-1:
		return None

	if posA<posB:
		return 'L'
	if posA>posB:
		return 'R'
	return True

def getNodes(token):
	subtrees = token.subtrees()
	nodes = list(subtrees)
	return nodes

def isSubordinateConjuction(node):
	#['after', 'as', 'before', 'since', 'until', 'though']:
	# http://www.chompchomp.com/terms/subordinateconjunction.htm
	if node.label()=='IN':
		if node[0] in ['after','although','as','because','before','even if','even though','if','in order that','once','provided that','rather than','since','so that','than','that','though','unless','until','when','whenever','where','whereas','wherever','whether','while','why']:
			return True
	if node.label()=='CC':
		if node.parent() is not None:
			if node.parent().label().startswith("S"):
				return True
			elif node.parent().label() == 'VP':
				return True
		else:
			return False
	return False

def containsNode(listOfNodes, node):
	for n in listOfNodes:
		if n is node:
			return True
	return False

def safeRemoveNode(node, token):
	leaves = getLeaves(node)
	if containsNode(leaves, token):
		return token
	if node is not None:
		if node.parent() is not None:
			node.parent().remove(node)
			return token
	return None

def prune(token):
	nodes = getNodes(token.root())
	conjunctions = []
	for node in nodes:
		if (isSubordinateConjuction(node)) or (node[0]==',') or (node.label()=='S') or (node.label()=='SBAR') or (node.label()=='SINV'):
			if node.label()=='SINV':
				for t in node:
					conjunctions.append(t)
			elif node.label().startswith('S'):
				conjunctions.append(node)
			else:
				for t in node.parent():
					conjunctions.append(t)

	for node in conjunctions:
		rs = safeRemoveNode(node, token)

	return token

def isNegated(token, keyword):
	token = reRoot(token, keyword)
	topPhrase = findTopPhrase(token)
	negations1 = getNegations(topPhrase)
	negations1 = [t for t in negations1 if findRelativePosition(topPhrase, token, t)=='R']
	pruned = prune(token).root()

	leaves1 = getLeaves(topPhrase)
	leaves = getLeaves(pruned)
	leaves = [leaf for leaf in leaves if leaf not in leaves1]

	negations = []
	for leaf in leaves:
		if isNegationWord(leaf):
			negations.append(leaf)

	negationsCount = len(negations)
	if len(negations1)>0:
		negationsCount +=1
	if negationsCount % 2 == 1:
		return True
	return False

def processReturnResult(marks, asBoolean):
	if len(marks)==0:
		return None
	if asBoolean:
		rs = sum(marks)/float(len(marks))
		rs = int(round(rs))
		if rs==1:
			return True
		if rs==0:
			return False
		return None
	else:
		return marks

def predictExpression(sentence, expression, asBoolean=True):
	def getRightSibling(node):
		tokens = getLeaves(node.root())
		i = 0
		while True:
			if tokens[i]==node:
				break
			i = i+1
		if i<len(tokens)-1:
			return tokens[i+1]
		return None
	words = expression.split(" ")
	if len(words)<=1:
		return predict(sentence, expression)

	word = words[0]
	words = findSentencePTreeToken(expression, word)
	word = words[0]
	words = getLeaves(word.root())
	tokens = findSentencePTreeToken(sentence, word[0])
	rs = []
	for token in tokens:
		for word in words:
			if _lemma_(word)!=_lemma_(token):
				token = None
				break
			next = getRightSibling(token)
			if word==words[-1]:
				break
			if next is None:
				break
			token = next

		if token is not None:
			if _lemma_(token)==_lemma_(word):
				if word==words[-1]:
					rs.append(token)

	tokens = rs
	if len(tokens)==0:
		return None
	rs = []
	print tokens
	for token in tokens:
		tmp = not isNegated(token, word[-1])
		rs.append(tmp)

	return processReturnResult(rs, asBoolean)

def predict(sentence, keyword, asBoolean=True):
	sentence = preprocess(sentence, keyword)
	tokens = findSentencePTreeToken(sentence, keyword)
	# print tokens
	if len(tokens)==0:
		return None

	token = tokens[0]
	rs = []

	for token in tokens:
		root = token.root()
		sentence = ""
		for leaf in root.leaves():
			if leaf!=",":
				if len(sentence)==0:
					sentence = leaf
				else:
					sentence = sentence + " " + leaf
			else:
				sentence = sentence + leaf

		tokens = findSentencePTreeToken(sentence, keyword)
		if len(tokens)==0:
			return None

		for token in tokens:
			tmp = isNegated(token, keyword)
			tmp = not(tmp)
			rs.append(tmp)

	return processReturnResult(rs, asBoolean)