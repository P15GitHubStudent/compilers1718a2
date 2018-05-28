#!/usr/bin/env python3
# -*- coding: utf_8 -*-

import plex

class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass
class RunError(Exception):
	pass

'''
	conversts our list to boolean
'''
def conv_strtobool(str1):
	if str1 is None:
		raise RunError('str is none')
	str_upper = str1.upper()
	if str_upper == 'TRUE':
		return True
	elif str_upper == 'FALSE':
		return False
	else:
		raise RunError('true or false is only accepted you entered:  {}', str)

def join_list(lst):
	return ' '.join(str(e) for e in lst)

def rev_boolif(b, rev):
	if rev:
		return not b
	else:
		return b			


# def boolean_ops(b1, b2, mode):
# 	mode_l = mode.lower()

# 	if mode_l == 'or':
# 		return b1 or b2
# 	elif mode_l == 'and':
# 		return b1 and b2
# 	else:
# 		raise RunError('and or false is only supported !')

class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """

	def __init__(self, debug = True):
		self.debug = debug
		self.st = {} # our variables names are stores here

	def debug_message(self, caller):
		if self.debug:
			print('--------------------------------')
			print('DEBUG MESSAGE : ')
			print('CALLER : ', caller)
			print('LOOK_AHEAD :  ', self.la)
	
	def create_scanner(self,fp):
		""" Creates a plex scanner for a particular grammar 
		to operate on file object fp. """

		letter = plex.Range("azAZ")
		digit = plex.Range("09")

		ops = plex.Str("not", "and", "or")
		kprint = plex.Str("print")
		true = plex.NoCase(plex.Str("true", "t", "1"))
		false = plex.NoCase(plex.Str("false", "f", "0"))
		identifier = letter + plex.Rep(letter | digit)
		assign = plex.Str("=")
		space = plex.Rep1(plex.Any(" \n\t"))
		par = plex.Any("()")

		lexicon = plex.Lexicon([
			(kprint, "PRINT"),
			(ops, plex.TEXT),
            (true, "TRUE"),
            (false, "FALSE"),
            (identifier, "ID"),
            (assign, "="),
            (par, plex.TEXT),
            (space, plex.IGNORE)
        ])
        
		self.scanner = plex.Scanner(lexicon, fp)
		self.la, self.val = self.next_token()

	def boolean_ops(self,t, tt):
		#print(' boolean_ops -  ', t)
		left = t # to aristero meros you operator
		if tt is None:
			#print('(1)boolean_ops returning ', left)
			return left

		op = tt[0]
		right = tt[1] # to deksi meros tou operator

		if op == 'or':
			#print('(2)boolean_ops returning - ', left, right)
			return left or right
		elif op == 'and':
			#print('(1)boolean_ops returning - ', left,right)
			return left and right
		else:
			raise RunError('supported operators are: and or ')



	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		
		return self.scanner.read()		

	
	def position(self):
		""" Utility function that returns position in text in case of errors.
		Here it simply returns the scanner position. """
		
		return self.scanner.position()
	

	def match(self,token):
		""" Consumes (matches with current lookahead) an expected token.
		Raises ParseError if anything else is found. Acquires new lookahead. """ 
		
		if self.la==token:
			self.la,self.val = self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	def parse(self,fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """

		# create the plex scanner for fp
		self.create_scanner(fp)
		
		# call parsing logic
		self.stmt_list()

	def stmt_list(self):
		#print('stmt_list - ', self.la)
		st_lst = ['ID', 'PRINT']
		if self.la in st_lst:
			self.stmt()
			self.stmt_list()
		elif self.la is None: 
			return # gia na mporei na anagnorize >=0 entoles
		else:
			self.debug_message('stmt_list')
			raise ParseError('waiting for identifier or print your input {}', self.la)

	def stmt(self):
		#print('stmt - ', self.la)
		if self.la == 'ID':
			vname = self.val
			self.match('ID')
			self.match('=')
			self.st[vname] = self.expr() # anathesi 
		elif self.la == 'PRINT':
			self.match('PRINT')
			print(self.expr()) # ektuposi timis apotelesmaton
		else:
			self.debug_message('stmt')
			raise ParseError('waiting for identifier or print', self.la)


	def expr(self):
		#print('expr ', self.la)
		expr_lst = ['(','ID','TRUE', 'FALSE', 'not']
		if self.la in expr_lst:
			t = self.term()
			tt = self.term_tail()
			#print('expr {} - {}'.format(t, tt))
			return self.boolean_ops(t, tt)
		else:
			self.debug_message('expr')
			expected_str = join_list(expr_lst)
			raise ParseError('Expected : {} '.format(expected_str))


	def term_tail(self):
		#print('term_tail - ', self.la)
		tt_lst = ['or',')', 'ID', 'PRINT', None]

		if self.la == 'or':
			self.match('or')
			t = self.term()
			tt = self.term_tail()
			return 'or',self.boolean_ops(t, tt)
		elif self.la in tt_lst[1:]:
			return
		else:
			self.debug_message('term_tail')
			#raise ParseError('Expected or ')
			expected_str = join_list(tt_lst)
			raise ParseError('Expected : {} '.format(expected_str))		 	
	
	def term(self):
		#print('term - ', self.la)
		t_lst = ['FALSE', 'TRUE', '(', 'not', 'ID']
		if self.la in t_lst:
			f = self.negative_factor()
			ft = self.factor_tail()
			#print('term - f ', f)
			#print('term - ft', ft)
			return self.boolean_ops(f, ft)
		else:
			self.debug_message('term')
			expected_str = join_list(t_lst)
			raise ParseError('Expected : {}'.format(expected_str))

	def factor_tail(self):
		#print('factor_tail - ', self.la)
		ft_lst = ['and', 'or', ')', 'PRINT', 'ID', None]
		#print(" begin factor_tail - ", self.la )
		if self.la == 'and':
			self.match('and')
			op = 'and'
			f = self.negative_factor()
			ft = self.factor_tail()
			return  op, self.boolean_ops(f, ft)
		elif self.la in ft_lst[1:]:
			return
		else:
			self.debug_message('factor_tail')
			expected_str = join_list(ft_lst)
			raise ParseError("Expected : {}".format(expected_str))

	def negative_factor(self):
		#print('negative_factor - ', self.la)
		negative = False
		if self.la == 'not':
			self.match('not')
			negative = True
		return rev_boolif(self.factor(), negative)

	def get_idvalue(self, vname):
		#print('getting identifiers value : ')
		if vname in self.st:
			return self.st[vname]
		else:
			raise RunError('Variable {} is not initialised !'.format(vname))

	def or_op(self):
		if self.la == 'or':
			self.match('or')
			return 'or'
		else:
			raise ParseError('Expected or')

	def and_op(self):
		if self.la == 'and':
			self.match('and')
			return 'and'
		else:
			raise ParseError('Expected and ')

	def factor(self):
		#print('factor - ', self.la)
		nf_lst = ['not', '(', 'ID', 'TRUE', 'FALSE']
		if self.la == '(':
			#print('BASE CASE MATCHED SOMETHING ...')
			self.match('(')
			e = self.expr()
			self.match(')')
			return e
		elif self.la in ['TRUE', 'FALSE']:
			#print('converting to boolean - ', self.la)
			boolean = conv_strtobool(self.la)
			self.match(self.la)
			return boolean 		
		elif self.la == 'ID':
			vname = self.val
			#print("VARIABLE NAME IS: ", self.val)
			self.match(self.la)
			return self.get_idvalue(vname)
		else:
			self.debug_message('factor')
			expected_str = join_list(nf_lst[2:])
			raise ParseError('Expected : {}'.format(expected_str))

# create the parser object
parser = MyParser(debug = False)

# open file for parsing
with open("data.txt","r") as fp:

	# parse file
	try:
		parser.parse(fp)
	except plex.errors.PlexError:
		_,lineno,charno = parser.position()	
		print("Scanner Error: at line {} char {}".format(lineno,charno+1))
	except ParseError as perr:
		_,lineno,charno = parser.position()	
		print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))
	except RunError as rerror:
		_,lineno,charno = parser.position()	
		print("Parser Error: {} at line {} char {}".format(rerror,lineno,charno+1))
