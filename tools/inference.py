from tools.equations import Equation, solve_set_of_equations, apply_system
from tools.terrors import InconsistentSystemError
from tools.tstructure import *
from tools.utils import rename_all_abstractions, get_free_vars


class ClassicInferer:
    def __init__(self):
        self.defined_vars = {}

    def __get_type__(self, exp: Expression, last_var: int) -> (int, list, TType):
        """
        Get list of equations and type corresponding to given expression.
        Assumed that all variables is already renamed.

        :param exp: given expression
        :param last_var: next free variable
        :return: tuple(next free variable, list of equations, type)
        """
        if isinstance(exp, Var):
            self.defined_vars[exp] = TVar("t" + exp.name)
            return last_var, [], TVar("t" + exp.name)
        elif isinstance(exp, Abstraction):
            resort = None
            if exp.variable in self.defined_vars:
                resort = self.defined_vars[exp.variable]

            temp = self.__get_type__(exp.expression, last_var)

            if resort is None:
                if exp.variable in self.defined_vars:
                    del self.defined_vars[exp.variable]
            else:
                self.defined_vars[exp.variable] = resort

            return last_var, temp[1], TImpl(TVar("t" + exp.variable.name), temp[2])
        elif isinstance(exp, Applique):
            left = self.__get_type__(exp.left, last_var)
            right = self.__get_type__(exp.right, left[0])
            new_var = TVar("t" + str(right[0]))

            result_list = left[1] + right[1]
            result_list.append(Equation(left[2], TImpl(right[2], new_var)))
            return right[0] + 1, result_list, new_var
        else:
            raise Exception("Unknown type of" + str(exp))

    def get_type(self, exp: Expression) -> TType:
        """
        Get type of given expression

        :param exp: given expression
        :return: tuple(context, resulting type)
        """
        temp = self.__get_type__(rename_all_abstractions(exp), 0)
        try:
            eq_set = solve_set_of_equations(temp[1])
            for var in self.defined_vars:
                self.defined_vars[var] = apply_system(self.defined_vars[var], eq_set)
            return apply_system(temp[2], eq_set)
        except InconsistentSystemError:
            return None

    def get_type_with_context(self, exp: Expression) -> (dict, TType):
        """
        Get type of given expression and context of defined variables
        """
        self.defined_vars = {}
        # free_vars = get_free_vars(exp)
        # context = {}
        # for var in free_vars:
        #     context[var] = self.defined_vars[var]
        #
        return self.defined_vars, self.get_type(exp)


def __rename__(exp: TType, last_var: int, used: dict) -> (TType, int, dict):
    """
    Rename all variables in given expression in the same order every time.
    Variables get such names: t1, t2, t3 ...

    :param exp: given expression
    :param last_var: next free variable
    :param used: dictionary of renamed variables
    :return: renamed type
    """
    if isinstance(exp, TVar):
        if exp.name in used:
            return TVar(used[exp.name]), last_var, used
        else:
            used[exp.name] = "t" + str(last_var)
            return TVar(used[exp.name]), last_var + 1, used
    elif isinstance(exp, TImpl):
        left = __rename__(exp.left, last_var, used)
        right = __rename__(exp.right, left[1], left[2])
        return TImpl(left[0], right[0]), right[1], right[2]
    else:
        return None


def __is_eq__(exp1: TType, exp2: TType) -> bool:
    """
    Check if twp types is equivalent.

    :param exp1: first type
    :param exp2: second type
    :return: True is types is equivalent
    """
    return __rename__(exp1, 0, {})[0] == __rename__(exp2, 0, {})[0]


def test():
    def test_if_none(exp: Expression):
        print("Testing expression '{0}': expression cannot have a type".format(exp))
        res = ClassicInferer().get_type(exp)
        print("Result is {0}".format(res))
        assert res is None
        print("Passed\n")

    def test_if_same(exp: Expression, result: TType):
        print("Testing expression '{0}': expression must have type '{1}'".format(exp, result))
        res = ClassicInferer().get_type(exp)
        print("Result is {0}".format(res))
        assert __is_eq__(res, result)
        print("Passed\n")

    t = TVar("t")

    x = Var("x")
    y = Var("y")
    f = Var("f")

    e1 = Abstraction(x, Applique(x, x))
    test_if_none(e1)

    e2 = Abstraction(
            f,
            Abstraction(
                    x,
                    Applique(
                            f,
                            Applique(f, x)
                    )
            ))
    test_if_same(e2, TImpl(TImpl(t, t), TImpl(t, t)))

    e3 = Abstraction(x, Applique(x, y))

if __name__ == "__main__":
    test()
