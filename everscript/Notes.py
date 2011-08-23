"""Wrapper around a list of notes"""

from operator import getitem

from Note import Note

class Notes(object):

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
            print args
            return Notes(getitem(self.notes, *args))
        else:
            return Note(getitem(self.notes, i))
