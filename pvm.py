#!/usr/bin/env python2.7
import operator as op

class O(object):
    _REDUCIBLE = False

    def __repr__(self):
        return '<{}>'.format(self)

    def is_reducible(self):
        return self._REDUCIBLE

class Environment(dict): pass

class Variable(O):
    _REDUCIBLE = True

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def reduce(self, environment):
        return environment[self.name]

class Number(O):
    _REDUCIBLE = False

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Boolean(O):
    _REDUCIBLE = False

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class OPS(O):
    def __init__(self, n, f, xs):
        self.n = n
        self.f = f
        self.xs = xs

class AOPS(OPS):
    TYPE = None

    def __init__(self, n, f, value):
        super(AOPS, self).__init__(n, f, [value])

    def __str__(self):
        return '{} {}'.format(self.n, str(self.value))

    @property
    def value(self):
        return self.xs[0]

    def reduce(self, environment):
        if self.value.is_reducible():
            return self.__class__(self.value.reduce(environment))
        else:
            return self.TYPE(self.f(self.value))

class AlgebraAOPS(AOPS):
    TYPE = Number

class BooleanAOPS(AOPS):
    TYPE = Boolean

class BOPS(OPS):
    TYPE = None

    def __init__(self, n, f, left, right):
        super(BOPS, self).__init__(n, f, [left, right])

    def __str__(self):
        return '{} {} {}'.format(str(self.left), self.n, str(self.right))

    @property
    def left(self):
        return self.xs[0]

    @property
    def right(self):
        return self.xs[1]

    def reduce(self, environment):
        if self.left.is_reducible():
            return self.__class__(self.left.reduce(environment), self.right)
        elif self.right.is_reducible():
            return self.__class__(self.left, self.right.reduce(environment))
        else:
            return self.TYPE(self.f(self.left.value, self.right.value))

class AlgebraBOPS(BOPS):
    TYPE = Number

class BooleanBOPS(BOPS):
    TYPE = Boolean

class Add(AlgebraBOPS):
    _REDUCIBLE = True

    def __init__(self, left, right):
        super(Add, self).__init__('+', op.add, left, right)

class Sub(AlgebraBOPS):
    _REDUCIBLE = True

    def __init__(self, left, right):
        super(Sub, self).__init__('-', op.sub, left, right)

class Mul(AlgebraBOPS):
    _REDUCIBLE = True

    def __init__(self, left, right):
        super(Mul, self).__init__('*', op.mul, left, right)

class Div(AlgebraBOPS):
    _REDUCIBLE = True

    def __init__(self, left, right):
        super(Div, self).__init__('/', op.div, left, right)

class LT(BooleanBOPS):
    _REDUCIBLE = True

    def __init__(self, left, right):
        super(LT, self).__init__('<', op.lt, left, right)

class LE(BooleanBOPS):
    _REDUCIBLE = True

    def __init__(self, left, right):
        super(LE, self).__init__('<=', op.le, left, right)

class GT(BooleanBOPS):
    _REDUCIBLE = True

    def __init__(self, left, right):
        super(GT, self).__init__('>', op.gt, left, right)

class GE(BooleanBOPS):
    _REDUCIBLE = True

    def __init__(self, left, right):
        super(GE, self).__init__('>=', op.ge, left, right)

class And(BooleanBOPS):
    _REDUCIBLE = True

    def __init__(self, left, right):
        super(And, self).__init__('and', op.and_, left, right)

class Or(BooleanBOPS):
    _REDUCIBLE = True

    def __init__(self, left, right):
        super(Or, self).__init__('or', op.or_, left, right)

class Not(BooleanAOPS):
    _REDUCIBLE = True

    def __init__(self, value):
        super(Not, self).__init__('not', op.not_, value)

class Machine(object):
    def __init__(self, expression, environment):
        self.expression = expression
        self.environment = environment
        self.count = 0

    def step(self):
        self.expression = self.expression.reduce(self.environment)
        self.count += 1

    def run(self):
        while self.expression.is_reducible():
            self.print_current_status()
            self.step()
        self.print_current_status()
        return self.expression

    def print_current_status(self):
        print "[{}]: {}".format(self.count, self.expression)

if __name__ == '__main__':
    print "[!] Machine V0:"
    Machine(Add(Number(5),
                Mul(Number(10),
                    Number(5))),
            Environment()).run()

    print "[!] Machine V1:"
    Machine(Not(Or(LT(Number(5), Number(10)),
                   GE(Number(10), Number(22)))),
            Environment()).run()

    print "[!] Machine V2:"
    Machine(Variable("x"),
            Environment(x=Number(5))).run()
