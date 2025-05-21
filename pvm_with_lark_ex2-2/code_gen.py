from pvm_ast import Assign, Print, BinOp, Var, Number, If, While

class CodeGenerator:
    def __init__(self):
        self.code = []
        self.label_id = 0

    def emit(self, instr, arg=None):
        self.code.append((instr, arg) if arg is not None else (instr,))

    def new_label(self):
        label = f"L{self.label_id}"
        self.label_id += 1
        return label

    def set_label(self, label):
        self.code.append(("LABEL", label))

    def compile_expr(self, node):
        if isinstance(node, Number):
            self.emit("LOAD_CONST", node.value)
        elif isinstance(node, Var):
            self.emit("LOAD_NAME", node.name)
        elif isinstance(node, BinOp):
            self.compile_expr(node.left)
            self.compile_expr(node.right)
            opmap = {'+': "BINARY_ADD", '-': "BINARY_SUB", '*': "BINARY_MUL"}
            self.emit(opmap[node.op])

    def compile_stmt(self, stmt):
        if isinstance(stmt, Assign):
            self.compile_expr(stmt.expr)
            self.emit("STORE_NAME", stmt.name)
        elif isinstance(stmt, Print):
            self.compile_expr(stmt.expr)
            self.emit("PRINT")
        elif isinstance(stmt, If):
            else_label = self.new_label()
            end_label = self.new_label()
            self.compile_expr(stmt.cond)
            self.emit("JUMP_IF_FALSE", else_label)
            for s in stmt.then_block:
                self.compile_stmt(s)
            self.emit("JUMP", end_label)
            self.set_label(else_label)
            if stmt.else_block:
                for s in stmt.else_block:
                    self.compile_stmt(s)
            self.set_label(end_label)
        elif isinstance(stmt, While):
            start_label = self.new_label()
            end_label = self.new_label()
            self.set_label(start_label)
            self.compile_expr(stmt.cond)
            self.emit("JUMP_IF_FALSE", end_label)
            for s in stmt.body:
                self.compile_stmt(s)
            self.emit("JUMP", start_label)
            self.set_label(end_label)

    def compile_program(self, stmts):
        for stmt in stmts:
            self.compile_stmt(stmt)
