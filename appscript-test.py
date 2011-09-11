#!/usr/bin/env python
from appscript import app
evernote = app("EverNote")
notebooks = evernote.notebooks.get()
print "Notebooks:"
for notebook in notebooks:
    print notebook.name.get()
print "Notes:"
notes = evernote.find_notes("July")
for note in notes:
    print note.title.get()
print notes[0].HTML_content.get()
    #print note.source_URL.get()
#evernote.open_note_window(with_=notes[0])
#evernote.open_collection_window(with_query_string="June")
