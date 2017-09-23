#
# Author(s): Amirul Menjeni (amirulmenjeni@gmail.com)
#

import re
import math
import sys
import logging
import parser
from enum import Enum, auto

# This class describe the type of value of the component's option.
class ValueType(Enum):
    TIME_COMPARISON = auto()
    INT_RANGE = auto()
    STRING_COMPARISON = auto()
    LIST = auto()

class ScrapComponent:
   
    group = None # The group that contain this scrap component.
    symbol = ''
    name = ''
    info = ''

    # Used name and symbols, kept record to prevent conflict.
    used_names = []
    used_symbols = []

    # @param name: Name of the scrap component.
    # @param symbol: Symbol of the scrap component.
    # @param info: Information about the scrap component.
    def __init__(self, name, symbol=None, info=''):
        self.options = {}

        # Symbol must be an alphabetical character.
        if symbol:
            if len(symbol) != 1 or not symbol.isalpha():
                logging.error(
                    'Scrap option symbol for the option %s::%s '\
                    'must be an alphabet character.' 
                    % (self.name, name)
                )
                sys.exit()
    
        # Prevent name/symbol conflict.
        if name in ScrapComponent.used_names:
            logging.error(
                'The name \'%s\' has already been used.'
                % name
            )
            sys.exit()
        if symbol in ScrapComponent.used_symbols:
            logging.error(
                'The symbol \'%s\' has already been used'
                % symbol
            )
            sys.exit()

        self.symbol = symbol
        self.name = name
        self.info = info

        if self.symbol:
            ScrapComponent.used_symbols.append(self.symbol)
        ScrapComponent.used_names.append(self.name)

    def add_option(self, name, value_type, symbol=None, info=''):
        if symbol:
            if len(symbol) != 1 or not symbol.isalpha():
                logging.error(
                    'Scrap option symbol for the option %s::%s '\
                    'must be an alphabet character.' 
                    % (self.name, name)
                )
                sys.exit()
        opt = ScrapOption(name, value_type, symbol=symbol, info=info)
        opt.set_component(self)
        if symbol:
            self.options[symbol] = opt
        self.options[name] = opt

    def set_group(self, group):
        self.group = group

    def get(self, key):
        try:
            return self.options[key]
        except KeyError:
            logging.error(
                'The scrap component \'%s\' has no option with the name or '\
                'symbol \'%s\'. Please run "dmine -F %s" to '\
                'see the list of available scrap components and their options.'
                % (self.name, key, self.group.spider_name)
            )
            sys.exit()

    def contain(self, component_symbol):
        return (component_symbol in self.options)

class ScrapOption:

    component = None # The component that contain this scrap option.
    symbol = ''
    name = ''
    info = ''
    value = '*'
    value_type = ValueType.STRING_COMPARISON

    def __init__(self, name, value_type, symbol=None, info=''):
        self.symbol = symbol
        self.name = name
        self.value_type = value_type
        self.info = info

    def set_component(self, component):
        self.component = component

    # Get the raw string value of this scrap option. The raw
    # value is the string value that appear in the scrap filter 
    # untouched.
    def raw_value(self):
        val = ''

        # Try to capture the value using this scrap option's symbol.
        # If that doesn't work, try using the name instead.
        try:
            pattern = '(?<=\/%s:)(.*?)(?=(\/[a-zA-Z\-]:|}))' % self.symbol
            val = re.search(pattern, self.component.group.scrap_filter).group(0)
        except AttributeError:
            logging.debug(
                'Unable to find the value of the scrap option '\
                '%s::%s.'
                % (self.component.name, self.name)
            )
            try:
                pattern = '(?<=\/%s:)(.*?)(?=(\/[a-zA-Z\-]:|}))' % self.name
                val = re.search(pattern, self.component.group.scrap_filter)\
                        .group(0)
            except AttributeError:
                raise
    
        return val.strip()
    
    # @param item: The scraped item of type string.
    def should_scrap(self, item):
        # The default is no filter.
        if self.value == '*': 
            return True
        out = Parser.compile(self, item)
        return out
    
