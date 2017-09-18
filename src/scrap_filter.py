#
# Author(s): Amirul Menjeni (amirulmenjeni@gmail.com)
#
# e.g.
# dmine -f 'p{/t:trump,islam/c:hello/r:200-300/a:49m/g:nsfw} c{/u:spez}'
#
# Explanation:
#   Scrap component refers to general things found in the site that are to be
#   scrapped such as posts, users, and comments. Each component have its own
#   options. For example one can create a component called post, symbolized
#   as p, and look for the post with the title (symbolized as t) containing 
#   the word 'awesome' and fun', or 'colour', but not 'gore'. Thus, the scrap 
#   filter for this would be 'p{%t:awesome^fun,colou?r,!gore}'. Note that 
#   we use can use regex expression to look for the word colour/color. In other
#   words, dmine will only scrap the post (p) that where its title contains
#   the words awesome AND fun, or colou?r. But it will ignore the word gore. 

import re
import math
import sys
import logging
import parser
from enum import Enum, auto

# This class describe the type of value of the component's option.
class ValueType(Enum):
    SINGLE_STRING = auto()
    INT_RANGE = auto()
    WORD_FILTER = auto()
    COMMA_SEPARATED_LIST = auto()
    DATE_TIME = auto()
    BOOLEAN = auto()

class ScrapComponent:
   
    group = None # The group that contain this scrap component.
    symbol = ''
    name = ''
    options = {}

    def __init__(self, symbol, name):
        if len(symbol) != 1 or not symbol.isalpha():
            logging.error('Scrap component symbol for the component \'%s\' '\
                          'must be an alphabet character.' % name)
            sys.exit()

        self.symbol = symbol
        self.name = name

    # To access the option:
    #   my_scrap_component.get('p') will return the value
    def add_option(self, symbol, name, value_type):
        if len(symbol) != 1 or not symbol.isalpha():
            logging.error('Scrap option symbol for the option \'%s\' '\
                          'must be an alphabet character.' % name )
            sys.exit()
        opt = ScrapOption(symbol, name, value_type)
        opt.set_component(self)
        self.options.update({
            symbol: opt
        })

    def set_group(self, group):
        self.group= group

    def get(self, symbol):
        return self.options[symbol]

    def contain(self, component_symbol):
        return (component_symbol in self.options)

class ScrapOption:

    component = None # The component that contain this scrap option.
    symbol = ''
    name = ''
    value = ''
    value_type = ValueType.SINGLE_STRING

    def __init__(self, symbol, name, value_type):
        self.symbol = symbol
        self.name = name
        self.value_type = value_type

    def set_component(self, component):
        self.component = component

    def get_value(self):
        pattern = '(?<=\/%s:)(.*?)(?=(\/[a-z]:|}))' % self.symbol
        val = re.search(pattern, self.component.group.scrap_filter).group(0)
        return val
    
    def parse(self):
        if not self.component:
            logging.error('The scrap option named %s is not assigned to a '\
                          'component.' % self.name)
            sys.exit()
        if not self.value:
            logging.error('The scrap option named %s have no value assigned.'\
                          % self.name)
            sys.exit()
        logging.info('Parsing...')
        logging.info('value: %s, type: %s' % (self.value, self.value_type))
        return Parser.parse_option_value(self.value_type, self.value)

    def should_scrape(item):
        out = False
        if self.type == ValueType.BOOLEAN:
            pass
        elif self.type == ValueType.WORD_FILTER:
            pass
        elif self.type == ValueType.INT_RANGE:
            pass
        elif self.type == ValueType.DATE_TIME:
            pass
        return out

class ComponentGroup:
    components = {}
    scrap_filter = ''
    
    def __init__(self, scrap_filter):
        self.scrap_filter = scrap_filter

    def add(self, component):
        self.components.update({
            component.symbol: component
        })
        component.set_group(self)

    def get(self, component_symbol):
        return self.components[component_symbol]

    # Check if a component_symbol representing a scrap component 
    # exists in this component group.
    def contain(self, component_symbol):
        return (component_symbol in self.components)

