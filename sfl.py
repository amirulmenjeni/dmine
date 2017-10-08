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
import copy
import logging

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
        opt_chars = '[(){}<>!=andornotin]'
        while i < len(line):
            errored_token = line[i]
            # Ignore whitespace.
            if Lexer.__is_whitespace(line[i]):
                i += 1

            # Ignore new lines.
            elif Lexer.__is_newline(line[i]):
                i += 1

            # TYPE: identifier, operator, or boolean.
            #
            # Since there exists some operators with alphabetical
            # character, the starting char of an identifier may
            # be confused with an operator's.
            #
            # Boolean is also consists of alphabetical chars, 
            # similar to identifier.
            elif re.match('[_a-zA-Z]', line[i])\
            or   re.match(opt_chars, line[i]):

                operator = ''
                identifier = ''
                boolean = ''

                # Assume it's a boolean value.
                boolean, i = Lexer.__scan(
                    i, line, '[TrueFalse]', '^(True|False)$'
                )
                if boolean:
                    tokens.append(('boolean', boolean))
                    continue

                # Assume it's an operator.
                opts = '^(\(|\)|\{|\}|<|<=|>|>=|==|!=|=|and|or|not|in)$'
                operator, i = Lexer.__scan(
                    i, line, opt_chars, opts
                )
                if operator:
                    tokens.append((operator, ''))
                    continue
                
                # Assume it's an identifier.
                identifier, i = Lexer.__scan(
                    i, line, '[_a-zA-Z0-9]', '^[a-zA-Z0-9_]+$', last=True
                )
                if identifier:
                    tokens.append(('identifier', identifier))
                    continue


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
            elif re.match('[\-0-9]', line[i]):
                number, i = Lexer.__scan(i, line, '[\-\.0-9]', '-?\d+(\.\d+)?') 
                if number:
                    tokens.append(('number', number))
                else:
                    Lexer.__throw_token_error(number)

            # TYPE: storable
            #
            # A token of type storable must starts with the
            # `$` character. Then the following characters
            # follows the identifier pattern rule.
            elif line[i] == '@':
                storable, i = Lexer.__scan(
                    i, line, '[\_\@a-zA-Z0-9]', '\@[a-zA-Z0-9_]+'
                )
                if storable:
                    tokens.append(('storable', storable))
                else:
                    Lexer.__throw_token_error(storable)
            
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

    def __is_whitespace(c):
        return c == ' ' or c == '\t'

    def __is_newline(c):
        return c == '\n'

    def __scan(i, line, chars_pattern, token_pattern, last=False):
        """
        @param i: The position of the char in the string line
                  to start scan.
        @param line: The input stream string.
        @param chars_pattern: The chars' regex pattern e.g. [a-zA-Z0-9]
        @param token_pattern: The token's regex pattern e.g. ^(True|False)$
        @param last: If set to True, then a non-match will result in error
                     being thrown instead of returning None and the
                     index.
        """
        s = ''
        j = i

        # Special characters: delimiters that indicate
        # a token's boundary.
        if line[i] in ('{', '}', '(', ')'):
            if re.match(token_pattern, line[i]):
                return line[i], j + 1
            else:
                return None, i

        # Scan and append chars in the line from j-th index
        # until an unwanted char is reached.
        delimiter = '(\s|{|}|\(|\))'
        while j < len(line) and not re.match(delimiter, line[j]):
            s += line[j]
            j += 1

        # Try to match the scanned string `s` with the `token_pattern`
        # regex string. If it doesn't match, then return None and 
        # restore the current index (by returning `i`).
        match = re.match(token_pattern, s)
        if not match:
            if last:
                Lexer.__throw_token_error(s)
            else:
                return None, i
        return s, j

    def __scan_str(i, line, delim):
        s = ''
        j  = i + 1
        while j < len(line) and line[j] != delim:
            s += line[j]
            j += 1

        # Ensure that an end quote char exists.
        try:
            if not line[j] == delim:
                Lexer.__throw_token_error(delim + s)
        except IndexError:
                Lexer.__throw_token_error(delim + s)
        return s, j + 1 # +1 because of the end quote char.

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

    def __accepts(self, sym, *syms):
        sym_list = [sym]
        sym_list.extend(syms)
        if self.curr[0] in sym_list:
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
        root = ParseTree('PROG', 'NODE')
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

        expr ::= 
            { 
                ( 
                    { identifier "{" eval "}"  }  | 
                    { storable = ( "string" | "integer" ) }
                ) 
            }
    """
    def __expr(self, node):

        while self.__accept('identifier') or self.__accept('storable'):
            if self.prev[0] == 'identifier':
                # Add the identifier (scrape component),
                # and expect "{"
                node.add_child(self.prev[0], self.prev[1]) 
                self.__expect('{')
                node.add_child(self.prev[0], self.prev[1])

                # EVAL production.
                self.__eval(node.add_child('EVAL', 'NODE'))

                self.__expect('}')
                node.add_child(self.prev[0], self.prev[1])
            else:
                storable = node.add_child(self.prev[0], self.prev[1])
                self.__expect('=')
                node.add_child(self.prev[0], self.prev[1])
                if self.__accept('string')\
                or self.__accept('number')\
                or self.__accept('boolean'):
                    node.add_child(self.prev[0], self.prev[1])
                else:
                    self.__throw_assignment_error(storable.value)                    

    """
    The eval node method. Note that the EBNF expression for the expression
    is:
        eval ::= term ( "and" | "or" ) term { ( "and" | "or" ) term }
    """
    def __eval(self, node):
        self.__term(node.add_child('TERM', 'NODE'))
        while self.curr[0] in ('and', 'or'):
            node.add_child(self.curr[0], self.curr[1])
            self.__nextsym()
            self.__term(node.add_child('TERM', 'NODE'))

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
        | "(" eval ")"
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
            self.__eval(node.add_child('EVAL', 'NODE'))
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

    def __throw_assignment_error(self, token):
        msg = 'The storable token \'%s\' was expecting an integer, '\
              'a string, or a boolean value.' % token
        logging.error(msg)
        raise SyntaxError(msg)

class Evaluator:

    def eval(pt, idns, stors):
        """
        @param pt: The parse tree object that is obtained 
                   from the parser.
        @param idns: The list of dict of identifiers.
        """
        out = Evaluator.parse_node(pt, idns, stors)
        if out is None:
            out = {}
        return out

    def parse_node(node, idns, stors, scope=''):
        """
        @param node: A node in a parse tree.
        @param idns: The list of Component class from sfl module.
        @param scope: This should be left untouched at first called.
                      This parameter is used internally in this method
                      to keep track and check the scope of the scrap 
                      attributes.

        This method recursively evaluate a node in the parse tree.

        Simply put, given parse tree from the following scrap filter input:
        
            post { score > 0 } comment { 0 < score < 100 } $my_var = 123

        If the post's score is greater than zero, but the comment's score
        is greater than 100, this method will returns the following 
        dictionary object:

            {post: True, comment: False, $my_var: 123}

        """

        for n in node.children:

            if n.symbol == 'string':
                if n.parent.symbol != 'EXPR':
                    n.parent.children = []
                    n.parent.symbol, n.parent.value = n.symbol, n.value

            elif n.symbol == 'number':
                if n.parent.symbol != 'EXPR':
                    n.parent.children = []
                    n.parent.symbol, n.parent.value = n.symbol, int(n.value)

            elif n.symbol == 'identifier':
                if scope == '':
                    # Update the new scope, and check if it's defined.
                    scope = n.value
                    if not Evaluator.__is_comp_defined(idns, scope):
                        Evaluator.__throw_eval_error(
                            'Undefined scrape component: %s' % scope
                        )
                else:
                    # Check if the identifier is defined within the scope.
                    # (i.e. if the component contains the attribute.)
                    if not Evaluator.__is_comp_defined(idns, scope, n.value):
                        Evaluator.__throw_eval_error(
                            'In the scrape component \'%s\', '\
                            'there\'s undefined attribute: %s'\
                            % (scope, n.value)
                        )
                    # If it is, then move the value up a node.
                    n.value = Evaluator.__get_idn_val(idns, scope, n.value)
                    n.parent.children = []
                    n.parent.symbol, n.parent.value = n.symbol, n.value

            elif n.symbol == 'EXPR':
                Evaluator.parse_node(n, idns, scope)

                # Once we finished parsing each nodes in EXPR,
                # create the output dict and return it.
                out = {}
                for i in range(len(n.children)):
                    m = n.children[i]
                    if m.symbol == 'identifier':
                        out[(m.symbol, m.value)] = n.children[i + 2].value
                    elif m.symbol == 'storable':
                        if not Evaluator.__is_stor_defined(stors, m.value):
                            Evaluator.__throw_eval_error(
                                'Undefined storable: %s' % m.value
                            )
                        # Assign value to the storable token.
                        val_token = n.children[i + 2]
                        val = val_token.value
                        if val_token.symbol == 'number':
                            val = int(val)
                        out[(m.symbol, m.value[1:])] = val
                return out

            elif n.symbol == 'EVAL':
                Evaluator.parse_node(n, idns, stors, scope)
                Evaluator.__operate(n)

            elif n.symbol == 'TERM':
                Evaluator.parse_node(n, idns, stors, scope)
                Evaluator.__operate(n)

            elif n.symbol == 'FACTOR':
                Evaluator.parse_node(n, idns, stors, scope)

                # Every operated node has its children emptied.
                # Therefore, we only operate a FACTOR node 
                # if it has at least 1 child.
                if len(n.children) > 0:
                    Evaluator.__operate(n)
                    n.parent.value = n.value

            else:
                # This node should be an operator, if it's non
                # of the above.
                
                # Reset the scope when '}' end of scope.
                if n.symbol == '}':
                    scope = ''

    def __operate(n):
        """
        @param n: A node of a parse tree.

        Do the operations pernaining the children of the node n.
        This method only changes the structure of node n, and does not
        return anything.
        """

        # If a node has only one child (i.e. no evaluation takes place),
        # then just take the child's value.
        if len(n.children) == 1:
            n.value = n.children[0].value
            n.children = []
            return

        i = 0
        opts = ('<', '<=', '>', '>=', '==', '!=',\
                'and', 'or', 'not', 'in', '(')
        is_negate = False
        while i < len(n.children):

            opt = ''
            j = 0 # Used to calculate the char-length of the operator.
            res = True

            while n.children[i].symbol in opts:
                opt += n.children[i].symbol
                i += 1
                j += 1
                
                if i >= len(n.children):
                    break

            if opt != '':
                
                # If the operation is a negation, we set the negation
                # flag and continue to be used against the next operation's
                # result.
                if opt == 'not':
                    is_negate = True
                    continue

                left = None
                if i - j - 1 >= 0:
                    left = n.children[i - j - 1].value
                right = n.children[i].value

                # Handling the occurence when left or right operand
                # has not been assigned any value.
                if right is None or left is None:
                    # This is the side effect of calling
                    # to evaluate the parse tree before assigning
                    # values to the components' attributes.
                    msg = 'An operand has no value assigned. Ignoring '\
                          'the \'<%s> %s <%s>\' operation.'\
                          % (n.children[i - j - 1].symbol, 
                             opt, n.children[i].symbol)
                    logging.debug(msg)
                    continue

                operate = {
                    '<': lambda x, y: x < y,
                    '<=': lambda x, y: x <= y,
                    '>': lambda x, y: x > y,
                    '>=': lambda x, y: x >= y,
                    '==': lambda x, y: x == y,
                    '!=': lambda x, y: x != y,
                    'in': lambda x, y: x in y,
                    'notin': lambda x, y: x not in y,
                    'and': lambda x, y: x and y,
                    'or': lambda x, y: x or y,
                    '(': lambda x, y: y
                }
                try:
                    res = operate[opt](left, right)
                    if is_negate:
                        res = not res
                        is_negate = False
                except TypeError as e:
                    Evaluator.__throw_eval_error(
                        str(e) + '. left operand is \'%s\', and '\
                        'the right operand is \'%s\'.'\
                        % (left, right)
                    )

            if res:
                i += 1
            else:
                break

        n.children = []
        n.value = res
            
    def __get_idn_val(idns, comp, attr):
        for idn in idns:
            if idn.name == comp:
                return idn[attr]
        Evaluator.__throw_eval_error(
            'Attribute not found: %s' % attr
        )
  
    def __is_comp_defined(idns, component, attribute=None):
        """
        @param idns: A list of sfl.Component object.
        @param component: The supposed component.
        @param attribute: The supposed attribute the component.

        Check if the identifier (the scrape component or its attribute) 
        is defined or not. Returns True if defined. Otherwise, 
        returns False.
        """
        
        # The attribute is None, so we're only
        # checking whether the component is defined.
        if attribute is None:
            for idn in idns:
                if component == idn.name:
                    return True
            return False

        # The attribute is not None, so we're checking
        # whether the attribute is defined under the component.
        else:
            for idn in idns:
                if idn.has_attr(attribute):
                    return True
            return False
    
    def __is_stor_defined(stors, sname):
        """
        @param stors: The list of sfl.Storable object. 
        @param sname: The supposed storable's name.

        Check if the storable is defined or not. Returns true if defined.
        Otherwise, returns False.
        """
        for s in stors:
            if s.fname == sname:
                return True
        return False

    def __throw_eval_error(msg):
        logging.error(msg)
        raise SyntaxError(msg)

class Interpreter:
    """
    This class is responsible to stitch everything together.
    """

    identifiers = [] # List of sfl.Component objects.
    storables = []   # List of sfl.Storable objects.
    scrape_filter = None

    def feed(scrape_filter):
        """
        @param scrape_filter: A scrape filter object.
        
        Feed this interpreter the identifiers and storables.
        The list `Interpreter.identifiers` is emptied before
        it is filled again with new values. The list
        `Interpreter.storables` is only filled once.
        """

        Interpreter.identifiers = []
        for comp_name in scrape_filter.comp:
            component = Component(comp_name)
            comp = scrape_filter.comp
            for attr_name in comp[comp_name].attr:
                attr = comp[comp_name].attr
                component[attr_name] = attr[attr_name].value
            Interpreter.identifiers.append(component)

        if len(Interpreter.storables) == 0:
            for name, variable in scrape_filter.var.items():
               storable = Storable(name, variable.default_value)
               Interpreter.storables.append(storable) 

    def set(script):
        """
        @param script: SFL script.
        This 'set' the stage for evaluating the SFL script. This
        method should be called only once to maximize performance
        (i.e. at the instantiation of the dmine's scrape filter).
        """
        tokens = Lexer.lexer(script)
        Interpreter.parse_tree = Parser(tokens).parse()

    def output():
        """
        @param code: The SFL code.

        Run the SFL code. After the interpreter runs the code and
        evaluate it, a dictionary of components and its boolean value
        will be returned. The boolean value for each component dictates
        whether or not a particular component should be scraped or not.

        For example, if we have the components named `post` and `commment`,
        then this method may return the dictionary 
        
            {'post': True, 'comment': False}

        if the SFL code computed that the post should be scraped while the
        comment component shouldn't be scraped.

        If no code is give (i.e. no filter applied), then all the components
        should be scraped. Any component that does not show up in the filter
        code will automatically be flagged as True.
        """
   
        # Use a clone of the parse tree, since `Evaluator.eval` modifies
        # the parse tree.
        ptree_clone = copy.deepcopy(Interpreter.parse_tree)

        out = Evaluator.eval(ptree_clone, 
                            Interpreter.identifiers,
                            Interpreter.storables)

        # Flag untouched components (identifiers) as True.
        for idn in Interpreter.identifiers:
            is_touched = False
            for sym, val in out:
                if val == idn.name:
                    is_touched = True
                    continue
            if not is_touched:
                out[('identifier', idn.name)] = True

        # Assign untouched variables (storables) with their default
        # values.
        for s in Interpreter.storables:
            is_touched = False
            for sym, val in out:
                if val == s.name:
                    is_touched = True
                    continue
            if not is_touched:
                out[('storable', s.name)] = s.default_value

        return out

    def debug_run(code):
        """
        Debugging purpose.
        """
        # For testing purpose.
        post = Component('post')
        post['title'] = 'This cat is funny'
        post['score'] = 99
        comment = Component('comment')
        comment['body'] = 'No it isn\'t'
        comment['score'] = -19
        idns = [post, comment]

        subreddit = Storable('scan_subreddit', 'all')
        sections = Storable('scan_sections', 'hot,trending,new')
        skip_comments = Storable('skip_comments', False)
        stors = [subreddit, sections, skip_comments]

        tokens = Lexer.lexer(code)
        print('identifiers:\n', idns)
        print('storables:\n', stors)
        print('tokens:\n', tokens)

        parse_tree = Parser(tokens).parse()
        print('===A===')
        print(parse_tree)

        out = Evaluator.eval(parse_tree, idns, stors)
        print('===B===')
        print(parse_tree)

        print('out:', out)

        for idn in idns:
            is_touched = False
            for sym, val in out:
                if val == idn.name:
                    is_touched = True
                    continue
            if not is_touched:
                out[('identifier', idn.name)] = True
        return out

class ParseTree:

    symbol = ''
    value = ''
    parent = None
    children = []
   
    def __init__(self, symbol, value):
        self.parent = None
        self.symbol = symbol
        self.value = value
        self.left = None
        self.right = None
        self.children = []

    """
    Append a new parse tree node that is a child of this
    node, and then return the newly added node.
    """
    def add_child(self, symbol, value):
        new_child = ParseTree(symbol, value)
        new_child.parent = self
        self.children.append(new_child)
        return new_child

    """
    Returns the representation of this ParseTree. It will be a pretty
    printed string.
    """
    def __repr__(self, depth=4):
        lr = ''
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

    # A dictionary where it hold the names and the values of this
    # component's attributes.
    attr_dict = {}

    def __init__(self, name):
        """
        @param name: The name of this component.
        """
        self.name = name
        self.attr_dict = {}
        self.__dict__[self.name] = self.attr_dict

    def has_attr(self, attr):
        return attr in self.attr_dict

    def __setitem__(self, attribute, value):
        self.attr_dict[attribute] = value
        self.__dict__[self.name] = self.attr_dict

    def __getitem__(self, attr):
        return self.attr_dict[attr]

    def __repr__(self):
        return "%s::%s" % (self.name, self.attr_dict)

    def __str__(self):
        return repr(self)

class Storable:
    
    fname = ''
    name = ''
    default_value = ''

    def __init__(self, name, default_value='', prefix='@'):
        """
        @param name: The name of the storable (without prefix).
        @param default_value: The default value of this storable.
        @param prefix: The prefix used to indicate variable.
        """
        self.fname = prefix + name
        self.name = name
        self.default_value = default_value

    def __repr__(self):
        return "(name: %s, val: %s)" % (self.name, self.default_value)

    def __str__(self):
        return repr(self)
