class Package(object):
    """
    A project's package.
    """

    def __init__(self, name):  # type: (str) -> None
        self._name = name

    @classmethod
    def root(cls):  # type: () -> Package
        return Package("_root_")

    @property
    def name(self):  # type: () -> str
        return self._name

    def __eq__(self, other):  # type: (object) -> bool
        if not isinstance(other, Package):
            return NotImplemented
        return str(other) == self.name

    def __str__(self):  # type: () -> str
        return self._name

    def __repr__(self):  # type: () -> str
        return 'Package("{}")'.format(self.name)

    def __hash__(self):  # type: () -> int
        return hash(self.name)
