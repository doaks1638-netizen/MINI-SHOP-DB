from enum import Enum


class PriceFilter(str, Enum):
    more_expensive = "more_expensive"
    cheaper = "cheaper"


class ActiveFilter(str, Enum):
    all = "all"
    active = "active"
    inactive = "inactive"


class DateFilter(str, Enum):
    old = "old"
    new = "new"
