from lark import Transformer

# AST 노드 클래스들

class Number:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"

class Var:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Var({self.name})"

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinOp({self.left} {self.op} {self.right})"

class Assign:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def __repr__(self):
        return f"Assign({self.name} = {self.expr})"

class Print:
    def __init__(self, expr):
        self.expr = expr

    def __repr__(self):
        return f"Print({self.expr})"


# Lark Transformer → ASTBuilder

class ASTBuilder(Transformer):
    def number(self, args):
        return Number(int(args[0]))

    def var(self, args):
        return Var(str(args[0]))

    def add(self, args):
        return BinOp(args[0], '+', args[1])

    def sub(self, args):
        return BinOp(args[0], '-', args[1])

    def mul(self, args):
        return BinOp(args[0], '*', args[1])

    def assign_stmt(self, args):
        return Assign(str(args[0]), args[1])

    def print_stmt(self, args):
        return Print(args[0])

    def stmt_list(self, args):
        return args
