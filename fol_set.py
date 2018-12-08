from kb import *


class fol_set(Term):
    def __init__(self, name, *args):
        super(fol_set).__init__(*args, value=name)


def contains(x, s):
    return Predicate("ϵ", x, s)
