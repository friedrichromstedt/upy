# Developed since: October 2016

""" The implementation of the upy Session notion. """

import threading


class Session(object):
    def __init__(self):
        """ Initialises the Session with an empty Thread Stack
        registry and an empty stack of Defaults. """

        self.thread_stacks = {}
            # {ID: [manager0, manager1, ...], ...}
        self.default_stack = []
            # [manager0, manager1, ...]
        self.lock_default = threading.Lock()
            # A non-reentrant lock to serialise transactions on
            # *self.default_stack*.

    def register(self, manager):
        """ Register a new session manager *manager*.  The manager
        will be placed on the stack of the thread which is calling
        this method. """

        # We don't need to lock here, since *ID* is unique for all
        # running threads.
        ID = threading.current_thread().ident
        self.thread_stacks.setdefault(ID, [])
        self.thread_stacks[ID].append(manager)

    def unregister(self, manager):
        """ Unregister the session manager *manager* from the stack
        of the thread which is calling.  It is a ``ValueError`` to
        specify a manager which isn't the top-level manager on the
        respective stack. """

        # Ditto as for :meth:`register`: No locking required.
        ID = threading.current_thread().ident
        thread_stack = self.thread_stacks[ID]
        if manager is not thread_stack[-1]:
            raise ValueError('The session manager to be unregistered '
                'is not the topmost entry on the stack')

        del thread_stack[-1]
        if len(thread_stack) == 0:
            del self.thread_stacks[ID]

    def current(self):
        """ Returns the session manager applicable to the thread
        calling.  When the stack of the thread calling is empty, the
        Default Stack will be considered.  When this is empty too, a
        LookupError will be raised. """

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
        raise LookupError('No applicable session manager found')

    def default(self, manager):
        """ Provide *manager* as the new thread-global default
        session manager.  This will be used by :meth:`current` when
        there is no thread-local manager present.  The new manager
        will be placed on the Default Stack. """

        # We need to respect the atomicity of the access to
        # :attr:`default_stack` in :meth:`undefault` and
        # :meth:`current`:
        with self.lock_default:
            self.default_stack.append(manager)

    def undefault(self, manager):
        """ Recalls *manager* defined previously as Default session
        manager.  It is a ``ValueError`` to provide a *manager*
        which is not the toplevel item on the Default Stack. """

        # It can happen that another thread defines a new Default
        # between the check below and the removal.  Hence we need
        # to render the un-defaulting transaction atomic.
        with self.lock_default:
            if manager is not self.default_stack[-1]:
                raise ValueError('Un-defaulting a session manager '
                    'which is not the current default item')

            del self.default_stack[-1]

# The module-scope implementation of the Session registry:

sessions = {}  # {Protocol class: Session}

def define(protocol):
    """ Define a :class:`Session` for the given *protocol*.  When the
    respective Session already exists, this function is a no-op.
    Otherwise an empty :class:`Session` instance will be registered
    for the key *protocol*.

    The *protocol* should be a subclass of
    :class:`upy2.context.Protocol`. """

    sessions.setdefault(protocol, Session())
# Sessions exist as long as their key Protocol class, so we don't need
# :func:`undefine`.

def byprotocol(protocol):
    """ Returns the Session for a Protocol class *protocol*.  Keys
    which are a *parent class* of *protocol* will match. """

    for key in sessions.keys():
        if issubclass(protocol, key):
            # *protocol* is a subclass of *key*.
            return sessions[key]
    raise KeyError('No Session defined for protocol {}'.\
            format(protocol))

def byprotocolobj(protocolobj):
    """ Returns the Session for an instance of :class:`Protocol` given
    as *protocolobj*.  Keys will match when *protocolobj* is an
    instance of the respective key class. """

    for key in sessions.keys():
        if isinstance(protocolobj, key):
            return sessions[key]
    raise KeyError('No Session defined for protocol object {}'.\
            format(protocolobj))

# Registering and unregistering at the registry:

class Protocol(object):
    """ This class implements the Python Context Manager protocol to
    register and unregister instances of this class at the respective
    :class:`upy2.sessions.Session` instance.  It is the base class of
    all Protocol classes and their implementations.  It also provides
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

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.unregister()
