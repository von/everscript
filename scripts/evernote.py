#!/usr/bin/env python
"""Evernote commandline script via appscript and AppleTalk

Uses the configuration file ~/.evernote/config by default, which has
the following format:

[Diary]
Notebook=Diary
Template=Diary-Template

[ToDos]
NextAction=2.Next Action
Pending=3.Pending
Scheduled=2a.Scheduled

[iCal]
# Calendars to filter on for events (can use UIDs)
Calendars=Calendar,Informational,Personal,3F0B97F7-0B88-48E3-BDAB-977382767D28
"""
import abc
from appscript import app
import argparse
import cgi
import ConfigParser
from datetime import date
import logging
import re
import subprocess
import os.path
import sys

from everscript import EverNote, EverNoteException, ToDos

######################################################################
#
# Command abstract base class

class Command(object):
    """Base class for commands"""
    __metaclass__ = abc.ABCMeta

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

    @abc.abstractmethod
    def execute(self, args):
	"""Execute the command with given args namespace"""
	return

    @abc.abstractmethod
    #@classmethod
    def add_subparser(cls, subparsers):
	"""Add this command's subparser to the given argparser.

	subparsers should be the action returned from ArgumentParser.add_subparsers()
	Returns nothing.
	"""
	return

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
    # Flags for types of todos based on due date
    PAST_DUE = 0x01
    DUE_TODAY = 0x02
    DUE_SOON = 0x04
    DUE_LATER = 0x08
    NO_DUE_DATE = 0x10

    def execute(self, args):
	todo_notebook = self.config("ToDos", "NextAction")
	if not todo_notebook:
	    raise MissingConfigurationException("No ToDos notebook defined")
	todos = ToDos(todo_notebook)
	past_due, due_today, due_soon, due_later, not_due = todos.bin_by_due_date()
	if args.show_flags == []:
	    lists = [ past_due, due_today, due_soon, due_later, not_due ]
	else:
	    lists = []
	    for flag in args.show_flags:
		if flag == self.PAST_DUE:
		    lists.append(past_due)
		elif flag == self.DUE_TODAY:
		    lists.append(due_today)
		elif flag == self.DUE_SOON:
		    lists.append(due_soon)
		elif flag == self.DUE_LATER:
		    lists.append(due_later)
		elif flag == self.NO_DUE_DATE:
		    lists.append(not_due)
	for list in lists:
	    if len(list) > 0:
		for todo in list:
		    self.output(todo.title())
	return(0)

    @classmethod
    def add_subparser(cls, subparsers):
	"""Add this command's subparser to the given argparser.

	subparsers should be the action returned from ArgumentParser.add_subparsers()
	Returns nothing.
	"""
	parser = subparsers.add_parser("todos", help="list todos")
	parser.set_defaults(cmd_class=cls,
			    show_flags=[])
	parser.add_argument("--past",
			    help="Show ToDos past due",
			    dest="show_flags",
			    action="append_const",
			    const=cls.PAST_DUE)
	parser.add_argument("--today",
			    help="Show ToDos due today",
			    dest="show_flags",
			    action="append_const",
			    const=cls.DUE_TODAY)
	parser.add_argument("--soon",
			    help="Show ToDos due soon",
			    dest="show_flags",
			    action="append_const",
			    const=cls.DUE_SOON)

######################################################################

# Event as returned from DiaryCmd.get_events()
class Event(object):
    def __init__(self, title, location, time,
		 url=None, phone=None, note=None):
	self.title = title
	self.location = location
	self.time = time
	self.url = url
	self.phone = phone
	self.note = note

    def __str__(self):
	s = "\"{}\"".format(self.title)
	s += " time: " + self.time
	s += " location:" + self.location
	s += " url:" + self.url if self.url else ""
	s += " phone:" + self.phone if self.phone else ""
	s += " note:" + self.note if self.note else ""
	return s

######################################################################

