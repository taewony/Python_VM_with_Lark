from lark import Lark, Transformer
# 문법 정의
grammar = r"""
    start: stmt+
    stmt: assign_stmt | print_stmt
    assign_stmt: NAME "=" expr           -> assign
    print_stmt: "print" "(" expr ")"     -> print

    ?expr: term
        | expr "+" term   -> add
        | expr "-" term   -> sub

    ?term: factor
        | term "*" factor -> mul

    ?factor: NUMBER        -> number
           | NAME          -> var
           | "(" expr ")"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""
# 인터프리터 정의
class Interpreter(Transformer):
    def __init__(self):
        self.env = {}

    def assign(self, args):
        name = str(args[0])
        value = self._eval(args[1])
        self.env[name] = value

    def print(self, args):
        value = self._eval(args[0])
        print(value)

    def add(self, args):
        return self._eval(args[0]) + self._eval(args[1])

    def sub(self, args):
        return self._eval(args[0]) - self._eval(args[1])

    def mul(self, args):
        return self._eval(args[0]) * self._eval(args[1])

    def number(self, args):
        return int(args[0])

    def var(self, args):
        name = str(args[0])
        if name in self.env:
            return self.env[name]
        raise NameError(f"Undefined variable: {name}")

    def _eval(self, tree):
        if isinstance(tree, int):
            return tree
        return self.transform(tree)
# 샘플 코드
sample_code = """
a = 10
b = 20
c = a + b * 2
print(c)
print(a - 5)
"""
# 파싱만 먼저
parser = Lark(grammar, parser="lalr")
tree = parser.parse(sample_code)
# Parse Tree 출력
print(tree.pretty())  # 파싱 트리 출력
# 인터프리터 실행
interpreter = Interpreter()
interpreter.transform(tree)