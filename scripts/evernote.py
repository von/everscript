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

def list_todos(args, output, config):
    todos = ToDos(config.get("ToDos", "Notebook"))
    for todo in todos:
        print todo.title()
    return(0)

def daily_diary(args, output, config):
    todays_title = date.today().strftime("%B %d, %Y")
    diary_notebook = config.get("Diary", "Notebook")
    todays_notes = EverNote.find_notes(todays_title, notebook=diary_notebook)
    if len(todays_notes):
        output.info("Opening existing diary for {}".format(todays_title))
        todays_note = todays_notes[0]
    else:
        output.info("Creating new diary for {}".format(todays_title))
        todays_note = EverNote.create_note(with_text="",
                                           title=todays_title,
                                           notebook=diary_notebook)
    EverNote.open_note_window(todays_note)
    return(0)

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
    parser_list.set_defaults(func=list_todos)

    parser_diary = subparsers.add_parser("diary", help="daily diary")
    parser_diary.set_defaults(func=daily_diary)

    args = parser.parse_args()
    output_handler.setLevel(args.output_level)

    config = ConfigParser.SafeConfigParser()
    conf_path = os.path.expanduser(args.config)
    if os.path.exists(conf_path):
        output.debug("Parsing configuration file {}".format(args.config))
        config.read(conf_path)

    result = args.func(args, output, config)

    return(result)

if __name__ == "__main__":
    sys.exit(main())
    
