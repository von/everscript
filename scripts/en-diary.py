#!/usr/bin/env python
"""Evernote diary manager
"""
from appscript import app
import argparse
from datetime import date
import logging
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
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()
    output_handler.setLevel(args.output_level)

    todays_title = date.today().strftime("%B %d, %Y")
    todays_notes = EverNote.find_notes(todays_title, notebook=DIARY_NOTEBOOK)
    if len(todays_notes):
	output.info("Opening existing diary for {}".format(todays_title))
	todays_note = todays_notes[0]
    else:
	output.info("Creating new diary for {}".format(todays_title))
	todays_note = EverNote.create_note(with_text="",
					   title=todays_title,
					   notebook=DIARY_NOTEBOOK)
    EverNote.open_note_window(todays_note)
    return(0)

if __name__ == "__main__":
    sys.exit(main())