class DiaryCmd(Command):
    def __init__(self, *args, **kwargs):
	Command.__init__(self, *args, **kwargs)
	self.title = date.today().strftime("%B %d, %Y")
	self.notebook = self.config("Diary", "Notebook")
	if not self.notebook:
	    raise MissingConfigurationException("No Diary notebook defined")

    def execute(self, args):
	self.debug("Today's date is \"{}\" - searching for existing diary".format(self.title))
	try:
	    todays_note = EverNote.find_note_by_title(self.title,
						       notebook=self.notebook)
	except EverNoteException as e:
	    self.output("Error trying to find today's diary: " + str(e))
	    raise
	if todays_note and not args.force:
	    self.output(
		"Opening existing diary: {}".format(todays_note.title()))
	else:
	    self.output("Creating new diary for {}".format(self.title))
	    template = self.get_template()
	    # XXX decode()s here are hacks until I figure out how to deal
	    #     with unicode for real.
	    events = self.get_events_as_html().decode('utf8', 'ignore')
	    todos = self.get_todos_as_html().decode('utf8', 'ignore')
	    html = template.format(events=events, todos=todos)
	    try:
		todays_note = EverNote.create_note(with_html=html,
						   title=self.title,
						   notebook=self.notebook)
	    except EverNoteException as e:
		raise CommandException(
		    "Error creating today's diary: " + str(e))
	EverNote.open_note_window(todays_note)
	return(0)

    def get_template(self):
	template_note_title = self.config("Diary", "Template")
	template = ""
	if template_note_title:
	    try:
		template_notes = EverNote.find_notes(template_note_title,
						     notebook=self.notebook)
	    except EverNoteException as e:
		self.output("Error finding diary tempalte: " + str(e))
		raise
	    if len(template_notes) > 0:
		# TODO: find exact note
		self.debug("Using \"{}\" for template.".format(template_note_title ))
		template = template_notes[0].content()
	else:
	    self.debug("No template in use: " + str(e))
	return template

    def get_todos_as_html(self):
	"""Return list of todos as html"""

	next_action_notebook = self.config("ToDos", "NextAction")
	if next_action_notebook is None:
	    self.debug("No Next Action notebook defined")
	    next_action_todos = ToDos()
	else:
	    self.debug("Next Action notebook is {}".format(next_action_notebook))
	    next_action_todos = ToDos(next_action_notebook)
	    self.debug("Read {} Next Action ToDos".format(len(next_action_todos)))

	pending_notebook = self.config("ToDos", "Pending")
	if pending_notebook is None:
	    self.debug("No Pending Todos notebook defined")
	    pending_todos = ToDos()
	else:
	    pending_todos = ToDos(pending_notebook)
	    self.debug("Read {} Pending ToDos".format(len(pending_todos)))

	scheduled_notebook = self.config("ToDos", "Scheduled")
	if scheduled_notebook is None:
	    self.debug("No Scheduled notebook defined")
	    scheduled_todos = ToDos()
	else:
	    scheduled_todos = ToDos(scheduled_notebook)
	    self.debug("Read {} Scheduled ToDos".format(len(scheduled_todos)))

	html =""
	html += "<b>Past due:</b>\n"
	html += self.todos_to_html(next_action_todos.past_due())
	html += self.todos_to_html(scheduled_todos.past_due())

	html += "<b>Pending past due:</b>\n"
	html += self.todos_to_html(pending_todos.past_due())

	html += "<b>Due today:</b>\n"
	html += self.todos_to_html(next_action_todos.due_today())
	html += self.todos_to_html(scheduled_todos.due_today())

	html += "<b>Pending due today:</b>\n"
	html += self.todos_to_html(pending_todos.due_today())

	html += "<b>Due ASAP:</b>\n"
	html += self.todos_to_html(next_action_todos.due_asap())

	html += "<b>Pending due ASAP:</b>\n"
	html += self.todos_to_html(pending_todos.due_asap())

	html += "<b>Due soon:</b>\n"
	html += self.todos_to_html(next_action_todos.due_soon())

	html += "<b>Pending due soon:</b>\n"
	html += self.todos_to_html(pending_todos.due_soon())

	return html

    def todos_to_html(self, todos):
	"""Covert a ToDos instance to a hunk of HTML."""
	html = "<ul>\n"
	for todo in todos:
	    try:
		html += "<li>{}</li>\n".format(cgi.escape(todo.title()))
	    except Exception as e:
		self.output(
		    "Error encoding todo: \"{}\" : {}".format(
			todo.title(), str(e)))
	html += "</ul>\n"
	return html

    def get_events_as_html(self):
	"""Return list of today's events as html"""
	return self.events_to_html(self.get_events())

    def events_to_html(self, events):
	"""Convert a list of Events to a hunk of HTML."""
	html = "<ul>\n"
	for event in events:
	    html += "<li>{} {}".format(cgi.escape(event.time),
				       cgi.escape(event.title))
	    html += "<ul>"
	    if event.location != "":
		html += "<li>{}</li>".format(cgi.escape(event.location))
	    if event.url:
		html += "<li>{}</li>".format(cgi.escape(event.url))
	    if event.phone:
		html += "<li>{}</li>".format(cgi.escape(event.phone))
	    if event.note:
		html += "<li>{}</li>".format(cgi.escape(event.note))
	    html += "</ul></li>\n"
	html += "</ul>\n"
	return html

    def get_events(self):
	"""Return list of Event objects representing today's events

	Requires icalBuddy to be installed in PATH."""
	self.debug("Getting today's events...")

	icalBuddy = "icalBuddy"
	cmd = [icalBuddy]
	cmd.extend(["-b", "* "])  # Event prefix
	cmd.extend(["-nc"])  # No calendar titles

	# Fields to display, in order
	fields = "title,datetime,location,notes"
	cmd.extend(["-iep", fields])
	cmd.extend(["-po", fields])

	calendars = self.config("iCal", "Calendars")
	if calendars:
	    self.debug("Filtering on calendars: " + calendars)
	    cmd.extend(["-ic", calendars])

	cmd.append("eventsToday")
	self.debug("Executing: " + " ".join(cmd))
	try:
	    out = subprocess.check_output(cmd)
	except OSError as e:
	    self.debug("Error executing {}: {}".format(icalBuddy,
						       str(e)))
	    return []
	self.debug("Raw icalBuddy output:\n" + out)
	raw_events = re.split("^\* ", out, flags=re.M)

	events = []
	for raw_event in raw_events:
	    # Skip empty events
	    if re.match(raw_event, "\s*$"):
		continue
	    title_match = re.match("(.*)", raw_event, flags=re.M)
	    title = title_match.group(1) if title_match else ""
	    time_match = re.search("(\d+:\d+ .M - \d+:\d+ .M)",
				   raw_event, flags=re.M)
	    time = time_match.group(1) if time_match else ""
	    location_match = re.search("location: (.*)",
				       raw_event, flags=re.M)
	    location = location_match.group(1) if location_match else ""
	    notes_match = re.search("notes: (.*)", raw_event, flags=re.DOTALL)
	    notes = notes_match.group(1) if notes_match else ""

	    # Parse tags out of notes field
	    url_match = re.search("@url: (\S+)$", notes, flags=re.M)
	    url = url_match.group(1) if url_match else None
	    phone_match = re.search("@phone: (.+)$", notes, flags=re.M)
	    phone = phone_match.group(1) if phone_match else None
	    note_match = re.search("@note: (.+)$", notes, flags=re.M)
	    note = note_match.group(1) if note_match else None

	    event = Event(title, location, time,
			  url=url, phone=phone, note=note)
	    self.debug("Event found:" + str(event))
	    events.append(event)
	return events

    @classmethod
    def add_subparser(cls, subparsers):
	"""Add this command's subparser to the given argparser.

	subparsers should be the action returned from ArgumentParser.add_subparsers()
	Returns nothing.
	"""
	parser = subparsers.add_parser("diary", help="daily diary")
	parser.set_defaults(cmd_class=cls)
	parser.add_argument("-f", "--force",
			    action='store_const', const=True,
			    dest="force", default=False,
			    help="Force creation of new diary")


######################################################################
#
# main()

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

    for cmd in Command.__subclasses__():
	cmd.add_subparser(subparsers)

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
	result = 1

    return(result)

if __name__ == "__main__":
    sys.exit(main())
