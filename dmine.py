# Author(s): Amirul Menjeni, amirulmenjeni@gmail.com
#
# Dmine module.
# 

import sys
import logging
import json
import re
import enum
from abc import ABCMeta, abstractmethod

###############################################################################
# Classes
###############################################################################

# The types of expected and valid input for each instance of an
# Input class.
class InputType(enum.Enum):
    BOOLEAN = enum.auto()
    INTEGER = enum.auto()
    STRING = enum.auto()

# Takes in input for a particular spider.
class InputGroup:
    inputs = {}
    input_string = ''
    spider_name = ''
    
    def __init__(self, input_string, spider_name=''):
        self.inputs = {}
        self.input_string = input_string
        self.spider_name = spider_name

    def add_input(self, input_obj):
        if input_obj.symbol:
            self.inputs[input_obj.symbol] = input_obj
        self.inputs[input_obj.name] = input_obj

    def get(self, key):
        try:
            return self.inputs[key]
        except KeyError:
            logging.error(
                'There is no input with the name or symbol \'%s\'. '\
                'Please run "dmine -I %s" to see the list of available '\
                'input for this spider.'
                % (key, self.spider_name)
            )
            sys.exit()

    def detail(self):
        lines = ''
        for k in self.inputs:
            if len(k) > 1:
                name = k
                symbol = self.get(k).symbol
                val = self.get(k).val()
                info = self.get(k).info
                input_type = str(self.get(k).input_type)
                input_type = input_type[input_type.find('.') + 1:]
                lines += '%s (%s):\n' % (name, symbol)
                lines += '    Input type    : %s\n' % input_type
                lines += '    Default value : %s\n' % val
                lines += '    Info          : %s\n' % info
        return lines

class Input:
    name = ''
    symbol = ''
    value = None
    default_value = None
    info = ''
    input_type = InputType.STRING

    used_symbols = []
    used_names = []
    
    def __init__(self, name, input_type, default=None, symbol=None, info=''):
        if name in Input.used_names:
            longging.error(
                'The input name \'%s\' has been used.'
                % name
            )
            sys.exit()
        if symbol and (symbol in Input.used_symbols):
            longging.error(
                'The input symbol \'%s\' has been used.'
                % symbol
            )
            sys.exit()

        self.name = name
        self.symbol = symbol
        self.value = ''
        self.default_value = default
        self.input_type = input_type
        self.info = info
       
        Input.used_names.append(self.name)
        Input.used_symbols.append(self.symbol)

    def val(self):
        return self.compile()

    # Validate the input type. If the input is correct with
    # respect to its input type, then parse to its type (if needed)
    # and return it. Otherwise, throw an error.
    def compile(self):
        if not self.value:
            self.value = self.default_value

        # If the default value is None, then just return it.
        if not self.value:
            return self.value

        # Process input according to its defined input type.
        val = self.value
        if self.input_type == InputType.BOOLEAN:
            if val not in ['True', 'False', '1', '0']:
                logging.error(
                    'The input type for \'%s\' is %s, but the value given '\
                    'is not a boolean. Accepted value for this input is '\
                    'either True, False, 1, or 0.'
                    % (self.name, self.value_type)
                )
                sys.exit()
        if self.input_type == InputType.INTEGER:
            if not val.isdigit():
                logging.error(
                    'The input type for \'%s\' is %s, but the value given '\
                    'is not an integer.'
                    % (self.name, self.value_type)
                )
                sys.exit()
            val = int(val) 

        return val

