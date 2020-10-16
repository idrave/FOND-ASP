from typing import List, Iterator

def get_combinations(options: List[Iterator], current, combine, count=0):
    if count == len(options):
        yield current
    else:
        for op in options[count]:
            for comb in get_combinations(options, combine(current, op), combine, count=count+1):
                yield comb