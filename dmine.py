# Author(s): Amirul Menjeni, amirulmenjeni@gmail.com
#
# Dmine module.
# 

import os
import sys
import time
import datetime
import logging
import time
import json
import jsonlines
import re
import enum
import parser
from sfl import Interpreter
from abc import ABCMeta, abstractmethod

class Component:
    """
    WARNING: This class isn't supposed to be instantiated outside
             the class `ScrapFilter`.

    This class defines a component that can be found in a target site.
    For example, a user submission, a user profile, and a comment can
    be manifested as a component. Each component its attribute(s). 
    Attributes are defined in the class `Attribute`.
    """
   
    scrape_filter  = None # The scrape filter 
                          # that contain this scrap component.
    name = ''
    info = ''
    attr = {}
    flag = False

    def __init__(self, scrape_filter, name, info=''):
        """
        @param name: The unique name of the component.
        @param info: Information about the component.

        Create an instance of the `Component` class.
        """
        if not ScrapeFilter.is_name_valid(name):
            ScrapeFilter.throw_invalid_name_error(name)

        self.scrape_filter = scrape_filter
        self.name = name
        self.info = info
        self.attr = {}
        self.flag = False

    def add(self, name, info=''):
        """
        @param name: The name of the attribute.
        @param info: The information about the attribute.

        Add an attribute to this component.
        """
        
        if name in self.attr:
            self.__throw_attr_name_error(name)
    
        self.attr[name] = Attribute(self, name, info)

    def get(self, name):
        """
        @param name: The name of the attribute to get.
        """
        try:
            return self.attr[name]
        except KeyError:
            self.__throw_get_attr_error(name)

    def should_scrape(self):
        self.scrape_filter.run_interpreter()
        return self.flag

    def set_attr_values(self, **attributes):
        """
        @param **attributes: A dictionary of attributes where the attribute's
                             name is the key and its attribute value is 
                             the value corresponding to the dictionary key.
        """
        for k in attributes:
            self.get(k).value = attributes[k]

    def __throw_attr_name_error(self, name):
        msg = 'An attribute in the component \'%s\' with '\
              'the name \'%s\' already exists.'\
              % (self.name, name)
        logging.error(msg)
        raise ValueError(msg)

    def __throw_get_attr_error(self, name):
        msg = 'The component \'%s\' has no attribute with the name \'%s\''\
               % (self.name, name)
        logging.error(msg)
        raise KeyError(msg)

class Attribute:
    """
    WARNING: This class isn't supposed to be instantiated outside the
             `Component` class.

    This class defines an attribute of a component. See `Component` class.
    """ 

    component = None
    name = ''
    info = ''
    value = None

    def __init__(self, component, name, info=''):
        """
        @param name: The name of this attribute.
        @param info: The information pertaining this attribute.

        Create an instance of `Attribute` class.
        """
        if not ScrapeFilter.is_name_valid(name):
            ScrapeFilter.throw_invalid_name_error(name)

        self.component = component
        self.name = name
        self.info = info
        self.value = None

class Variable:
    """
    WARNING: This class isn't supposed to be instantiated outside the 
             `ScrapeFilter` class.

    This class defines an argument variable (or just called as variables or
    storables in SFL).
    """

    scrape_filter = None
    name = ''
    info = ''
    type = str
    value = None
    default_value = None

    def __init__(self, scrape_filter, name, type=str, default=None, info=''):
        """
        @param scrape_filter: The scrape filter object that is used
                              to define this variable from.
        @param name: The variable name.
        @param type: The type of the variable. By default, the variable
                     type is a string. This can also be a function that
                     that takes in the value of this variable to make this
                     variable's value the output of the given function.
        @param defval: The default value of this variable. By default, this is
                       set to None.
        @param info: The information pertaining this variable.
        """
        self.scrape_filter = scrape_filter
        self.name = name
        self.type = type
        self.value = None
        self.default_value = default
        self.info = info

    def __to_type(self, value):
        """
        @param value: The value of the variable.

        Convert a given variable's value to its specified type.
        """
        if self.type == bool:
            print('type bool:', value)
            if value in (1, 'True'):
                return True
            elif value in (0, 'False'):
                return False
            else:
                Variable.__throw_type_error(self.name, value, self.type)
        return self.type(value) 

    def __throw_type_error(name, value, type):
        msg = 'Invalid value for the type %s of variable \'%s\': %s'\
              % (type, name, value)
        logging.error(msg)
        raise TypeError(msg)

    def set_value(self, value):
        self.value = self.__to_type(value)

