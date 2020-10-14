from typing import List, Iterator

def get_combinations(options: List[Iterator], current: List, combine):
    if len(current) == len(options):
        yield current
    else:
        i = len(current)
        for op in options[i]:
            for comb in get_combinations(options, combine(current, op), combine):
                yield comb