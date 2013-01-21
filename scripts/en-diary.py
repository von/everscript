#!/usr/bin/env python
"""Evernote diary manager
"""
import argparse
import ConfigParser
from datetime import date
import logging
import os
import sys

from everscript import EverNote

# Note book containing my diary entries
DIARY_NOTEBOOK="Diary"

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
    parser.add_argument("-f", "--force",
			action='store_const', const=True,
			dest="force", default=False,
			help="Force creation of new diary")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()
    output_handler.setLevel(args.output_level)

    config = ConfigParser.SafeConfigParser()
    conf_path = os.path.expanduser(args.config)
    if os.path.exists(conf_path):
	output.debug("Parsing configuration file {}".format(args.config))
	config.read(conf_path)

    title = date.today().strftime("%B %d, %Y")
    output.debug("Today's note title is: {}".format(title))

    try:
	notebook = config.get("Diary", "Notebook")
    except (ConfigParser.NoOptionError,
	    ConfigParser.NoSectionError) as e:
	output.error("No Diary notebook defined in configuration")
	sys.exit(1)

    if args.force:
        output.debug("Forcing creationg of new diary")
        note = None
    else:
        try:
            note = EverNote.find_note_by_title(title, notebook=notebook)
        except EverNoteException as e:
            output.exception("Error trying to find today's diary")
            raise

    if note:
	output.debug("Using existing diary: {}".format(title))
    else:
        output.debug("Creating new diary: {}".format(title))
        try:
            template_title = config.get("Diary", "Template")
            output.debug("Using template: {}".format(template_title))
            template_note = EverNote.find_notes(template_title,
                                                notebook=notebook)[0]
            template = template_note.content()
        except (ConfigParser.NoOptionError,
                ConfigParser.NoSectionError) as e:
            pass  # No template defined
        except EverNoteException as e:
            output.exception("Error finding diary template")
            sys.exit(1)

        html = template.format(events="", todo="")
        try:
            note = EverNote.create_note(with_html=html,
                                        title=title,
                                        notebook=notebook)
        except EverNoteException as e:
            output.exception("Error creating today's diary")
            sys.exit(1)

    output.debug("Success. Opening diary: {}".format(title))
    EverNote.open_note_window(note)
    return(0)

if __name__ == "__main__":
    sys.exit(main())
