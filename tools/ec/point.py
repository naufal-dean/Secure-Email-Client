import math
import collections


Point = collections.namedtuple('Point', ['x', 'y'])


def get_identity_point() -> Point:
    return Point(math.inf, math.inf)


def is_identity_point(P: Point) -> bool:
    return P == get_identity_point()