class ScrapeFilter:
    """
    The scrap filter contains several components that can be found in the
    target site that is to be scraped. It is from the object of this class
    that the components are created.
    """

    comp = {}
    spider_name = ''
    sfl_input = ''
    var = {}
    
    def __init__(self, sfl_script, spider_name=''):
        """
        @param sfl_script: The scrape filter language script.
        @param spider_name: The name of the spider that employ this scrape
                            filter.

        Create an instance of `ScrapFilter` class.
        """
        self.spider_name = spider_name
        self.sfl_input = sfl_script
        self.var = {}
        Interpreter.set(sfl_script)

    def add_com(self, name, info=''):
        """
        @param name: The name of the component.
        @param info: The information pertaining the component.

        Add a new component to this scrape filter.
        """
        if name in self.comp:
            ScrapeFilter.__throw_comp_name_error(name)
        self.comp[name] = Component(self, name, info)

    def add_var(self, name, type=str, default='', info=''):
        """
        @param name: The name of the variable.
        @param defval: The default value assigned to the variable.
        @param info: The information pertaining the variable.

        Add a new variable to this scrape filter.
        """
        if name in self.var:
            msg = 'The variable name \'%s\' already exist.' % name
            ScrapeFilter.__throw_error(msg)
        self.var[name] = Variable(self, name, type, default, info)

    def is_name_valid(name):
        """
        @param name: The name of a component or attribute.

        The name of a component or an attribute can contain only
        any alphabetical, numerical characters and underscores,
        but its first character must not be numeric.

        This method returns True if the name pattern match with the
        above description. Otherwise, this method will return false.

        """
        return re.match('^[_a-zA-Z][_a-zA-Z0-9]+$', name)

    def __throw_error(msg):
        logging.error(msg)
        raise KeyError(msg)

    def __throw_not_exist_error(symbol, name):
        msg = 'No %s named \'%s\' exist.' % (symbol, name)
        ScrapeFilter.__throw_error(msg)

    def throw_invalid_name_error(name):
        msg = 'The of the component or attribute \'%s\' is invalid.' % name
        ScrapeFilter.__throw_error(msg)

    def get(self, name):
        """
        @param name: The name of the component to get.

        Returns a component with the name `name`. If the name doesn't
        exists, an error will be thrown.
        """
        try:
            return self.comp[name]
        except:
            ScrapeFilter.__throw_not_exist_error('component', name)

    def ret(self, name):
        """
        @param name: The name of the variable to get.

        Returns a variable with the given name. If the name doesn't
        exists, an error will be thrown.
        """
        try:
            return self.var[name].value
        except:
            ScrapeFilter.__throw_not_exist_error('variable', name)

    def run_interpreter(self):
        """
        Run the SFL interpreter. All the definitions of components
        and variables are defined from this scrape filter. We just
        need to feed the interpreter this scrape filter, and get
        its output.
        """
        Interpreter.feed(self)
        sfl_output = Interpreter.output()
        print('sfl out:', sfl_output)
        for key in sfl_output:
            sym, name = key 
            val = sfl_output[key]
            if sym == 'storable':
                self.var[name].set_value(val)
            elif sym == 'identifier':
                self.comp[name].flag = val
            else:
                msg = 'Unknown token symbol: %s' % sym
                logging.error(msg)
                raise ValueError(msg)

    def detail(self):
        """
        Returns a multiline string that represents the components and
        its attributes, as well as the variables created in this 
        scrape filter.
        """
        lines = ''
        lines += 'COMPONENTS:\n\n'
        for k in self.comp:
            name = k
            info = self.get(k).info
            component = ' %s: %s\n' % (name, info)
            lines += component
            for j in self.comp[k].attr:
                if len(j) != 1:
                    name = j
                    info = self.get(k).get(j).info
                    if info == '':
                        info = '(No info available)'
                    attribute =  '     %s: %s\n' % (name, info)
                    lines += attribute
            lines += '\n'

        lines += 'ARGUMENT VARIABLES:\n\n'
        for k in self.var:
            name = k
            info = self.var[k].info
            variable = ' %s: %s\n' % (name, info)
            lines += variable
        return lines

