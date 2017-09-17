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
    """ Define a :class:`Context` for the given *protocol*.  When the
    respective Context already exists, this function is a no-op.
    Otherwise an empty :class:`Context` instance will be registered
    for the key *protocol*.

    The *protocol* should be a subclass of
    :class:`upy2.context.Protocol`. """

    registry.setdefault(protocol, Context())
# Contexts exist as long as their key Protocol class, so we don't need
# :func:`undefine`.

def byprotocol(protocol):
    """ Returns the Context for a Protocol class *protocol*.  Keys
    which are a *parent class* of *protocol* will match. """

    for key in registry.keys():
        if issubclass(protocol, key):
            return registry[key]
    raise KeyError('No Context defined for protocol %s' % protocol)

def byprotocolobj(protocolobj):
    """ Returns the Context for an instance of :class:`Protocol` given
    as *protocolobj*.  Keys will match when *protocolobj* is an
    instance of the respective key class. """

    for key in registry.keys():
        if isinstance(protocolobj, key):
            return registry[key]
    raise KeyError('No Context defined for protocol object %s' % protocolobj)

# Registering and unregistering at the registry:

class Protocol(object):
    """ This class implements the Python Context Manager protocol to
    register and unregister instances of this class at the respective
    :class:`upy2.context.Context` instance.  It is the base class of
    all Protocol Classes and their implementations.  It also provides
    means to register/unregister and to default/undefault its
    instances explicitly. """

    def default(self):
        byprotocolobj(self).default(self)

    def undefault(self):
        byprotocolobj(self).undefault(self)

    def register(self):
        byprotocolobj(self).register(self)

    def unregister(self):
        byprotocolobj(self).unregister(self)

    def __enter__(self):
        self.register()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.unregister()