class Parser:
    # Returns a dictionary of scrap components. For example,
    # the scrap filter shown as 
    # p{/t:awesome^fun,colou?r,!gore/g:nsfl} c{/t:lol,me^too^thanks}
    # will return the dictionary { p: [t, g], c: [t] }, where the keys
    # p and c are the scrap components, and the lists [t, g] and [t] are
    # their corresponding scrap options.
    #
    # @param component_group: The object of type ComponentGroup.
    # @param filter_input: Filter input syntax a{/a:...,.../b:...} b{/a:..}
    def parse_scrap_filter(component_group):
        # By default, filter_input is set to '*', which means
        # no filter is applied.
        f = component_group.scrap_filter
        if f == '*':
            return None

        r = r'([a-z]{)?(\/[a-z]{1})+'
        m = re.findall(r, f)

        # Check if pattern is valid. The pattern is inferred to be invalid
        # if m is empty or when either position in the m[0] tuple is 
        # an empty string ('').
        if not m or (m[0][0] == '' or m[0][1] == ''):
            logging.error('Invalid filter pattern: %s', filter_input)
            sys.exit()

        # This is a dict where the keys are the component symbols and
        # their values are the option symbols contained by each component.
        components = {}
        # This is a dict where the keys are the component and option symbols
        # concatenated with '::' between them. The values are their parsed
        # value used for filtering scraping selections.
        options = {}

        # Temp vars.
        temp_key = ''
        temp_val = []
        temp_component = None

        logging.info('m: %s', m)

        # Populating the components dict.
        # Note: t is a 2-tuple containing the pattern ('p{', '/t')
        # where p and t is the component symbol and option symbol
        # respectively. Thus, t[0][0] represent the component symbol,
        # and t[1][1] represent the option symbol.
        for t in m:
            if t[0] is not '':
                if not Parser.is_component_exist(component_group, t[0][0]):
                    continue
                if not Parser.is_option_exist(component_group,
                                              t[0][0], t[1][1]):
                    continue
                temp_component = component_group.get(t[0][0])
                opt = temp_component.get(t[1][1])
                opt.value = opt.get_value()
                parsed_value = opt.parse()
                components.update({
                    (t[0][0], t[1][1]): parsed_value
                })
                temp_key = t[0][0]
            else:
                if not Parser.is_option_exist(component_group, temp_key, 
                                              t[1][1]):
                    continue
                opt = temp_component.get(t[1][1])
                opt.value = opt.get_value()
                parsed_value = opt.parse()
                components.update({
                    (temp_key, t[1][1]): parsed_value
                })
        logging.info('components: %s' % components)

        out = {}
        for com, opt in components.items():
            pass
        return components

    def is_component_exist(component_group, component_symbol):
        # Ignore non-existent scrap component.
        if not component_group.contain(component_symbol):
            logging.warning(
                'The scrap component with the symbol %s '\
                'does not exist. This scrap component will '\
                'be ignored.' % component_symbol
            )
            return False
        return True

    def is_option_exist(component_group, component_symbol, option_symbol):
        # Ignore non-existent scrap option in this scrap component.
        if not component_group.get(component_symbol)\
                .contain(option_symbol):
            logging.warning(
                'The scrap component \'%s\' does not contain '\
                'the scrap option \'%s\'. This scrap option '\
                'will be ignored.' % (component_symbol, option_symbol)
            )
            return False
        return True

    def parse_option_value(value_type, value):
        if value_type == ValueType.SINGLE_STRING:
            return value
        elif value_type == ValueType.INT_RANGE:
            return Parser.parse_int_range(value)
        elif value_type == ValueType.COMMA_SEPARATED_LIST:
            return Parser.parse_comma_separated_list(value)
        elif value_type == ValueType.WORD_FILTER:
            return Parser.parse_word_filter(value)
        else:
            logging.warning('Invalid value type: %s', value_type)

    def parse_int_range(value):
        x = 0 # Init. variable called x.
        code = parser.expr(value).compile()
        try:
            parsed_expr = eval(code)
        except NameError as e:
            unknown_var = re.search('name \'(.*)\' is not defined', str(e))\
                            .group(1)
            logging.error(
                'Unknown variable \'%s\' in the expression \'%s\'. '\
                'Please change the variable name to \'x\''\
                % (unknown_var, value)
            )
            sys.exit()

        # Test if the expression 'value' is an inequality
        # (or equality).
        if not isinstance(parsed_expr, bool):
            logging.error('The value for ValueType.INT_RANGE must be a boolean'
                          ' expression e.g. "x == 100" or "x < 5"')
            sys.exit()
        return value

    # Return a list of words to be search from a comma separated
    # value.
    def parse_comma_separated_list(value):
        return value.split(',')

    # @param value: The value is a string delimited by comma (',').
    #               Each delimited item is either a single string,
    #               a multiple strings join with ^, and a negation
    #               of a single string.
    #
    # Suppose we have the scrap filter f = 'p{/t:cat^really shocked,very funny,
    # ~grave injury,~repost}', and the component t is of type WORD_FILTER. 
    # Then, the scraper will retrieve any component t which contains  both the 
    # strings 'cat' and 'really shocked', or any which contains the string 
    # 'very funny'. Any component which contain at least one string prefixed
    # with ~ will not be retrieved. Thus, if any component t contains the 
    # string 'grave injury' or 'repost', it will not be retrieved.
    def parse_word_filter(value):
        logging.info('Parsing value type: %s' % ValueType.WORD_FILTER)
        items = value.split(',') 
        return items
