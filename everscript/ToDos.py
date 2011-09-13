"""Collection of ToDo notes"""

import datetime

from . import EverNote, Notes, ToDo

class ToDos(Notes):

    _item_class = ToDo

    def __init__(self, notebook=None, search_term=""):
        self.notebook = notebook
        if notebook:
            notes = EverNote.find_notes(search_term=search_term,
                                        notebook=notebook).notes
        else:
            notes = []
        Notes.__init__(self, notes)

    def bin_by_due_date(self, soon_days=7):
        """Return separate ToDos sorted by due date.

        Returns tuple of ToDos: past due, due today, due soon, due later, not due.
        soon defines soon by number of days."""
        soon = datetime.timedelta(soon_days)
        today = datetime.date.today()
        past_due = ToDos()
        due_today = ToDos()
        due_soon = ToDos()
        due_later = ToDos()
        not_due = ToDos()
        for todo in self:
            due_date = todo.due_date()
            if due_date is None:
                not_due.append(todo)
            elif due_date < today:
                past_due.append(todo)
            elif due_date == today:
                due_today.append(todo)
            elif due_date - today <= soon:
                due_soon.append(todo)
            else:
                due_later.append(todo)
        return past_due, due_today, due_soon, due_later, not_due