# This class describe the type of value of the component's option.
class ValueType(enum.Enum):
    TIME_COMPARISON = enum.auto()
    INT_RANGE = enum.auto()
    STRING_COMPARISON = enum.auto()
    LIST = enum.auto()

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
    #
    # The symbol must be an alphabetical character, and the name
    # must consists of more than one characters.
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

        if len(name) <= 1:
            logging.error(
                'Scrap option name for the option %s::%s '\
                'must consist of more than 1 characters.'
                % (self.name, name)
            )
            sys.exit()

        self.symbol = symbol
        self.name = name
        self.info = info

        if self.symbol:
            ScrapComponent.used_symbols.append(self.symbol)
        ScrapComponent.used_names.append(self.name)

    # @param name: Name of the scrap option.
    # @param value_type: The value type of the scrap option.
    #                    See ValueType class.
    # @param symbol: The symbol used for shorthand reference of this
    #                scrap option.
    # @param info: Developer defined info about the scrap option.
    #
    # The symbol must be an alphabetical character, while the name
    # must have more than 1 character.
    def add_option(self, name, value_type, symbol=None, info=''):
        if symbol:
            if len(symbol) != 1 or not symbol.isalpha():
                logging.error(
                    'Scrap option symbol for the option %s::%s '\
                    'must be an alphabet character.' 
                    % (self.name, name)
                )
                sys.exit()
        if len(name) <= 1:
            logging.error(
                'Scrap option name for the option %s::%s '\
                'must consist of more than 1 characters.'
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

    # Should this component be scraped, based on user's
    # scrap filter?
    def should_scrap():
        for k in self.options:
            if len(k) > 1:
                pass

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
        if component.symbol in self.components:
            loggging.error(
                'A component with the symbol %s already exists.'
                % component.symbol
            )
            sys.exit()
        if component.name in self.components:
            loggging.error(
                'A component with the name %s already exists.'
                % component.symbol
            )
            sys.exit()

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

    # Populate a spider input with values as extracted
    # from the spider input string it's given.
    def parse_input_string(spider_input):
        logging.info('spider_input: %s' % spider_input)
        if not spider_input.input_string:
            logging.info(
                'No spider input string was given. All '\
                'spider inputs will use its default value.'
            )
            return None
    
        s = spider_input.input_string
        pattern = r'\/([a-zA-Z-_]+):'
        input_names = re.findall(pattern, s)
        for input_name in input_names:
            pattern = r'(?<=\/%s:)(.*?)(?=\/[a-zA-Z-_]+:|$)' % input_name
            input_value = re.findall(pattern, s)[0]
            spider_input.get(input_name).value = input_value.strip()

    def compile(scrap_option, scrap_target):
        x = scrap_target
        expr = ""

        # Subtitute the scrap option's name or symbol with
        # x to allow using name/symbol as placeholder
        # instead of x.
        opt_symb = scrap_option.symbol
        opt_name = scrap_option.name
        if re.match('\ ?%s\ ?' % opt_name, scrap_option.value):
            scrap_option.value = scrap_option.value.replace(opt_name, 'x')
        elif re.match('\ ?%s\ ?' % opt_symb, scrap_option.value):
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

class Utils:
    # @param item: The item to append to the a file.
    # @param filename: The filename of the file.
    #
    # If no filename is specified, then print to stdout.
    # Otherwise, print to specified file. The default output
    # format is JSON.
    def to_file(item, filename=None, file_format='json'):
     
        # Store in JSON format.
        if file_format == 'json':
            if filename:
                with open(filename, 'w') as f:
                    for i in item:
                        json_str = json.dumps(i)
                        f.write(json_str)
            else:
                for i in item:
                    json_str = json.dumps(i)
                    sys.stdout.write(json_str)

        # Store in CSV format.
        elif file_format == 'csv':
            if filename:
                with open(filename, 'w') as f:
                    f.write(keys)
                    for i in item:
                        row = ','.join(list(i.values()))
                        f.write(row)
            else:
                for i in item:
                    row = ','.join(['\"' + v + '\"' for v in list(i.values())])
                    sys.stdout.write(row)

# This is an abstract class. All spider that runs on dmine should
# inherit this class.
class Spider:
    __metaclass__ = ABCMeta 
    component_group = None
    input_group = None
    name = ''
    args = None

    # Initialize the spider class. When a spider object
    # is called to be initialized, its name attribute is
    # checked for duplicate with other spider object.
    def __init__(self):
        component_group = None
        input_group = None
        name = ''
        args = None

        # Check for duplicate name.
        for c in Spider.__subclasses__():
            class_name = self.__class__.__name__
            if (c.name == self.name) and (c.__name__ != class_name):
                logging.error(
                    'There\'s already a spider  with the name \'%s\'. '
                    'Spider '\
                    'names must be unique. Please change the name of the '\
                    'miner in the class \'%s\' into something else.'
                    % (self.name, self.__class__.__name__)
                )
                sys.exit()

    # This method must be defined by the child classes
    # to define their scrap filter component group.
    @abstractmethod
    def setup_filter(component_group):
        # TODO
        # Overwritten by inheritor. 
        # Spider dev define his scrap filter here.
        pass

    @abstractmethod
    def setup_input(input_group):
        # TODO
        # Overwritten by inheritor.
        # Spider dev define his spider input here.
        pass
    
    # This shouldn't be overwritten.
    def run_parsers(self):
        Parser.parse_scrap_filter(self.component_group)
        Parser.parse_input_string(self.spider_input)
