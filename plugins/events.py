"""Plugin to generate list of events from iCal"""

import cgi
import re
import subprocess

import everscript

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

class Plugin(everscript.Plugin):
    def __init__(self):
        self.events = self.get_events()
        self.html = self.events_to_html(self.events)

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
	    self.error("Error executing {}: {}".format(icalBuddy,
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

    def __str__(self):
        return self.html
