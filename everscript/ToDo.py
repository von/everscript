"""Evernote note representing a ToDo"""

import datetime
import re

from . import Note

class ToDo(Note):
    """Evernote note representing a ToDo"""

    DUE_REGEX = re.compile("due:\s?(\d\d?/\d\d?(/\d\d\d?\d?)?)", re.IGNORECASE)

    DUE_ASAP_REGEX = re.compile("\s+ASAP$", re.IGNORECASE)

    def due_today(self):
        """Return True if note is due today.

        Return False if not due today, None if note has no due date."""
        due_date = self.due_date()
        if due_date is None:
            return None
        today = datetime.date.today()
        return (today == due_date)

    def due_asap(self):
        """Is task marked as due ASAP?"""
        match = self.DUE_ASAP_REGEX.search(self.title())
        return match is not None

    def due_soon(self, days):
        """Is task due in the defined future?

        Returns False if task is past due or due today.
        Returns None if task has no due date."""
        due_date = self.due_date()
        if due_date is None:
            return None
        soon = datetime.timedelta(days)
        day = datetime.timedelta(1)
        today = datetime.date.today()
        due_delta = due_date - today
        return ((due_delta >= day) and (due_delta <= soon))

        return 

    def due_later(self, days):
        """Is task due past the defined future?

        Returns False if task is due more than or equal to days in the future.
        Returns None if task has no due date."""
        due_date = self.due_date()
        if due_date is None:
            return None
        later = datetime.timedelta(days) + datetime.date.today()
        return (due_date >= later)

    def past_due(self):
        """Return True if note is past due.

        Return True if past due, None if note has no due date, False otherwise."""
        due_date = self.due_date()
        if due_date is None:
            return None
        today = datetime.date.today()
        return (today > due_date)

    def due_date(self):
        """Return this note's due date as datetime.date"""
        match = self.DUE_REGEX.search(self.title())
        if not match:
            return None
        return self.parse_date(match.group(1))

    @classmethod
    def parse_date(cls, date_str):
        """Parse date string, returning datetime.date

        Returns None if string cannot be parsed."""
        formats = [
            "%m/%d",
            "%m/%d/%Y",
            "%m/%d/%y",
            ]
        for format in formats:
            try:
                # Only datetime has strptime()
                dt = datetime.datetime.strptime(date_str, format)
                break  # Success
            except ValueError:
                # Failed, try next format
                pass
        else:  # No format matached
            return None
        year, month, day = dt.year, dt.month, dt.day
        if year == 1900:
            # Handle undefined year. This is simplistic and
            # should use the note creation date perhaps?
            year = datetime.date.today().year
        # Convert from datetime to simpler date
        date = datetime.date(year, month, day)
        return date
