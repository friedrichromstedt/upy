# Developed since: October 2016

import threading

class Context:
    def __init__(self):
        self.stacks = {}
        self.default = None
        self.lock = threading.Lock()

    def register(self, item):
        # We don't need to lock here, since *ID* is unique for all
        # running threads.
        ID = threading.current_thread().ident
        self.stacks.setdefault(ID, [])
        self.stacks[ID].append(item)

    def unregister(self, item):
        # Ditto as for :meth:`register`: No locking required.
        ID = threading.current_thread().ident
        stack = self.stacks[ID]
        if item is not stack[-1]:
            raise ValueError('The item to be unregistered is not the '
                    'topmost entry on the stack')

        del stack[-1]
        if len(stack) == 0:
            del self.stacks[ID]

    def current(self):
        ID = threading.current_thread().ident
        if ID in self.stacks:
            return self.stacks[ID][-1]
        # No locking required:  It does not matter when *self.default*
        # changed since entering the method.
        return self.default

    def default(self, item):
        # No locking required:  Setting the default is atomic, and
        # race conditions do not matter here.
        self.default = item

    def undefault(self, item):
        # No locking required:  There exists only one *default* item
        # which can be un-defaulted.

        if item is not self.default:
            raise ValueError('Unsetting an item which is not the '
                    'current default item')

        self.default = None
