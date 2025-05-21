class Number:
    def __init__(self, value): self.value = int(value)
    def __repr__(self): return f"Number({self.value})"

class Var:
    def __init__(self, name): self.name = name
    def __repr__(self): return f"Var({self.name})"

class BinOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self): return f"BinOp({self.left} {self.op} {self.right})"

class Assign:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr
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

from lark import Transformer

class ASTBuilder(Transformer):
    def number(self, n): return Number(int(n[0]))
    def var(self, v): return Var(str(v[0]))
    def paren_expr(self, p): return p[0]
    def assign_stmt(self, a): return Assign(a[0].value, a[1])
    def print_stmt(self, p): return Print(p[0])
    def if_stmt(self, i):
        if len(i) == 3: return If(i[0], i[1], i[2])
        else: return If(i[0], i[1])
    def while_stmt(self, w):
        # print("while_stmt input:", w)
        return While(w[0], w[1])

    def flatten_and_transform(self, items):
        from lark.tree import Tree
        result = []
        for a in items:
            if isinstance(a, Tree):
                v = self.transform(a)
                if v is None:
                    continue
                if isinstance(v, list):
                    result.extend(v)
                else:
                    result.append(v)
            elif isinstance(a, list):
                result.extend(self.flatten_and_transform(a))
            else:
                if a is not None:
                    result.append(a)
        return result

    def stmt_block(self, s):
        # print("stmt_block raw input:", s)
        # s가 [stmt_list] 형태라면
        if len(s) == 1:
            items = s[0]
        elif len(s) == 3:
            items = s[1]
        else:
            items = []
        # print("stmt_block items:", items)
        return self.flatten_and_transform(items)

    def stmt_list(self, args):
        return self.flatten_and_transform(args)

    def stmt(self, args):
        # stmt는 보통 단일 문장 노드를 감싸는 역할이므로, 내부 값만 반환
        return args[0]

    def start(self, args):
        return self.flatten_and_transform(args)

    def expr(self, args):
        # 이진 연산자 처리
        if len(args) == 1:
            return args[0]
        current = args[0]
        for i in range(1, len(args), 2):
            op = args[i]
            op_str = op.value if hasattr(op, 'value') else str(op)
            right = args[i+1]
            current = BinOp(current, op_str, right)
        return current

    def term(self, args):
        if len(args) == 1:
            return args[0]
        current = args[0]
        for i in range(1, len(args), 2):
            op = args[i]
            op_str = op.value if hasattr(op, 'value') else str(op)
            right = args[i+1]
            current = BinOp(current, op_str, right)
        return current

    def assign_stmt(self, a): 
        return Assign(a[0].value, a[1])

    def binop(self, args):
        left = args[0]
        op = args[1].value if hasattr(args[1], 'value') else str(args[1])
        right = args[2]
        return BinOp(left, op, right)