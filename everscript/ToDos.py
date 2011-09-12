"""Collection of ToDo notes"""

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