class ComponentGroup:
    components = {}
    scrap_filter = ''
    spider_name = ''
    
    def __init__(self, scrap_filter, spider_name=''):
        self.scrap_filter = scrap_filter
        self.spider_name = spider_name

    def add(self, component):
        if component.symbol:
            self.components[component.symbol] = component
        self.components[component.name] = component
        component.set_group(self)

    def get(self, key):
        try:
            return self.components[key]
        except KeyError as e:
            logging.error(
                'No component with the name or symbol \'%s\' exist. '\
                'Please run "dmine -F %s" to see the list '\
                'of available scrap components and their options.'
                % (key, self.spider_name)
            )
            sys.exit()

    # Check if a key (name or symbol) representing a scrap component 
    # exists in this component group.
    def contain(self, key):
        return (key in self.components)

    # Returns a list of scrap components and its options
    # in the form of:
    # my_component_name_1 (my_component_symbol_1):
    #    my_option_name_1 (my_option_symbol_1) [my_option_type_1]
    #    my_option_name_2 (my_option_symbol_2) [my_option_type_2]
    #           .
    #           .
    # .
    # .
    def detail(self):
        lines = ''
        for k in self.components:
            if len(k) != 1:
                name = k
                symbol = self.get(k).symbol
                info = self.get(k).info
                if info != '':
                    info = '\n' + info
                component = '%s (%s):%s\n' % (name, symbol, info)
                lines += component
                for j in self.components[k].options:
                    if len(j) != 1:
                        name = j
                        symbol = self.get(k).get(j).symbol
                        val_type = str(self.get(k).get(j).value_type)
                        val_type = val_type[val_type.find('.') + 1:]
                        info = self.get(k).get(j).info
                        if info == '':
                            info = '(No info available)'
                        option =  '    %s (%s): \n' % (name, symbol)
                        option += '        Value type : %s\n' % val_type
                        option += '        Info       : %s\n' % info
                        lines += option
                lines += '\n'
        return lines

