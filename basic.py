from kb import *
import string
import random


class Eq(Predicate):
    def __init__(self, *op, name=" = "):
        super(Eq, self).__init__(name, *op)

    def __str__(self):
        return self.value.join(str(x) for x in self.args)

    def substitute(self, sbs):
        result = Eq()
        result.args = [x.substitute(sbs) for x in self.args]
        return result


class plus(Term):
    def __init__(self, *ops, name=" + "):
        super(plus, self).__init__(name, *ops)

    def __str__(self):
        return self.value.join(str(x) for x in self.args)


def state_assosiative(op, v1=None, v2=None):
    v1 = v1 if v1 else Var()
    v2 = v2 if v2 else Var()
    return Disjunct(Eq(op(v1, v2), op(v2, v1)))


def constant(x):
    return Term(value=x)


def skolem_constant(*vars):
    def gen(len, chars=string.ascii_letters):
        return ''.join(random.choices(chars, k=len))
    while True:
        x = gen(6)
        if x not in skolem_constant.C:
            skolem_constant.C.add(x)
            return Term(*vars, value=x)


skolem_constant.C = set()


def state_existential(x, s):
    sbs = Substitution({x: skolem_constant()}, s)
    return s.substitute(sbs)


def implies(s1, s2):
    return Disjunct(s1.negate(), s2)
