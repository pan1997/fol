from kb import *
from fol_group import *


def unify_check():
    five = Term(value="5")
    six = Term(value="6")
    x = Var()
    s1 = five.unify(six)
    s2 = six.unify(x)
    s3 = five.unify(x)
    s4 = six.unify(x, s3)
    assert s1 is None
    assert s2 is not None
    assert s3 is not None
    assert s4 is None
    print(s1, s2, s3, s4)


def gt():
    s = constant('S')
    op = constant('op')
    zero = constant('O')
    r = create_group(s, op, zero)
    verify(r)
    print(r)


def kb_test():
    op = constant('op')
    zero = constant('O')
    r = create_group_2(op, zero)
    k = kb()
    k.tell(r)
    print(k.contradiction())


def verify_dis(exp):
    if type(exp) == Disjunct:
        for x in exp.args:
            verify_con(x)
    else:
        verify_con(exp)


def verify_con(exp):
    if type(exp) == Disjunct:
        raise Exception("Dis inside con")


def verify(exp):
    verify_dis(exp)


if __name__=="__main__":
    kb_test()
    #unify_check()
    #gt()
