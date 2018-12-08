from kb import *
from basic import *
from fol_set import *


def create_group(set, op, zero):
    v1 = Var()
    identity = implies(contains(v1, set), Eq(op(v1, zero), v1))
    v2, v3 = Var(), Var()
    closure = Disjunct(Not(contains(v2, set)), Not(contains(v3, set)),
                       contains(op(v2, v3), set))
    v4 = Var()
    inv = skolem_constant(v4)
    inverse1 = implies(contains(v4, set), contains(inv, set))
    inverse2 = implies(contains(v4, set), Eq(op(v4, inv), zero))
    v5, v6 = Var(), Var()
    associative = Disjunct(Not(contains(v5, set)), Not(contains(v6, set)),
                           state_assosiative(op, v5, v6))
    return Conjunct(closure, associative, identity, inverse1, inverse2)


def create_group_2(op, zero):
    v1 = Var()
    identity = Disjunct(Eq(op(v1, zero), v1))
    v4 = Var()
    inv = skolem_constant(v4)
    inverse2 = Disjunct(Eq(op(v4, inv), zero))
    v5, v6 = Var(), Var()
    associative = state_assosiative(op, v5, v6)
    return Conjunct(associative, identity, inverse2)



