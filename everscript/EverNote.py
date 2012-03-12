"""EverNote class"""

import appscript
from contextlib import contextmanager

from Note import Note
from Notes import Notes

class EverNote(object):

    def __init__(self, app_name="EverNote"):
        self.app = self.__get_app(app_name)

    @classmethod
    def __get_app(cls, app_name="EverNote"):
        return appscript.app(app_name)

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
        with AppCallContextManager():
            note = cls.__get_app().create_note(**kwargs)
        return Note(note)

    @classmethod
    def find_notes(cls, search_term, notebook=None):
        """Find notes matching search_term. Returns Notes object.

        If notebook is not None, scope search to notebook.
        """
        search_term="\"" + search_term + "\""
        if notebook:
            search_term += " notebook:\"{}\"".format(notebook)
        with AppCallContextManager():
            notes = cls.__get_app().find_notes(search_term)
        return Notes(notes)

    @classmethod
    def open_collection_window(cls, query_string=None):
        """Open a collection window"""
        # TODO: handle other arguments besides query_string
        kwargs={}
        if query_string:
            kwargs["with_query_string"] = query_string
        with AppCallContextManager():
            window = cls.__get_app().open_collection_window(**kwargs)
        return window

    @classmethod
    def open_note_window(cls, note):
        with AppCallContextManager():
            window = cls.__get_app().open_note_window(with_=note.note)
        return window

class EverNoteException(Exception):
    def __init__(self, message, detailed_message):
        self.message = message
        self.detailed_message = detailed_message

    def __str__(self):
        return self.message

class AppCallContextManager:
    """Context manager for calls to appscript app"""
    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        if type == appscript.reference.CommandError:
            raise EverNoteException(value.errormessage,
                                    str(value))

        
