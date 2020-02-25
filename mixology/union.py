from typing import List
from typing import Union as _Union

import mixology.range


class Union(object):
    """
    An union of Ranges.
    """

    def __init__(self, *ranges):  # type: (*mixology.range.Range) -> None
        self._ranges = list(ranges)

    @property
    def ranges(self):  # type: () -> List[mixology.range.Range]
        return self._ranges

    @classmethod
    def of(cls, *ranges):  # type: (*_Union[mixology.range.Range, Union]) -> _Union[mixology.range.Range, Union]
        flattened = []  # type: List[mixology.range.Range]
        for constraint in ranges:
            if constraint.is_empty():
                continue

            if isinstance(constraint, Union):
                flattened += constraint.ranges
                continue

            flattened.append(constraint)

        if not flattened:
            return mixology.range.EmptyRange()

        if any([constraint.is_any() for constraint in flattened]):
            return mixology.range.Range()

        flattened.sort()

        merged = []  # type: List[mixology.range.Range]
        for constraint in flattened:
            # Merge this constraint with the previous one, but only if they touch.
            if not merged or (
                not merged[-1].allows_any(constraint)
                and isinstance(merged[-1], mixology.range.Range)
                and not merged[-1].is_adjacent_to(constraint)
            ):
                merged.append(constraint)
            else:
                union = merged[-1].union(constraint)
                assert isinstance(union, mixology.range.Range)
                merged[-1] = union

        if len(merged) == 1:
            return merged[0]

        return Union(*merged)

    def is_empty(self):  # type: () -> bool
        return False

    def is_any(self):  # type: () -> bool
        return False

    def allows_all(self, other):  # type: (_Union[mixology.range.Range, Union]) -> bool
        our_ranges = iter(self._ranges)
        their_ranges = iter(self._ranges_for(other))

        our_current_range = next(our_ranges, None)
        their_current_range = next(their_ranges, None)

        while our_current_range and their_current_range:
            if our_current_range.allows_all(their_current_range):
                their_current_range = next(their_ranges, None)
            else:
                our_current_range = next(our_ranges, None)

        return their_current_range is None

    def allows_any(self, other):  # type: (_Union[mixology.range.Range, Union]) -> bool
        our_ranges = iter(self._ranges)
        their_ranges = iter(self._ranges_for(other))

        our_current_range = next(our_ranges, None)
        their_current_range = next(their_ranges, None)

        while our_current_range and their_current_range:
            if our_current_range.allows_any(their_current_range):
                return True

            if their_current_range.allows_higher(our_current_range):
                our_current_range = next(our_ranges, None)
            else:
                their_current_range = next(their_ranges, None)

        return False

    def intersect(
        self, other
    ):  # type: (_Union[mixology.range.Range, Union]) -> _Union[mixology.range.Range, Union]
        our_ranges = iter(self._ranges)
        their_ranges = iter(self._ranges_for(other))
        new_ranges = []

        our_current_range = next(our_ranges, None)
        their_current_range = next(their_ranges, None)

        while our_current_range and their_current_range:
            intersection = our_current_range.intersect(their_current_range)

            if not intersection.is_empty():
                new_ranges.append(intersection)

            if their_current_range.allows_higher(our_current_range):
                our_current_range = next(our_ranges, None)
            else:
                their_current_range = next(their_ranges, None)

        return Union.of(*new_ranges)

    def union(
        self, other
    ):  # type: (_Union[mixology.range.Range, Union]) -> _Union[mixology.range.Range, Union]
        return Union.of(self, other)

    def difference(
        self, other
    ):  # type: (_Union[mixology.range.Range, Union]) -> _Union[mixology.range.Range, Union]
        our_ranges = iter(self._ranges)
        their_ranges = iter(self._ranges_for(other))
        new_ranges = []  # type: List[_Union[mixology.range.Range, Union]]

        state = {
            "current": next(our_ranges, None),
            "their_range": next(their_ranges, None),
        }

        def their_next_range():  # type: () -> bool
            state["their_range"] = next(their_ranges, None)
            if state["their_range"]:
                return True

            assert state["current"] is not None
            new_ranges.append(state["current"])
            our_current = next(our_ranges, None)
            while our_current:
                new_ranges.append(our_current)
                our_current = next(our_ranges, None)

            return False

        def our_next_range(include_current=True):  # type: (bool) -> bool
            if include_current:
                assert state["current"] is not None
                new_ranges.append(state["current"])

            our_current = next(our_ranges, None)
            if not our_current:
                return False

            state["current"] = our_current

            return True

        while True:

            if state["their_range"] is None:
                break

            if state["current"] is None:
                break


            if state["their_range"].is_strictly_lower(state["current"]):
                if not their_next_range():
                    break

                continue

            if state["their_range"].is_strictly_higher(state["current"]):
                if not our_next_range():
                    break

                continue

            difference = state["current"].difference(state["their_range"])
            if isinstance(difference, Union):
                assert len(difference.ranges) == 2
                new_ranges.append(difference.ranges[0])
                state["current"] = difference.ranges[-1]

                if not their_next_range():
                    break
            elif difference.is_empty():
                if not our_next_range(False):
                    break
            else:
                state["current"] = difference

                if state["current"].allows_higher(state["their_range"]):
                    if not their_next_range():
                        break
                else:
                    if not our_next_range():
                        break

        if not new_ranges:
            return mixology.range.EmptyRange()

        if len(new_ranges) == 1 and new_ranges[0] is not None:
            return new_ranges[0]

        return Union.of(*new_ranges)

    def excludes_single_version(self):  # type: () -> bool
        difference = self.difference(mixology.range.Range())

        return (
            isinstance(difference, mixology.range.Range)
            and difference.is_single_version()
        )

    def _ranges_for(
        self, constraint
    ):  # type: (_Union[Union, mixology.range.Range]) -> List[mixology.range.Range]
        if constraint.is_empty():
            return []

        if isinstance(constraint, Union):
            return constraint.ranges

        return [constraint]

    def __eq__(self, other):  # type: (object) -> bool
        if not isinstance(other, Union):
            return False

        return self._ranges == other.ranges

    def __str__(self):  # type: () -> str
        if self.excludes_single_version():
            return "!={}".format(mixology.range.Range().difference(self))

        return " || ".join([str(r) for r in self._ranges])

    def __repr__(self):  # type: () -> str
        return "<Union {}>".format(str(self))
