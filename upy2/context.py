# Developed since: October 2016

import threading


# The implementation of the "upy Context" notion:

class Context(object):
    def __init__(self):
        """ Initialises the Context with an empty Thread Stack
        registry and an empty stack of Defaults. """

        self.thread_stacks = {}  # {ID: [item0, item1, ...], ...}
        self.default_stack = []  # [item0, item1, ...]
        self.lock_default = threading.Lock()
            # A non-reentrant lock to serialise transactions on
            # *self.default_stack*.

    def register(self, item):
        """ Register a new item *item*.  It will be placed on the
        stack of the thread which is calling this method. """

        # We don't need to lock here, since *ID* is unique for all
        # running threads.
        ID = threading.current_thread().ident
        self.thread_stacks.setdefault(ID, [])
        self.thread_stacks[ID].append(item)

    def unregister(self, item):
        """ Unregister the item *item* from the stack of the thread
        which is calling.  It is a ``ValueError`` to provide an item
        which isn't the top-level item on the respective stack. """

        # Ditto as for :meth:`register`: No locking required.
        ID = threading.current_thread().ident
        thread_stack = self.thread_stacks[ID]
        if item is not thread_stack[-1]:
            raise ValueError('The context item to be unregistered is '
                'not the topmost entry on the stack')

        del thread_stack[-1]
        if len(thread_stack) == 0:
            del self.thread_stacks[ID]

    def current(self):
        """ Returns the item applicable to the thread calling.  When
        the stack of the thread calling is empty, the Default Stack
        will be considered.  When this is empty too, a LookupError
        will be raised.
        """

        ID = threading.current_thread().ident
        # No locking required:  Only the thread defined by *ID* can
        # alter self.stacks[ID].
        if ID in self.thread_stacks:
            # Thread Stacks are removed by :meth:`unregister` when
            # they are empty.  Hence we always have a non-empty Thread
            # Stack here.
            return self.thread_stacks[ID][-1]

        # Other threads could remove the final Default item between
        # the check and the retrieval.  Hence we need to render the
        # access to *self.default_stack* transactional.
        with self.lock_default:
            if len(self.default_stack) > 0:
                return self.default_stack[-1]
        
        # When we reached here, no item is applicable.
        raise LookupError('No applicable context item found')

    def default(self, item):
        """ Provide *item* as the new thread-global default item.
        This will be used by :meth:`current` when there is no
        thread-local item present.  The new item will be placed on the
        Default Stack. """

        # We need to respect the atomicity of the access to
        # :attr:`default_stack` in :meth:`undefault` and
        # :meth:`current`:
        with self.lock_default:
            self.default_stack.append(item)

    def undefault(self, item):
        """ Calls back *item* defined previously as Default Item.  It
        is a ``ValueError`` to provide an *item* which is not the
        toplevel item on the Default Stack. """

        # It can happen that another thread defines a new Default
        # between the check below and the removal.  Hence we need
        # to render the un-defaulting transaction atomic.

        with self.lock_default:
            if item is not self.default_stack[-1]:
                raise ValueError('Un-defaulting a context item which '
                    'is not the current default item')

            del self.default_stack[-1]

# The module-scope implementation of the Context Registry:

registry = {}  # {Protocol Class: Context}

def define(protocol):
    registry.setdefault(protocol, Context())
# Contexts exist as long as their key Protocol class, so we don't need
# :func:`undefine`.

def protocol(protocol):
    for key in registry.keys():
        if issubclass(protocol, key):
            return registry[key]
    raise KeyError('No Context defined for protocol %s' % protocol)

def protocolobj(protocolobj):
    for key in registry.keys():
        if isinstance(protocolobj, key):
            return registry[key]
    raise KeyError('No Context defined for protocol object %s' % protocolobj)

# Registering and unregistering at the registry:

class ContextProvider(object):
    """ This class implements the Python Context Manager protocol to
    register and unregister the instance of this class at a
    :class:`upy2.Context` instance (to "Provide Context"). """

    def __init__(self):
        self._upy_context = protocolobj(self)
            # Protocol classes registered later might "shadow" the
            # Context retrieved here when they are subclasses of the
            # respective protocol class.  Hence we store the Context
            # for later use.

    def default(self):
        self._upy_context.default(self)

    def undefault(self):
        self._upy_context.undefault(self)

    def register(self):
        self._upy_context.register(self)

    def unregister(self):
        self._upy_context.unregister(self)

    def __enter__(self):
        self.register()

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.unregister()
