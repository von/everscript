"""Collection of ToDo notes"""

from . import EverNote, Notes, ToDo

class ToDos(Notes):

    _item_class = ToDo

    def __init__(self, notebook, search_term=""):
        self.notebook = notebook
        Notes.__init__(self, EverNote.find_notes(search_term=search_term,
                                                 notebook=notebook).notes)

