"""

sfl.py

This SFL (scrape filter language) module contains all the neccessary
classes to interpret the SFL input stream.

Author: Amirul Menjeni (amirulmenjeni@github.com)

Reference materials:
    * Recursive descent parser:
    https://en.wikipedia.org/wiki/Recursive_descent_parser

    * Backus-Naur Form (BNF):
    https://en.wikipedia.org/wiki/Backus-Naur_form

"""

import re
import logging
import pprint

class Lexer:

    # @param line: The input line.
    #
    # Returns a generator of tokens taken from the input line.
    def lexer(line):
        # A list of token (a tuple with an type of token and the value
        # of the token itself).
        tokens = []
    
        i = 0
        c = ''
        errored_token = ''
        #print('Line length:', len(line))
        while i < len(line):
            errored_token = line[i]
            # Ignore whitespace.
            if Lexer.__is_whitespace(line[i]):
                #print('---WHITESPACE---')
                #print('    i: %s, c: %s' % (i, line[i]))
                i += 1

            # Ignore new lines.
            elif Lexer.__is_newline(line[i]):
                i += 1

            # TYPE: identifier or operator
            #
            # Since there exists some operators with alphabetical
            # character, the starting char of an identifier may
            # be confused with an operator's.
            elif re.match('[_a-zA-Z]', line[i]) or\
                 Lexer.__is_operator(line[i]):

                j = i
                operator = ''
                identifier = ''

                # Assume it's a starting character of an identifier, since
                # the alphabetical chars in the operators is a subset
                # of the chars in the identifiers.
                #print('---IDENTIFIER---')
                while j < len(line) and Lexer.__is_identifier(j, line):
                    #print('    j: %s, c: %s' % (j, line[j]))
                    identifier += line[j]
                    j += 1

                # If the identifier string is not a reserved string
                # for an operator, add it as token.
                if not Lexer.__is_operator_valid(identifier) and\
                       len(identifier) > 0:
                    tokens.append(('identifier', identifier))
                    i = j
                    continue 
                else:
                    # Then this isn't an identifier. Maybe this is an
                    # operator?
                    errored_token = identifier
                    pass

                # The operator tokens contains symbolic characters
                # as well as alphabetical characters (for 'not', 'in', etc).
                # So if the operator starts with a symbolic char, 
                # the remaining chars of the operator must be symbolic
                # char as well. Same applied with alphabetical operators.
                j = i
                #print('---OPERATOR---')
                if line[j].isalpha():
                    while j < len(line) and\
                          Lexer.__is_operator(line[j]) and\
                          line[j].isalpha():
                        
                        #print('    j: %s, c: %s' % (j, line[j]))
                        operator += line[j]
                        j += 1
                else:
                    while j < len(line) and\
                          Lexer.__is_operator(line[j]) and\
                          not line[j].isalpha():

                        #print('    j: %s, c: %s' % (j, line[j]))
                        operator += line[j]
                        j += 1

                # Validate operator token.
                if Lexer.__is_operator_valid(operator):
                    tokens.append((operator, ''))
                    i = j

                else:
                    # Fix nested parentheses not tokenized correctly.
                    k = 0
                    while len(operator) >= 0:
                        operator = operator[:-1]
                        k += 1
                        if Lexer.__is_operator_valid(operator):
                            tokens.append((operator, ''))
                            i = j - k
                            break
                    else:
                        # If this is not an operand either, then this must
                        # be an invalid token.
                        invalid_token = operator
                        if len(operator) == 0:
                            invalid_token = identifier
                        Lexer.__throw_token_error(invalid_token)

            # TYPE: string
            #
            # A token of type string starts with a quote character.
            # Either a single-quote char (') or a double-quote char
            # ("). The opening and closing quote of the string must
            # be a matching pair of chars.
            elif line[i] == '\"' or line[i] == '\'':
                string, i = Lexer.__scan_str(i, line, line[i])
                if string:
                    tokens.append(('string', string))
                else:
                    Lexer.__throw_token_error(string)

            # TYPE: number
            #
            # A token of type number have all digits for its
            # chars. So, 123abc is not an integer.
            elif re.match('[0-9]', line[i]):
                number, i = Lexer.__scan(i, line, '[.0-9]') 
                if number:
                    if Lexer.__is_valid_number(number):
                        tokens.append(('number', number))
                    else:
                        Lexer.__throw_token_error(number)
                else:
                    Lexer.__throw_token_error(number)

            # Weird token.
            else:
                Lexer.__throw_token_error(errored_token)
                logging.error(msg)
                raise ValueError(msg)

        tokens.append(('EOF', ''))
        return tokens

    def __throw_token_error(token):
        msg = 'Invalid token: \'%s\'' % token
        logging.error(msg)
        raise ValueError(msg)

    def __is_operator(c):
        regex = '[(){}<>!=andornotin]'
        return re.match(regex, c) is not None

    def __is_operator_valid(operator):
        valid_operators = ['(', ')', '{', '}', '<', '<=', '>', '>=',\
                           '==', '!=', 'and', 'or', 'not', 'in'] 
        return operator in valid_operators

    def __is_whitespace(c):
        return c == ' ' or c == '\t'

    def __is_newline(c):
        return c == '\n'

    def __is_identifier(i, line):
        c = line[i]
        return re.match('[a-zA-Z0-9_]', line[i]) is not None

    def __scan(i, line, regex_pattern):
        s = ''
        while i < len(line) and re.match(regex_pattern, line[i]):
            s += line[i]
            i += 1

        # Test the next char (if possible), whether or it
        # follows the same regex pattern as those chars collected
        # in `s`. If possible, and the next char does not follow
        # the same pattern, then return None.
        try:
            if line[i] != ' ' or line[i] != '\t':
                return s, i
            if not re.match(regex_pattern, line[i]):
                return None, i
        except IndexError:
            pass
        return s, i

    def __scan_str(i, line, delim):
        s = ''
        #print('i: ', i, 'delim:', delim)
        j  = i + 1
        while j < len(line) and line[j] != delim:
            s += line[j]
            #print('j: ', j, 's:', s)
            j += 1

        # Ensure that an end quote char exists.
        try:
            if not line[j] == delim:
                Lexer.__throw_token_error(delim + s)
        except IndexError:
                Lexer.__throw_token_error(delim + s)
        return s, j + 1 # +1 because of the end quote char.

    # Returns True if the number is valid -- either an integer
    # or a floating point number.
    def __is_valid_number(number):
        return re.match('^\d+(\.\d+)?$', number) is not None

