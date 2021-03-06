"""Wrapper around a list of notes"""

from operator import getitem

from Note import Note

class Notes(object):

    # class representing our individual notes
    _item_class = Note

    def __init__(self, notes):
        self.notes = notes

    def __len__(self):
        return len(self.notes)

    def __getitem__(self, i):
        if isinstance(i, slice):
            args = [i.start] if i.start is not None else []
            args.append(i.stop)
            if i.step:
                args.append(i.step)
            return self.__class__(getitem(self.notes, *args))
        else:
            return self._item_class(getitem(self.notes, i))

    def append(self, note):
        """Append a note to list.

        note must be a Note instance."""
        self.notes.append(note.note)

    def extend(self, notes):
        """Extend a list of notes with another list of notes.

        notes must be a Notes instance."""
        self.notes.extend(notes.notes)

