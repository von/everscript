#!/usr/bin/env python
"""Evernote commandline script via appscript and AppleTalk

Uses the configuration file ~/.evernote/config by default, which has
the following format:

[Diary]
Notebook=Diary

[ToDos]
Notebook=2.Next Action
"""
from appscript import app
import argparse
import ConfigParser
from datetime import date
import logging
import os.path
import sys

from everscript import EverNote, ToDos

######################################################################

class Command:
    """Base class for commands"""
    logger = None
    conf = None

    def __init__(self, **kwargs):
        self.logger = kwargs["logger"]
        self.conf = kwargs["config"]

    #
    # Config functions
    def config(self, section, param):
        """Get parameter from section.

        Returns None if not defined."""
        value = None
        if self.conf:
            try:
                value = self.conf.get(section, param)
            except (ConfigParser.NoOptionError,
                    ConfigParser.NoSectionError) as e:
                pass
        return value

    #
    # Logging functions
    def output(self, msg):
        """Output a message."""
        if self.logger:
            self.logger.info(msg)

    def info(self, msg):
        """Log a message at info level"""
        if self.logger:
            self.logger.info(msg)

    def debug(self, msg):
        """Log a message at debug level"""
        if self.logger:
            self.logger.debug(msg)

    def execute(self, args):
        """Execute the command with given args namespace"""
        raise NotImplementedError()

class CommandException(Exception):
    """Exception in command"""
    pass

class MissingConfigurationException(CommandException):
    """Configuration missing"""
    pass

######################################################################
#
# Commands

class ToDosCmd(Command):
    def execute(self, args):
        todo_notebook = self.config("ToDos", "Notebook")
        if not todo_notebook:
            raise MissingConfigurationException("No ToDos notebook defined")
        todos = ToDos(todo_notebook)
        for todo in todos:
            self.output(todo.title())
        return(0)

class DiaryCmd(Command):
    def __init__(self, *args, **kwargs):
        Command.__init__(self, *args, **kwargs)
        self.title = date.today().strftime("%B %d, %Y")
        self.notebook = self.config("Diary", "Notebook")
        if not self.notebook:
            raise MissingConfigurationException("No Diary notebook defined")

    def execute(self, args):
        todays_notes = EverNote.find_notes(self.title,
                                           notebook=self.notebook)
        if len(todays_notes):
            self.output("Opening existing diary for {}".format(self.title))
            todays_note = todays_notes[0]
        else:
            self.output("Creating new diary for {}".format(self.title))
            template = self.get_template()
            todays_note = EverNote.create_note(with_html=template,
                                               title=self.title,
                                               notebook=self.notebook)
        EverNote.open_note_window(todays_note)
        return(0)

    def get_template(self):
        template_note_title = self.config("Diary", "Template")
        template = ""
        if template_note_title:
            template_notes = EverNote.find_notes(template_note_title,
                                                 notebook=self.notebook)
            if len(template_notes) > 0:
                # TODO: find exact note
                self.debug("Using \"{}\" for template.".format(template_note_title ))
                template = template_notes[0].content()
        else:
            self.debug("No template in use: " + str(e))
        return template
            
def main(argv=None):
    # Do argv default this way, as doing it in the functional
    # declaration sets it at compile time.
    if argv is None:
        argv = sys.argv

    # Set up out output via logging module
    output = logging.getLogger(argv[0])
    output.setLevel(logging.DEBUG)
    output_handler = logging.StreamHandler(sys.stdout)  # Default is sys.stderr
    # Set up formatter to just print message without preamble
    output_handler.setFormatter(logging.Formatter("%(message)s"))
    output.addHandler(output_handler)

    # Argument parsing
    parser = argparse.ArgumentParser(
        description=__doc__, # printed with -h/--help
        # Don't mess with format of description
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # To have --help print defaults with trade-off it changes
        # formatting, use: ArgumentDefaultsHelpFormatter
        )
    # Only allow one of debug/quiet mode
    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument("-d", "--debug",
                                 action='store_const', const=logging.DEBUG,
                                 dest="output_level", default=logging.INFO,
                                 help="print debugging")
    verbosity_group.add_argument("-q", "--quiet",
                                 action="store_const", const=logging.WARNING,
                                 dest="output_level",
                                 help="run quietly")
    parser.add_argument("-c", "--config",
                        default="~/.evernote/config",
                        help="specify configuration file")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")

    subparsers = parser.add_subparsers(help="Commands")

    parser_list = subparsers.add_parser("todos", help="list todos")
    parser_list.set_defaults(cmd_class=ToDosCmd)

    parser_diary = subparsers.add_parser("diary", help="daily diary")
    parser_diary.set_defaults(cmd_class=DiaryCmd)

    args = parser.parse_args()
    output_handler.setLevel(args.output_level)

    config = ConfigParser.SafeConfigParser()
    conf_path = os.path.expanduser(args.config)
    if os.path.exists(conf_path):
        output.debug("Parsing configuration file {}".format(args.config))
        config.read(conf_path)

    try:
        cmd = args.cmd_class(config=config, logger=output)
        result = cmd.execute(args)
    except CommandException as e:
        output.error(str(e))

    return(result)

if __name__ == "__main__":
    sys.exit(main())
    