class Utils:
    """
    This class contains utility methods, and should not be instantiated.
    """

    # @param data: The dict to write to the file.
    # @param filename: The filename of the file.
    # @param file_format: The format the data is written into the file.
    #
    # If no filename is specified, then print to stdout.
    # Otherwise, print to specified file. The default output
    # format is JSON.
    def dict_to_file(data, filename=None, file_format='json'):

        # Store in JSON format.
        if file_format == 'json':
            if filename:
                with open(filename, 'a') as f:
                    s = json.dumps(data)
                    f.write(s)
            else:
                s = json.dumps(data)
                sys.stdout.write(s)

        # Store in JSONL format.
        if file_format == 'jsonl':
            if filename:
                with jsonlines.open(filename, mode='a') as w:
                    w.write(data)
            else:
                s = json.dumps(data)
                sys.stdout.write(s + '\n')

        # Store in CSV format.
        elif file_format == 'csv':
            if filename:
                with open(filename, 'a') as f:
                    row = ','.join(list(data.values()))
                    f.write(row)
            else:
                row = ','.join(['\"' + v + '\"' for v in list(data.values())])
                sys.stdout.write(row)

    # @param component_loader: A component loader object.
    # @param out_dir: The directory location in which to put the
    #                 written files for each component.
    # @param file_format: The format in which the data is stored.
    #
    # If the path `out_dir` doesn't exists, create the directory path
    # and store the data file for each scraped components to `out_dir`.
    # The name of each file should have a basename corresponding
    # to `component_loader.name`, and its extension should be
    # `file_format`.
    def component_loader_to_file(\
            component_loader, out_dir, file_format='json'\
        ):
        
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        path = os.path.realpath(out_dir)

        file_path = path + '/' + component_loader.name + '.' + file_format
        data = component_loader.data
        
        if file_format == 'json':
            with open(file_path, 'a') as f:
                s = json.dumps(data)
                f.write(s)

        elif file_format == 'jsonl':
            with open(file_path, 'a') as f:
                s = json.dumps(data)
                f.write(s + '\n')

# This is an abstract class. All spider that runs on dmine should
# inherit this class.
class Spider:
    __metaclass__ = ABCMeta 
    name = ''
    args = None

    def __init__(self):
        """
        Initialize the spider class. When a spider object (which inherits
        this class) is initialized, its name attribute is checked whether
        its name is unique or not.
        """
        self.scrape_filter = None
        self.input_group = None
        self.name = ''
        self.args = None

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
                raise

    @abstractmethod
    def setup_filter(self, scrape_filter):
        # TODO
        # Overwritten by inheritor.
        # Spider dev define scrape filter here.
        pass

    @abstractmethod
    def setup_input(self, input_group):
        # TODO
        # Overwritten by inheritor.
        # Spider dev define his spider input here.
        pass

    @abstractmethod
    def start(self, component_group, input_group):
        # TODO
        # Spider do job.
        pass

    # @param timer_sec: Time in the given unit. By default, `time_sec`
    #                   is interpreted in seconds.
    # @param unit: The unit for the time `timer_sec`.
    #
    # Terminate running the spider when the spider
    # has run for `time` unit.
    def timer(self, time, unit='s'):
        if unit not in ['s', 'm', 'h']:
            logging.error('Invalid time unit: %s.' % unit)
            raise

class ComponentLoader:

    name = ''
    data = {}
    names = []

    def __init__(self, name, data):
        self.name = name
        self.data = data
        ComponentLoader.names.append(name)

    def set_data(self, data):
        if not isinstance(data, dict):
            logging.error('Data is expected to be of type \'int\' but '
                          '\'%s\' received.' 
                          % (dict.__name__, int.__name__))
            raise
        self.data = data
