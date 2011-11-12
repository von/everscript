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
    
    def due_today(self):
        """Return Todos with subset of todos due today."""
        return self.filter(lambda t: t.due_today())

    def past_due(self):
        """Return Todos with subset of todos due prior to tody."""
        today = datetime.date.today()
        return self.filter(lambda t: t.past_due())

    def due_asap(self):
        """Returns Todos with subset of todos due ASAP."""
        return self.filter(lambda t: t.due_asap())

    def without_due_date(self):
        """Return Todos with subset of todos without due date."""
        return self.filter(lambda t: t.due_date() is None)

    def due_soon(self, soon_days=7):
        """Return Todos with subset of todos due in next soon_days days."""
        return self.filter(lambda t: t.due_soon(soon_days))

    def due_later(self, later_days=8):
        """Return Todos with subset of todos due later_days or more from today."""
        later = datetime.date.today() + datetime.timedelta(later_days)
        return self.filter(lambda t: t.due_later(later_days))

    def filter(self, filter_function):
        """Return Todos with subset of tods that evaluate to True with filter_function."""
        todos = ToDos()
        for todo in self:
            if filter_function(todo):
                todos.append(todo)
        return todos
