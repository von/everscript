"""Wrapper around a EverNote Note"""

class Note(object):

    def __init__(self, note):
        self.note = note

    def title(self):
        return self.note.title.get()

    def content(self):
        """Return content as HTML"""
        return self.note.HTML_content.get()