class Parser:
    # @param component_group: The object of type ComponentGroup.
    # This method parse the scrap filter string of the component
    # group and is needed to be called right after all components
    # and their options has been initialized in order for every
    # component to be usable.
    def parse_scrap_filter(component_group):
        # By default, filter_input is set to '*', which means
        # no filter is applied.
        f = component_group.scrap_filter
        if f == '*':
            return None

        r = r'([a-zA-Z-_]+{)?(\/[a-zA-Z-_]+)+'
        m = re.findall(r, f)

        # Check if pattern is valid. The pattern is inferred to be invalid
        # if m is empty or when either position in the m[0] tuple is 
        # an empty string ('').
        if not m or (m[0][0] == '' or m[0][1] == ''):
            logging.error('Invalid filter pattern: %s', filter_input)
            sys.exit()
        
        components = {}

        # Temp vars.
        temp_key = ''
        temp_val = []

        # Populating the components dict.
        # Note: t is a 2-tuple containing the pattern ('p{', '/t')
        # where p and t is the component symbol and option symbol
        # respectively. Thus, t[0][0] represent the component symbol,
        # and t[1][1] represent the option symbol.
        for t in m:
            tuple_com = t[0][:-1]
            tuple_opt = t[1][1:]
            if t[0] is not '':
                temp_component = component_group.get(tuple_com)
                opt = temp_component.get(tuple_opt)
                opt.value = opt.raw_value()
                components.update({
                    (tuple_com, tuple_opt): opt.value
                })
                temp_key = tuple_com
            else:
                if not Parser.is_option_exist(component_group, temp_key, 
                                              tuple_opt):
                    continue
                opt = temp_component.get(tuple_opt)
                opt.value = opt.raw_value()
                components.update({
                    (temp_key, tuple_opt): opt.value
                })
        logging.info('components: %s' % components)

    def compile(scrap_option, scrap_target):
        x = scrap_target
        expr = ""

        # Subtitute the scrap option's name or symbol with
        # x to allow using name/symbol as placeholder
        # instead of x.
        opt_symb = scrap_option.symbol
        opt_name = scrap_option.name
        if re.match('\ ?%s\ ?' % opt_name, scrap_option.value):
            print('replacing symbol')
            scrap_option.value = scrap_option.value.replace(opt_name, 'x')
        elif re.match('\ ?%s\ ?' % opt_symb, scrap_option.value):
            print('replacing name')
            scrap_option.value = scrap_option.value.replace(opt_symb, 'x')

        expr = expr.replace(scrap_option.name, 'x')
        # Ensure that the scrap option's value and its target
        # is valid according to the value type set for the
        # scrap option.
        if not Parser.is_value_valid(scrap_option) or\
           not Parser.is_target_valid(scrap_option, scrap_target):
            logging.error(
                'The scrap option %s::%s have invalid value or scrap target.'\
                % (scrap_option.component.name, scrap_option.name)
            )
            sys.exit()

        # Parse the scrap target to its supposed data type
        # to conduct boolean comparison operation for filtering.
        if scrap_option.value_type == ValueType.TIME_COMPARISON:
            # Dictionary of scrap target's value.
            v = scrap_target.split(' ')
            target_time = {
                'y': 0, 'M': 0, 'd': 0,
                'h': 0, 'm': 0, 's': 0
            }
            for u in v:
                target_time[u[-1]] = int(u[:-1])

            # Dictonary of scrap option's value.
            v = scrap_option.value.split(' ')
            value_time = {
                'y': 0, 'M': 0, 'd': 0,
                'h': 0, 'm': 0, 's': 0
            }
            for u in v:
                value_time[u[-1]] = int(u[:-1])

            # Conversion from the given time units to seconds.
            secs = {
                'y': 365 * 24 * 60 * 60,
                'M': 30 * 24 * 60 * 60,
                'd': 24 * 60 * 60,
                'h': 60 * 60,
                'm': 60,
                's': 1
            }

            # Convert both target and option value to seconds
            # to be compared.
            scrap_target_secs = 0
            for k in target_time:
                scrap_target_secs += target_time[k] * secs[k]
            scrap_value_secs = 0
            for k in value_time:
                scrap_value_secs += value_time[k] * secs[k]

            if scrap_target_secs <= scrap_value_secs:
                expr = "True"
            else:
                expr = "False"

        if scrap_option.value_type == ValueType.INT_RANGE:
            x = int(x)
            expr = scrap_option.value

        if scrap_option.value_type == ValueType.STRING_COMPARISON:
            x = str(x)
            expr = scrap_option.value

        if scrap_option.value_type == ValueType.LIST:
            x = scrap_option.value.split(',')
            expr = str(x)
            print('list expr:', expr)
        
        #
        # Use python parser to parse and compile the string.
        #
        code = parser.expr(expr).compile()
        try:
            parsed_expr = eval(code)
        except NameError as e:
            unknown_var = re.search('name \'(.*)\' is not defined', str(e))\
                            .group(1)
            logging.error(
                'Unknown variable \'%s\' in the expression \'%s\'. '\
                'Please change the variable name to %s.'\
                % (unknown_var, scrap_option.value, scrap_option.name)
            )
            sys.exit()
        return parsed_expr

    # Compute whether or not the target (item string scraped)
    # meet the expectation of the value type of the scrape option
    # it is tested with.
    def is_target_valid(scrap_option, scrap_target):
        com_name = scrap_option.component.name
        opt_name = scrap_option.name
        val_type = scrap_option.value_type

        if scrap_option.value_type == ValueType.TIME_COMPARISON:
            return Parser.validate_int_range(scrap_option, scrap_target)

        if scrap_option.value_type == ValueType.INT_RANGE:
            if not scrap_target.isdigit():
                logging.error(
                    'The scrap option %s::%s have value type %s, '
                    'but the scrap target is not an integer.'\
                    % (com_name, opt_name, val_type)
                )
                return False

        if scrap_option.value_type == ValueType.STRING_COMPARISON:
            if not isinstance(scrap_target, str):
                logging.error(
                    'The scrap option %s::%s have value type %s, '\
                    'but the scrap target is not a string.'\
                    % (com_name, opt_name, val_type)
                )
                return False
        
        if scrap_option.value_type == ValueType.LIST:
            if not isinstance(scrap_target, str):
                logging.error(
                    'The scrap option %s::%s have value type %s, '\
                    'but the scrap target is not a string.'\
                    % (com_name, opt_name, val_type)
                )
                return False

        return True

    # Compute whether or not the value of the scrap option
    # meet the expectation of the value type it is given.
    def is_value_valid(scrap_option):
        com_name = scrap_option.component.name
        opt_name = scrap_option.name
        val_type = scrap_option.value_type

        if scrap_option.value_type == ValueType.TIME_COMPARISON:
            return Parser.validate_int_range(scrap_option, scrap_option.value)

        if scrap_option.value_type == ValueType.INT_RANGE:
            # This regex expression test for string expressions
            # for comparing numbers (inequality and equality).
            p = r'(((\d+\ *\<=*)*\ *x\ *\<=*\ *\d+)'\
                '|(\d+\ *\<=*\ *x\ *(\<=*\ *\d+)*)'\
                '|((\d+\ *\>=*)*\ *x\ *\>=*\ *\d+)'\
                '|(\d+\ *\>=*\ *x\ *(\>=*\ *\d+)*)'\
                '|(x\ *==\ *\d+)'\
                '|(\d+\ *==\ *x))'
            if not re.match(p, scrap_option.value):
                logging.error(
                    'The scrap optioon %s::%s have value type %s, '\
                    'but the scrap option value is not an integer comparison '\
                    'operation. (Value: "%s")'
                    % (com_name, opt_name, val_type, scrap_option.value)
                )
                return False

        if scrap_option.value_type == ValueType.STRING_COMPARISON:
            pattern = 'x\ (==|!=|(not )?in) .+'
            m = re.match(pattern, scrap_option.value)
            if not m:
                logging.error(
                    'The scrap option %s::%s have value type %s, '\
                    'but the scrap option value is not a string comparison '\
                    'operation. (Value: "%s")'
                    % (com_name, opt_name, val_type, scrap_option.value)
                )
                return False

        if scrap_option.value_type == ValueType.LIST:
            pattern = '([a-zA-Z0-9-_ ]+)(,\s*[a-zA-Z0-9-_ ]+)*'
            m = re.match(pattern, scrap_option.value)
            if len(m.group(0)) != len(scrap_option.value):
                logging.error(
                    'The scrap option %s::%s have the value type %s, '\
                    'but the scrap option value is not a comma separated '\
                    'list.'
                )
                return False

        return True

    def validate_int_range(scrap_option, string):
        d = string.split(' ')
        com_name = scrap_option.component.name
        opt_name = scrap_option.name
        val_type = scrap_option.value_type

        # Dict keeping record which unit has been used.
        unit_instance = {
            'y': False, 'M': False, 'd': False,
            'h': False, 'm': False, 's': False
        }

        for i in d:
            if re.match(r'^\d+[yMdhms]{1}$', i):
                if unit_instance[i[-1]]:
                    logging.warning(
                        'Scrap component %s::%s: '\
                        'Multiple instance of time with the unit \'%s\' '\
                        'in "%s". Last occurence of the instance will be '\
                        'used.'\
                        % (com_name, opt_name, i[-1], scrap_option.value)
                    )
                else:
                    unit_instance[i[-1]] = True
            else:
                logging.error(
                    'The scrap option %s::%s have value type %s, '\
                    'but the scrap option value or scrap target'\
                    ' does not meet the pattern requirement.'\
                    % (com_name, opt_name, val_type)
                )
                return False
            if int(i[:-1]) < 0:
                logging.error(
                    'Scrap option %s::%s: '\
                    'The amount of time passed can not be negative.'\
                    % (com_name, opt_name)
                )
                return False
        return True

