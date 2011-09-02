"""Evernote note representing a ToDo"""

from EverNote import EverNote, Notes

class ToDos(Notes):

    def __init__(self, notebook, search_term=""):
        self.notebook = notebook
        Notes.__init__(self, EverNote.find_notes(search_term=search_term,
                                                 notebook=notebook).notes)

