from lark import Transformer

# ===== AST 노드 정의 =====
class Number:
    def __init__(self, value): self.value = value
    def __repr__(self): return f"Number({self.value})"

class Var:
    def __init__(self, name): self.name = name
    def __repr__(self): return f"Var({self.name})"

class BinOp:
    def __init__(self, left, op, right): self.left = left; self.op = op; self.right = right
    def __repr__(self): return f"BinOp({self.left} {self.op} {self.right})"

class Assign:
    def __init__(self, name, expr): self.name = name; self.expr = expr
    def __repr__(self): return f"Assign({self.name} = {self.expr})"

class Print:
    def __init__(self, expr): self.expr = expr
    def __repr__(self): return f"Print({self.expr})"

class If:
    def __init__(self, cond, then_block, else_block=None):
        self.cond = cond
        self.then_block = then_block
        self.else_block = else_block
    def __repr__(self): return f"If({self.cond}, {self.then_block}, {self.else_block})"

class While:
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body
    def __repr__(self): return f"While({self.cond}, {self.body})"

# ===== Transformer 구현 =====
class ASTBuilder(Transformer):
    def number(self, args): return Number(int(args[0]))
    def var(self, args): return Var(str(args[0]))
    def add(self, args): return BinOp(args[0], '+', args[1])
    def sub(self, args): return BinOp(args[0], '-', args[1])
    def mul(self, args): return BinOp(args[0], '*', args[1])
    def assign_stmt(self, args): return Assign(str(args[0]), args[1])
    def print_stmt(self, args): return Print(args[0])
    def if_stmt(self, args):
        if len(args) == 3:
            return If(args[0], args[1], args[2])
        else:
            return If(args[0], args[1])
    def while_stmt(self, args): return While(args[0], args[1])
    def stmt(self, args): return args[0]              # ✅ 추가
    def stmt_list(self, args): return args            # ✅ 리스트 반환
    def stmt_block(self, args): return args[1]        # ✅ 중첩 제거
