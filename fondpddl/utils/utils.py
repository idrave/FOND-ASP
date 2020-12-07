from typing import List, Iterator, Any

def get_combinations(options: List[Iterator], current, combine, count=0):
    if count == len(options):
        yield current
    else:
        for op in options[count]:
            for comb in get_combinations(options, combine(current, op), combine, count=count+1):
                yield comb

def find_combination(options: List[List[Any]], pos):
    total = 1
    for op in options:
        total *= len(op)
    def find_pos(i):
        if i == len(options)-1:
            return [options[i][pos%len(options[i])]], pos//len(options[i])
        result, j = find_pos(i+1)
        return [options[i][j%len(options[i])]]+result, j // len(options[i])
    if len(options) == 0:
        return None
    return find_pos(0)[0]

    
