from pvm_ast import Assign, Print, BinOp, Var, Number

class CodeGenerator:
    def __init__(self):
        self.code = []

    def emit(self, instr, arg=None):
        if arg is not None:
            self.code.append((instr, arg))
        else:
            self.code.append((instr,))

    def compile_expr(self, node):
        if isinstance(node, Number):
            self.emit("LOAD_CONST", node.value)
        elif isinstance(node, Var):
            self.emit("LOAD_NAME", node.name)
        elif isinstance(node, BinOp):
            self.compile_expr(node.left)
            self.compile_expr(node.right)
            if node.op == '+':
                self.emit("BINARY_ADD")
            elif node.op == '-':
                self.emit("BINARY_SUB")
            elif node.op == '*':
                self.emit("BINARY_MUL")

    def compile_stmt(self, stmt):
        if isinstance(stmt, Assign):
            self.compile_expr(stmt.expr)
            self.emit("STORE_NAME", stmt.name)
        elif isinstance(stmt, Print):
            self.compile_expr(stmt.expr)
            self.emit("PRINT")

    def compile_program(self, stmts):
        for stmt in stmts:
            self.compile_stmt(stmt)
