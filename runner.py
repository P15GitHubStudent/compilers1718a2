import plex


class ParseError(Exception):
    pass


class RunError(Exception):
    pass

def boolean_value(str1, str2, option):
    if option == "and":
        if str1 == "False" or str2 == "False":
            return "False"
        else:
            return "True"
    elif option == "or":
        if str1 == "False" or str2 == "False":
            return "False"
        else:
            return "True"
    else:
        return "WRONG-INPUT"


def revbool_value(str1, rev):
    if rev:
        if str1 == "True":
            return "False"
        elif str1 == "False":
            return "True"
        else:
            return str1
    else:
        return str1

class MyParser():

    def __init__(self):
        self.st = {}

    def create_scanner(self, fp):
        letter = plex.Range("azAZ")
        digit = plex.Range("09")

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
        if self.la == "IDENTIFIER":
            varname = self.val
            self.match("IDENTIFIER")
            self.match("=")
            self.st[varname] = self.expr()
        elif self.la == "print":
            self.match("print")
            print(self.expr())
        else:
            raise ParseError("Expected: identifier or print")

    def expr(self):
        if self.la in  self.la == "(" or self.la == "IDENTIFIER" or self.la == "not" or self.la == "True" or self.la == "False":
            t = self.term()
            tt = self.term_tail()
            if tt is None:
                return t
            if tt[0] == "or":
                return self.or_operation(t, tt[1])
        else:
            raise ParseError("Expected: '(' or identifier or not or boolean value")

    def term_tail(self):
        if self.la == "or":
            op = self.orop()
            t = self.term()
            tt = self.term_tail()
            if tt is None:
                return op, t
            if tt[0] == "or":
                return op, boolean_value(t, tt[1], "or")
        elif self.la == "IDENTIFIER" or self.la == "print" or self.la == ")" or self.la is None: 
            return
        else:
             raise ParseError('Expected or print or None or identifier ')

    def term(self):
        if self.la == "(" or self.la == "not" or self.la == "IDENTIFIER" or self.la == "True" or self.la == "False": 
            f = self.factor()
            ft = self.factor_tail()
            if ft is None:
                return f
            if ft[0] == "and":
                return boolean_value(f, ft[1], "and")
        else:
            raise ParseError("Expected: '(' or identifier or boolean value")

    def factor_tail(self):
        if self.la == "and":
            op = self.andop()
            f = self.factor()
            ft = self.factor_tail()
            if ft is None:
                return op, f
            if ft[0] == "and":
                return op, boolean_value(f, ft[1], "and")
        elif self.la == "or" or self.la == "print" or self.la =="IDENTIFIER" or self.la == ")" or self.la is None:   
            return
        else:
            raise ParseError("Expected: 'and'")

    def factor(self):
        n = False
        if self.la == 'not':
            self.match("not") 
            n = True   
        if self.la == '(':
            self.match('(')
            e = self.expr()
            self.match(')')
            return revbool_value(e, n)
        elif self.la == "IDENTIFIER":
            varname = self.val
            self.match(self.la)
            if varname in self.st:
                return revbool_value(self.st[varname], n)
            raise RunError("Unitialized variable: ", varname)
        elif self.la in ["True", "False"]:
            token = self.la
            self.match(token)
            return revbool_value(token, n )
        else:
            raise ParseError("Expected: notop id,  notop(expr), notop values, (expr), id, notop boolean")

    def orop(self):
        if self.la == "or":
            self.match("or")
            return "or"
        else:
            raise ParseError("Expected: 'or'")

    def andop(self):
        if self.la == "and":
            self.match("and")
            return "and"
        else:
            raise ParseError("Expected: 'and'")


p = MyParser()
fp = open("data.txt", "r")
try:
    p.parse(fp)
except ParseError as perr:
    print("perr" + perr)
fp.close()
