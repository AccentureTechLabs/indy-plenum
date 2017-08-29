from typing import NamedTuple, Set, Optional

Output = NamedTuple('Output', [('address', str), ('seq_no', int),
                               ('value', Optional[float])])

OutputList = NamedTuple("OutputList",
                        [("spent", Set[int]), ("unspent", Set[int])])
