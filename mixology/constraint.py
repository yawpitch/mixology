from typing import Hashable
from typing import Union as _Union

from .package import Package
from .range import Range
from .set_relation import SetRelation
from .union import Union


class Constraint(object):
    """
    A term constraint.
    """

    def __init__(
        self, package, constraint
    ):  # type: (Hashable, _Union[Range, Union]) -> None
        self._package = package
        self._constraint = constraint

    @property
    def package(self):  # type: () -> Hashable
        return self._package

    @property
    def constraint(self):  # type: () -> _Union[Range, Union]
        return self._constraint

    @property
    def inverse(self):  # type: () -> Constraint
        assert isinstance(self.constraint, Range)
        new_constraint = self.constraint.inverse
        return self.__class__(self.package, new_constraint)

    def allows_all(self, other):  # type: (Constraint) -> bool
        assert isinstance(other.constraint, (Range, Union))
        return self.constraint.allows_all(other.constraint)

    def allows_any(self, other):  # type: (Constraint) -> bool
        return self.constraint.allows_any(other.constraint)

    def difference(self, other):  # type: (Constraint) -> Constraint
        return self.__class__(
            self.package, self.constraint.difference(other.constraint)
        )

    def intersect(self, other):  # type: (Constraint) -> Constraint
        if other.package != self.package:
            raise ValueError("Cannot intersect two constraints for different packages")

        return self.__class__(self.package, self.constraint.intersect(other.constraint))

    def union(self, other):  # type: (Constraint) -> Constraint
        if other.package != self.package:
            raise ValueError(
                "Cannot build an union of two constraints for different packages"
            )

        return self.__class__(self.package, self.constraint.union(other.constraint))

    def is_subset_of(self, other):  # type: (Constraint) -> bool
        return other.allows_all(self)

    def overlaps(self, other):  # type: (Constraint) -> bool
        return other.allows_any(self)

    def is_disjoint_from(self, other):  # type: (Constraint) -> bool
        return not self.overlaps(other)

    def relation(self, other):  # type: (Constraint) -> SetRelation
        if self.is_subset_of(other):
            return SetRelation.SUBSET
        elif self.overlaps(other):
            return SetRelation.OVERLAPPING
        else:
            return SetRelation.DISJOINT

    def is_any(self):  # type: () -> bool
        return self._constraint.is_any()

    def is_empty(self):  # type: () -> bool
        return self._constraint.is_empty()

    def __eq__(self, other):  # type: (object) -> bool
        if not isinstance(other, Constraint):
            return NotImplemented

        return other.package == self.package and other.constraint == self.constraint

    def __hash__(self):  # type: () -> int
        return hash(self.package) ^ hash(self.constraint)

    def to_string(self, allow_every=False):  # type: (bool) -> str
        if self.package == Package.root():
            return "root"
        elif allow_every and self.is_any():
            return "every version of {}".format(self.package)

        return "{} ({})".format(
            self.package, "*" if self.is_any() else str(self.constraint)
        )

    def __str__(self):  # type: () -> str
        return self.to_string()
