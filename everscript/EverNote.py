"""EverNote class"""

from appscript import app

from Note import Note
from Notes import Notes

class EverNote(object):

    def __init__(self, app_name="EverNote"):
        self.app = self.__get_app(app_name)

    @classmethod
    def __get_app(cls, app_name="EverNote"):
        return app(app_name)

    @classmethod
    def create_note(cls, with_html=None, with_text=None, title="", notebook=None):
        """Create a note"""
        kwargs={
            "title":title,
            "notebook":notebook,
            }
        if with_html is not None:
            kwargs["with_html"] = with_html
        if with_text is not None:
            kwargs["with_text"] = with_text
        return Note(cls.__get_app().create_note(**kwargs))

    @classmethod
    def find_notes(cls, search_term, notebook=None):
        """Find notes matching search_term. Returns Notes object.

        If notebook is not None, scope search to notebook.
        """
        search_term="\"" + search_term + "\""
        if notebook:
            search_term += " notebook:\"{}\"".format(notebook)
        return Notes(cls.__get_app().find_notes(search_term))

    @classmethod
    def open_collection_window(cls, query_string=None):
        """Open a collection window"""
        # TODO: handle other arguments besides query_string
        kwargs={}
        if query_string:
            kwargs["with_query_string"] = query_string
        return cls.__get_app().open_collection_window(**kwargs)

    @classmethod
    def open_note_window(cls, note):
        return cls.__get_app().open_note_window(with_=note.note)

        
