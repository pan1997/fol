from collections import UserDict, deque


class Term(object):
    def __init__(self, *args, value=None):
        self.args = args
        self.value = value

    def __eq__(self, other):
        return True if self.unify(other) else False

    def leq(self, other, sbs):
        if isinstance(other, Var):
            return other.leq(self, sbs)
        if type(self) != type(other) or len(self.args) != len(other.args) or \
                self.value != other.value:
            return False
        for a, b in zip(self.args, other.args):
            if not a.leq(b, sbs):
                return False
        return True

    def _unify(self, other, base, result):
        if isinstance(other, Var):
            return other._unify(self, base, result)
        if type(self) != type(other) or len(self.args) != len(other.args) or \
                self.value != other.value:
            return None
        for a, b in zip(self.args, other.args):
            result = a._unify(b, base, result)
            if not result:
                return None
        return result

    def _eq(self, other, sbs, temporary):
        if isinstance(other, Var):
            return other._eq(self, sbs, temporary)
        if type(self) != type(other) or len(self.args) != len(other.args) or \
                self.value != other.value:
            return None
        for a, b in zip(self.args, other.args):
            temporary = a._eq(b, sbs, temporary)
            if not temporary:
                return None
        return temporary

    def eq(self, other, sbs=None):
        r = self._eq(other, sbs, {})
        return Substitution(sbs, r) if r else None

    def unify(self, other, sbs=None):
        r = self._unify(other, sbs, {})
        return Substitution(sbs, r) if r else None

    def __str__(self):
        res = type(self).__name__ if self.value is None else str(self.value)
        if len(self.args) > 0:
            res = res + "(" + (",".join(str(x) for x in self.args)) + ")"
        return res

    def __call__(self, *args, **kwargs):
        if len(self.args) > 0:
            raise Exception("Cannot instantiate {}".format(self))
        return type(self)(*args, value=self.value)

    def substitute(self, sbs):
        args = [x.substitute(sbs) for x in self.args]
        result = type(self)(*args, value=self.value)
        return result

    def occur_check(self, var, sbs):
        for x in self.args:
            if x.occur_check(var, sbs):
                return True
        return False


class Var(object):
    count = 0

    def __init__(self):
        self.count = Var.count
        Var.count += 1

    def leq(self, other, sbs):
        if isinstance(other, Var)and other.count == self.count:
            return True
        if self.count in sbs:
            return other.leq(sbs[self.count], sbs)
        return False

    def _unify(self, other, base, result):
        if isinstance(other, Var) and other.count == self.count:
            return result
        if base is not None and self.count in base:
            return other._unify(base[self.count], base, result)
        if other.occur_check(self, base):
            return None
        result[self.count] = other
        return result

    def _eq(self, other, sbs, temporary):
        if isinstance(other, Var) and other.count == self.count:
            return temporary
        if sbs is not None and self.count in sbs:
            return other._eq(sbs[self.count], sbs, temporary)
        if not isinstance(other, Var):
            return None
        temporary[self.count] = other
        return temporary

    def __str__(self):
        return "x_%d"%self.count

    def substitute(self, sbs):
        res = sbs.get(self.count, None)
        if not res:
            res = Var()
            sbs[self.count] = res
        return res

    def occur_check(self, var, sbs):
        if self.count == var.count:
            return True
        if sbs and self.count in sbs:
            return sbs[self.count].occur_check(var, sbs)
        return False


class Predicate(Term):
    def __init__(self, name, *args):
        super(Predicate, self).__init__(*args, value=name)

    def negate(self):
        return Not(self)

    def substitute(self, sbs):
        args = [x.substitute(sbs) for x in self.args]
        result = type(self)(self.value, *args)
        return result


class Disjunct(Term):
    def __init__(self, *args):
        super(Disjunct, self).__init__(*args, value=" ∨ ")

    def __str__(self):
        return self.value.join(str(x) for x in self.args)

    def __add__(self, other):
        return Disjunct(args=self.args+other.args)

    def negate(self):
        c = Conjunct()
        c.args = [x.negate() for x in self.args]
        return c

    def substitute(self, sbs):
        args = [x.substitute(sbs) for x in self.args]
        result = type(self)(*args)
        return result

    def _resolve_predicate(self, predicate, sbs):
        result = []
        np = predicate.negate()
        for i, p in enumerate(self.args):
            unification = np.unify(p, sbs)
            if unification:
                x1 = self.args[:i] if i>0 else []
                x2 = self.args[i+1:] if i+1<len(self.args) else []
                x = Disjunct()
                x.args = list(x1) + list(x2)
                result.append(x.substitute(unification))
        #print(
        #    "result of _predicate resolving {} <<%%>> {} IS {}"
        #    .format(np, self, [str(x) for x in result])
        #)
        return result

    def resolve(self, disjunct, sbs):
        result = []
        for i, p in enumerate(disjunct.args):
            temp = self._resolve_predicate(p, sbs)
            if temp:
                x1 = disjunct.args[:i] if i>0 else []
                x2 = disjunct.args[i+1:] if i+1<len(disjunct.args) else []
                for z in temp:
                    z.args = list(z.args) + list(x1) + list(x2)
                result = result + temp
        return result


class Conjunct(Term):
    def __init__(self, *args):
        super(Conjunct, self).__init__(*args, value=" ∧\n")

    def __str__(self):
        return self.value.join(str(x) for x in self.args)

    def negate(self):
        c = Disjunct()
        c.args = [x.negate() for x in self.args]
        return c

    def substitute(self, sbs):
        args = [x.substitute(sbs) for x in self.args]
        result = type(self)(*args)
        return result


class Not(Predicate):
    def __init__(self, p):
        super(Not, self).__init__("¬", p)

    def negate(self):
        return self.args[0]

    def substitute(self, sbs):
        result = Not(self.args[0].substitute(sbs))
        return result


class Substitution(UserDict):
    def __init__(self, base, data=None):
        super(Substitution, self).__init__({} if data is None else data)
        self.base = base

    def __getitem__(self, item):
        result = self.data.get(item)
        if not result and self.base:
            result = self.base[item]
            self.data[item] = result
        return result

    def substitute(self, a, b):
        result = Substitution(self)
        result.data[a] = b
        return result

    def __str__(self):
        return "{" +\
               (",".join("{}:{}".format(x, y) for x, y in self.data.items())) +\
               "}"


class kb(object):
    def __init__(self):
        super(kb, self).__init__()
        self.known = deque()
        self.resolved = deque()

    def _include(self, s):
        for x in self.known:
            if x == s:
                return
        self.known.appendleft(s)
        print("________{}_______{}________".format(len(self.known),
                                                   len(self.resolved)))

    def tell(self, s):
        if isinstance(s, Disjunct):
            if not s.args:
                raise Exception("CONTRADICTION")
            print(">>>", s)
            self._include(s)
        elif isinstance(s, Conjunct):
            for x in s.args:
                self._include(x)
                print(">>>", x)

    def contradiction(self):
        sbs = Substitution(None)
        while len(self.known) != 0:
            x = self.known[-1]
            self.known.pop()
            for y in self.resolved:
                sentences = x.resolve(y, sbs)
                print(
                    "resolving {} <<X>> {} results {}"
                    .format(x, y, [str(x) for x in sentences])
                )
                for s in sentences:
                    self.tell(s)
            self.resolved.appendleft(x)


