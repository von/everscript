""""Evernote note representing a ToDo"""

import datetime
import re

from . import Note

class ToDo(Note):
    """Evernote note representing a ToDo"""

    DUE_REGEX = re.compile("due:\s?(\d\d?/\d\d?(/\d\d\d?\d?)?)",re.IGNORECASE)

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
