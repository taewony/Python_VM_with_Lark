from lark import Transformer, v_args

# === AST 노드 정의 ===

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

class FuncDef:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body
    def __repr__(self): return f"FuncDef({self.name}, {self.params}, {self.body})"

class FuncCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def __repr__(self): return f"FuncCall({self.name}, {self.args})"

class Return:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Return({self.value})"

# === ASTBuilder 구현 ===

class ASTBuilder(Transformer):
    def number(self, n): return Number(int(n[0]))
    def var(self, v): return Var(str(v[0]))
    def assign_stmt(self, a): return Assign(a[0].value, a[1])
    def print_stmt(self, p): return Print(p[0])

    def if_stmt(self, i):
        if len(i) == 3: return If(i[0], i[1], i[2])
        else: return If(i[0], i[1])

    def while_stmt(self, w):
        return While(w[0], w[1])

    def func_def(self, args):
        name = str(args[0])
        param_arg = args[1]
        body = args[2]
        # print(f"[DEBUG] func_def args: {args}")  # debug print
        # param_arg는 None(파라미터 없음) 또는 [Token('NAME', ...), ...]
        if param_arg is None:
            params = []
        else:
            params = [str(p) for p in param_arg]
        # print(f"[DEBUG] FuncDef name: {name}, params: {params}, body: {body}")  # debug print
        return FuncDef(name, params, body)

    def func_call(self, args):
        name = str(args[0])
        # args[1:]이 [[Var(a), Var(b)]] 형태일 수 있으므로 평탄화
        if len(args) > 1 and isinstance(args[1], list):
            return FuncCall(name, args[1])
        else:
            return FuncCall(name, args[1:])

    def param_list(self, args):
        return args

    def arg_list(self, args):
        return args

    def stmt_block(self, s):
        if len(s) == 1:
            items = s[0]
        elif len(s) == 3:
            items = s[1]
        else:
            items = []
        return self.flatten_and_transform(items)

    def stmt_list(self, args):
        return self.flatten_and_transform(args)

    def stmt(self, args):
        return args[0]

    def start(self, args):
        return self.flatten_and_transform(args)

    def expr(self, args):
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

    def add(self, items):
        left, right = items
        return BinOp(left, '+', right)

    def sub(self, items):
        left, right = items
        return BinOp(left, '-', right)

    def mul(self, items):
        left, right = items
        return BinOp(left, '*', right)

    def div(self, items):
        left, right = items
        return BinOp(left, '/', right)

    def return_stmt(self, items):
        # grammar.lark에서 return_stmt: "return" expr
        return Return(items[0])

    def expr_stmt(self, args):
        # 보통 단순 표현식 문장은 무시하거나, 필요하면 반환
        # 여기서는 아무것도 반환하지 않음 (None)
        return None

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
