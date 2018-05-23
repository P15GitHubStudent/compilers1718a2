import plex


class ParseError(Exception):
    pass


class RunError(Exception):
    pass


class MyParser():

    def create_scanner(self, fp):
        letter = plex.Range("azAZ")
        digit = plex.Range("09")

        ops = plex.Str("not", "and", "or")
        kprint = plex.Str("print")
        true = plex.NoCase(plex.Str("true", "t", "1"))
        false = plex.NoCase(plex.Str("false", "f", "0"))
        identifier = letter + plex.Rep(letter | digit)
        assign = plex.Str("=")
        space = plex.Rep1(plex.Any(" \n\t"))
        par = plex.Str("(", ")")

        lexicon = plex.Lexicon([
            (kprint, plex.TEXT),
            (ops, plex.TEXT),
            (true, "True"),
            (false, "False"),
            (identifier, "IDENTIFIER"),
            (assign, "="),
            (par, plex.TEXT),
            (space, plex.IGNORE)
        ])

        self.scanner = plex.Scanner(lexicon, fp)
        self.la, self.val = self.next_token()

    def next_token(self):
        return self.scanner.read()

    def match(self, token):
        if self.la == token:
            self.la, self.val = self.next_token()
        else:
            raise ParseError("Expected: ", self.la)

    def parse(self, fp):
        self.create_scanner(fp)
        self.stmt_list()

    def stmt_list(self):
        if self.la == "IDENTIFIER" or self.la == "print":
            self.stmt()
            self.stmt_list()
        elif self.la is None:
            return
        else:
            raise ParseError("Expected: identifier or print")

    def stmt(self):
        # print("stmt: ", self.la)
        if self.la == "IDENTIFIER":
            self.match("IDENTIFIER")
            self.match("=")
            self.expr()
        elif self.la == "print":
            self.match("print")
            self.expr()
        else:
            raise ParseError("Expected: identifier or print")
    def expr(self):
        if self.la == "(" or self.la == "True" or self.la == "not" or self.la  == "False" or self.la == "IDENTIFIER":
            self.term()
            self.term_tail()
        else:
            raise ParseError("Exppected: '(' or identifier or boolean value")

    def term_tail(self):
        if self.la == "or":
            self.orop()
            self.term()
            self.term_tail()
            return
        elif self.la == "print" or self.la is None or self.la == "IDENTIFIER" or self.la == "print":
            return
        else:
            raise ParseError('Expected print or None or IDENTIFIER ')

    def term(self):
        if self.la == "False" or self.la == "True" or self.la == "(" or self.la == "not":
            self.factor()
            self.factor_tail()
            return
        else:
             raise ParseError("Expected: '(' or identifier or boolean value")

    def factor_tail(self):
        if self.la == "and":
            self.andop()
            self.factor()
            self.factor_tail()
            return
        elif self.la == "or" or  self.la == ")" or self.la == "IDENTIFIER" or self.la == "print" or self.la is None:
            return
        else:
            raise ParseError("Expected: 'and'")

    def factor(self):
        if self.la == "not":
            self.match("not") 
        if self.la == '(':
            self.match('(')
            self.expr()
            self.match(')')
            return
        elif self.la =="(" or self.la == "IDENTIFIER" or self.la == "True" or self.la =="False":
            self.match(self.la)
        else:
            raise ParseError("Expected: notop id,  notop(expr), notop values, (expr), id, notop boolean")

    def orop(self):
        if self.la == "or":
            self.match("or")
        else:
            raise ParseError("Expected: 'or'")

    def andop(self):
        if self.la == "and":
            self.match("and")
        else:
            raise ParseError("Expected: 'and'")


p = MyParser()
fp = open("data.txt", "r")
try:
    p.parse(fp)
except ParseError as perr:
    print(perr)
fp.close()
