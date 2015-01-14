import re
import os
from .nodes import TextNode, PythonNode, GroupNode, IfNode, ForNode, SafeNode, CommentNode

DIRECTORY = os.path.join(os.path.dirname(__file__), '..', 'templates')

class ParseException(Exception):
	pass

def split_tokens(s):

	r = re.compile(r'({[{%].*?[%}]})')
	return r.split(s)

def make_dict(label, data):
	return {'label' : label,
			'data'  : data
			}


def id_token(token):
	if token.startswith('{{') and token.endswith('}}'):
		return make_dict('python', token[2:-2].strip())
	elif token.startswith('{%') and token.endswith('%}'):
		inner = token[2:-2].strip().split()
		if inner[0] == 'include':
			return make_dict('include', {'path' : inner[1], 'variables' : inner[2:]})
		elif inner[0] == 'if':
			predicate = " ".join(inner[1:])
			return make_dict('if', predicate)
		elif inner[0] == 'else':
			return make_dict('else', None)
		elif ' '.join(inner) == 'end if':
			return make_dict('end if', None)
		elif inner[0] == 'for':
			return make_dict('for', {'variable': inner[1], 'iterable': " ".join(inner[3:])})
		elif ' '.join(inner) == 'end for':
			return make_dict('end for', None)
		elif inner[0] == 'safe':
			return make_dict('safe', " ".join(inner[1:]))
		elif inner[0] == 'comment':
			return make_dict('comment', ' '.join(inner[1:]))

	else:
		return make_dict('text', token)


def lexer(s):
	tags = split_tokens(s)
	tokens = [id_token(tag) for tag in tags]
	return tokens


def parse(tokens, parent=None, upto=0, parentType=None):
	if parent is None:
		parent = GroupNode()
	while upto < len(tokens):
		currentToken = tokens[upto]
		label = currentToken['label'] 
		if label == 'python':
			newNode = PythonNode(currentToken['data'])
			upto += 1
			parent.addChild(newNode)
		elif label == 'safe':
			newNode = SafeNode(currentToken['data'])
			upto += 1
			parent.addChild(newNode)
		elif label == 'text':
			newNode = TextNode(currentToken['data'])
			upto += 1
			parent.addChild(newNode)
		elif label == 'include':
			upto += 1
			includePath = os.path.join(DIRECTORY, currentToken['data']['path'])
			with open(includePath) as f:
				parse(lexer(f.read()), parent, 0, parentType) #new file, therefore upto = 0
		
		elif label == 'if':
			newNode = IfNode(currentToken['data'])
			parent.addChild(newNode)
			upto += 1
			ifGroup, newPos = parse(tokens, newNode.trueNode, upto, "if")
			upto = newPos
			currentToken = tokens[upto]
			label = currentToken['label']
			if label == "else":
				upto += 1
				elseGroup, newPos = parse(tokens, newNode.falseNode, upto, "else")
				upto = newPos

		elif label == "else":
			if parentType == "if":
				return parent, upto
			else:
				raise ParseException('Found "else" without corresponding "if" statement')
		elif label == 'end if':
			if parentType in ("if", "else"):
				upto += 1
				return parent, upto
			else:
				raise ParseException('Found "end if" without corresponding "if" statement')
			#consider unmatched if

		elif label == 'for':
			newNode = ForNode(currentToken['data']['iterable'], currentToken['data']['variable'])
			parent.addChild(newNode)
			upto += 1
			forGroup, newPos = parse(tokens, newNode.loopBlock, upto, "for")
			upto = newPos
			currentToken = tokens[upto]
			label = currentToken['label']
		elif label == 'end for':
			if parentType == 'for':
				upto += 1
				return parent, upto
			else:
				raise ParseException('Found "end for" without corresponding "for" statement')

		elif label == 'comment':
			upto += 1
			newNode = CommentNode(currentToken['data'])
			parent.addChild(newNode)



	return parent, upto

def render_page(fileName, context):
	filePath = os.path.join(DIRECTORY, fileName)
	with open(filePath) as f:
		return parse(lexer(f.read()))[0].render(context)

# if __name__ == '__main__':
# 	test = """
# 			<html>
# 			<head><title>TitleText</title><head>
# 			{{ 4+2 }} 
# 			{% if False %}
# 			Hello
# 			{% end if %}
# 			more text"""
# 	print(parse(lexer(test))[0].render({}))
