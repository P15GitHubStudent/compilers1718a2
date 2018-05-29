#!/usr/bin/env python3
# -*- coding: utf_8 -*-
import plex

class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass
class RunError(Exception):
	pass

def join_list(lst):
	return ' '.join(str(e) for e in lst)


class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """

	def __init__(self, debug = True):
		self.debug = debug

	def debug_message(self, caller):
		if self.debug:
			print('--------------------------------')
			print('DEBUG MESSAGE : ')
			print('CALLER : ', caller)
			print('LOOK_AHEAD : ', self.la)

	
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
			self.match('ID')
			self.match('=')
			self.expr()
		elif self.la == 'PRINT':
			self.match('PRINT')
			self.expr()
		else:
			self.debug_message('stmt')
			raise ParseError('Expected identifier print', self.la)

	def expr(self):
		expr_lst = ['(','ID','TRUE', 'FALSE', 'not']
		if self.la in expr_lst:
			self.term()
			self.term_tail()
		else:
			self.debug_message('expr')
			expected_str = join_list(expr_lst)
			raise ParseError('Expected : {} '.format(expected_str))


	def term_tail(self):

		tt_lst = ['or',')', 'ID', 'PRINT', None]

		if self.la == 'or':
			self.or_op()
			self.term()
			self.term_tail()
		elif self.la in tt_lst[1:]:
			return
		else:
			self.debug_message('term_tail')
			expected_str = join_list(tt_lst)
			raise ParseError('Expected : {}'.format(expected_str))		 	
	
	def term(self):
		t_lst = ['FALSE', 'TRUE', '(', 'not', 'ID']
		if self.la in t_lst:
			self.negative_factor()
			self.factor_tail()
			return
		else:
			self.debug_message('term')
			expected_str = join_list(t_lst)
			raise ParseError('Expected : {}'.format(expected_str))

	def factor_tail(self):
		#print('factor_tail - ', self.la)
		ft_lst = ['and', 'or', ')', 'PRINT', 'ID', None]
		if self.la == 'and':
			self.and_op()
			f = self.negative_factor()
			ft = self.factor_tail()

			if ft is None:
				return 'and', f
			if ft[0] == 'and':
				return op, f and ft[1]

		elif self.la in ft_lst[1:]:
			return
		else:
			self.debug_message('factor_tail')
			expected_str = join_list(ft_lst)
			raise ParseError("Expected : {}".format(expected_str))

	def negative_factor(self):
		if self.la == 'not':
			self.match('not')

		return self.factor()

	def factor(self):
		#print('factor - ', self.la)
		nf_lst = ['not', '(', 'ID', 'TRUE', 'FALSE']
		if self.la == '(':
			#print('BASE CASE MATCHED SOMETHING ...')
			self.match('(')
			self.expr()
			self.match(')')
		elif self.la in nf_lst[2: ]:
			#print('BASE CASE FOUND MATCHED SOMETHING ...')
			self.match(self.la)
		else:
			self.debug_message('factor')
			expected_str = join_list(nf_lst[2:])
			raise ParseError('Expected : {}'.format(expected_str))

	def and_op(self):
		if self.la == 'and':
			self.match('and')
		else:
			raise ParseError('Expected and !')

	def or_op(self):
		if self.la == 'or':
			self.match('or')
		else:
			raise ParseError('Expected or !')

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
		print("Parser Error: {} at line {} char {}".format(rerr,lineno,charno+1))