class Parser:
    """
    This Parser class accepts a list of tokens generated from
    the method `Lexer.lexer(input_stream)`. 

    Some this to note -- the variables `tokens`, is the list
    of tokens retrieved from the Lexer class. `tnum` tracks
    which token the Parser is currently at, and the `curr` 
    and `prev` attributes are the current token and the 
    previously parsed token respectively.
    """

    # Tokens variables.
    tokens = None        # The list of tokens.
    tnum = 0             # The current index number of tokens list.
    curr= None          # The current token.
    prev = None          # The previous token.

    # Tuple of valid comparators.
    comparators = ('<', '<=', '>', '>=', '==', '!=', 'not', 'in')

    """
    @param tokens: A list of tokens retrieved from a lexer class.

    Initialize a new instance of the Parser class.
    """
    def __init__(self, tokens):
        self.tnum = 0
        self.tokens = tokens
        self.curr = self.tokens[0]
        self.prev = (None, None)

        print('==============================')
        print('Number of tokens:', len(self.tokens))
        while self.__nextsym():
            print(self.tnum, self.curr)
        print('==============================')
        self.__resetsym()
    
    """
    Updates `tnum`, `curr` and `prev`. 

    If failed to retrieve the next token (due to index out of range),
    this method will return False. Otherwise, when successful, return
    True.
    """
    def __nextsym(self):
        self.tnum += 1
        if self.tnum >= len(self.tokens):
            logging.warning('index out of range, tnum: %s' % self.tnum)
            return False
        self.curr = self.tokens[self.tnum]
        self.prev = self.tokens[self.tnum - 1]
        return True

    """
    Similar to `__nextsym(self)`, this method updates `tnum`, `curr`, and
    `prev`, but instead of advancing the token, this token do the reverse.

    If failed to retrieve the previous token (due to index out range),
    this method will return False. Otherwise, when successful, return 
    True.
    """
    def __prevsym(self):
        self.tnum -= 1
        if self.tnum < 0:
            logging.warning('Index out of range, tnum: %s' % self.tnum)
            return False
        self.curr = self.tokens[self.tnum]
        self.prev = self.tokens[self.tnum - 1]

    """
    Simply reset the state of `tnum`, `curr` and `prev`. Used
    for debugging purpose only.
    """
    def __resetsym(self):
        self.tnum = 0
        self.prev = None, None
        self.curr = self.tokens[self.tnum]

    """
    @param symbol: The symbol/type of the token to be compared
                   with the symbol of the current token, `curr`,
                   whether they match or not.
    
    If the symbol match with the symbol of the current token,
    advance to the next token and return True. Otherwise, return
    False.
    """
    def __accept(self, symbol):
        if self.curr[0] == symbol:
            self.__nextsym()
            return True
        return False

    """
    @param symbol: The symbol of the next token that is expected 
                   to be found after the current token.
             
    Returns True if the expected symbol is found. Otherwise, throw an
    error.
    """
    def __expect(self, symbol):
        if self.__accept(symbol):
            return True
        self.__throw_parse_error(
            'Expected the symbol \'%s\' but got \'%s\' instead. '\
            % (symbol, self.curr[0])
        )

    """
    The ParseTree object instance is created here, and passed down
    to the `__prog` method.
    This method returns the parse tree.
    """
    def parse(self):
        root = ParseTree('PROG', '')
        self.__prog(root)
        return root

    """
    The program node method (start of a BNF set of productions or the 
    root of a parse tree). It add a child note EXPR to itself
    and pass it to the `__expr` node method.
    """
    def __prog(self, root):
        self.__expr(root.add_child('EXPR', 'NODE'))

    """
    The expression node method. Note that the EBNF expression
    for the expression is:

        expr ::= { identifier "{" term { ( "and" | "or" ) term  }  "}"  }
    """
    def __expr(self, node):
     
        # Count the number of identifiers.
        idn_count = 0

        while self.curr[0] == 'identifier':
            idn_count += 1
            node.add_child(self.curr[0], self.curr[1])
            self.__nextsym()
            self.__expect("{")
            node.add_child(self.prev[0], self.prev[1])
            self.__term(node.add_child('TERM', 'NODE'))
            while self.curr[0] in ('and', 'or'):
                node.add_child(self.curr[0], self.curr[1])
                self.__nextsym()
                self.__term(node.add_child('TERM', 'NODE'))
            self.__expect("}")
            node.add_child(self.prev[0], self.prev[1])

        if idn_count == 0:
            self.__throw_e  

    """
    The term node method. Note that the EBNF expression for the term is:

    opt ::= ("<" | "<=" | ">" | ">=" | "==" | "!=" | ["not"] "in")
    term ::= 
          factor opt factor { opt factor }
        | ["not"] term
    """
    def __term(self, node):
        if self.curr[0] == 'not':
            node.add_child(self.curr[0], self.curr[1])
            self.__nextsym()

        self.__factor(node.add_child('FACTOR', 'NODE'))
        while self.curr[0] in Parser.comparators:
            node.add_child(self.curr[0], self.curr[1])
            self.__nextsym()

            if self.curr[0] == 'in':
                node.add_child(self.curr[0], self.curr[1])
                self.__nextsym()

            self.__factor(node.add_child('FACTOR', 'NODE'))

    """
    The factor node method. Note that the EBNF expression for the factor is:

    factor ::= 
          "string" 
        | "number"
        | identifier
        | "(" term ")"
    """
    def __factor(self, node):
        csym, cval = self.curr

        if self.__accept('string'):
            node.add_child(self.prev[0], self.prev[1])

        elif self.__accept('number'):
            node.add_child(self.prev[0], self.prev[1])

        elif self.__accept('identifier'):
            node.add_child(self.prev[0], self.prev[1])

        elif self.__accept('('):
            node.add_child(self.prev[0], self.prev[1])
            self.__term(node.add_child('TERM', 'NODE'))
            self.__expect(')')
            node.add_child(self.prev[0], self.prev[1])

        else:
            self.__throw_parse_error(
                'Factor error: (\'%s\', \'%s\')' % self.curr
            )

    """
    @param msg: The text string message to be shown.
    """
    def __throw_parse_error(self, msg):
        logging.error(msg)
        raise SyntaxError(msg)

