from typing import Any

Incompatibility = Any

class IncompatibilityCause(Exception):
    """
    The reason and Incompatibility's terms are incompatible.
    """


class RootCause(IncompatibilityCause):
    """
    The incompatibility represents the requirement that the root package exists.
    """

    pass


class NoVersionsCause(IncompatibilityCause):
    """
    The incompatibility indicates that the package has no versions that match
    the given constraint.
    """

    pass


class DependencyCause(IncompatibilityCause):
    """
    The incompatibility represents a package's dependency.
    """

    pass


class ConflictCause(IncompatibilityCause):
    """
    The incompatibility was derived from two existing incompatibilities
    during conflict resolution.
    """

    def __init__(self, conflict, other):  # type: (Incompatibility, Incompatibility) -> None
        self._conflict = conflict
        self._other = other

    @property
    def conflict(self):  # type: () -> Incompatibility
        return self._conflict

    @property
    def other(self):  # type: () -> Incompatibility
        return self._other

    def __str__(self):  # type: () -> str
        return str(self._conflict)


class PackageNotFoundCause(IncompatibilityCause):
    """
    The incompatibility represents a package that couldn't be found by its
    source.
    """

    def __init__(self, error):  # type: (Incompatibility) -> None
        self._error = error

    @property
    def error(self):  # type: () -> Incompatibility
        return self._error