class Evaluator:

    """
    @param parse_tree: The parse tree object that is obtained 
                       from the parser.
    @param identifiers: The list of dict of identifiers.
    """
    def eval(parse_tree, identifiers):
        
        pass

    def parse_node(node):

        if node.symbol == 'string':
            return node.value

        elif node.symbol == 'number':
            return node.value

        elif node.symbol == 'identifier':
            pass

        else:
            pass
    def operate(sym):
        pass

class Interpreter:

    # @param scomp: The symbol of the scrap component.
    # @param sattr: The symbol of the component's attribute.
    #
    # Feed this interpreter the identifiers and its values.
    def feed(scomp, sattr, value):
        pass

    def run(line):
        tokens = Lexer.lexer(line)
        parse_tree = Parser(tokens).parse()
        return parse_tree

class ParseTree:

    symbol = ''
    value = ''
    children = []
   
    def __init__(self, symbol, value):
        self.symbol = symbol
        self.value = value
        self.children = []

    """
    Append a new parse tree node that is a child of this
    node, and then return the newly added node.
    """
    def add_child(self, symbol, value):
        new_child = ParseTree(symbol, value)
        self.children.append(new_child)
        return new_child

    """
    Returns the representation of this ParseTree. It will be a pretty
    printed string.
    """
    def __repr__(self, depth=4):
        s = [str('[%s] %s' % (self.symbol, self.value))]
        for child in self.children:
            s.extend(['\n', ' ' * (depth + 1), child.__repr__(depth + 4)])
        return ''.join(s)

    def __str__(self):
        return repr(self)

class Component(dict):
    """
    Usage: 
        Creating a Component instance:
            >> c = Component('post')

        Adding a new attribute and set it's value:
            >> c['score'] = 100

        Getting its attribute:
            >> c['score']
            100
    """

    attr_dict = {}

    def __init__(self, key):
        self.key = key
        self.attr_dict = {}
        self.__dict__[self.key] = self.attr_dict

    def __setitem__(self, attribute, value):
        self.attr_dict[attribute] = value
        self.__dict__[self.key] = self.attr_dict

    def __getitem__(self, attr):
        return self.attr_dict[attr]

    def __repr__(self):
        return "%s::%s" % (self.key, self.attr_dict)

    def __str__(self):
        return repr(self)
