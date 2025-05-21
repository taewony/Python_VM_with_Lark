from pvm_ast import Assign, Print, BinOp, Var, Number, If, While, FuncDef, FuncCall, Return

class CodeGenerator:
    def __init__(self):
        self.code = []
        self.label_id = 0
        self.function_defs = {}  # name -> label

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
        elif isinstance(node, FuncCall):
            for arg in node.args:
                self.compile_expr(arg)
            self.emit("CALL_FUNCTION", (node.name, len(node.args)))
        else:
            raise NotImplementedError(f"Unknown expr: {node}")

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
        elif isinstance(stmt, FuncDef):
            func_label = self.new_label()
            self.function_defs[stmt.name] = (stmt.params, func_label)
            self.emit("DEF_FUNC", (stmt.name, stmt.params, func_label))
            self.set_label(func_label)
            for s in stmt.body:
                self.compile_stmt(s)
            # 함수 바디에 Return이 없으면 None 반환
            if not has_return(stmt.body):
                self.emit("LOAD_CONST", None)
                self.emit("RETURN")
        elif isinstance(stmt, Return):
            self.compile_expr(stmt.value)
            self.emit("RETURN")
        else:
            raise NotImplementedError(f"Unknown statement: {stmt}")

    def compile_program(self, stmts):
        func_labels = {}
        # 1. 함수 정의를 먼저 DEF_FUNC로만 등록
        for stmt in stmts:
            if isinstance(stmt, FuncDef):
                func_label = self.new_label()
                self.function_defs[stmt.name] = (stmt.params, func_label)
                self.emit("DEF_FUNC", (stmt.name, stmt.params, func_label))
                func_labels[stmt.name] = func_label
        # 2. 함수 바디와 나머지 코드 컴파일
        for stmt in stmts:
            if isinstance(stmt, FuncDef):
                func_label = func_labels[stmt.name]
                end_label = self.new_label()
                self.emit("JUMP", end_label)  # 메인 흐름에서 함수 바디 건너뛰기
                self.set_label(func_label)
                for s in stmt.body:
                    self.compile_stmt(s)
                # 함수 바디에 Return이 없으면 None 반환
                if not has_return(stmt.body):
                    self.emit("LOAD_CONST", None)
                    self.emit("RETURN")
                self.set_label(end_label)
                # 함수 바디 컴파일 후 바이트코드 출력
                print(f"[DEBUG] After compiling function '{stmt.name}':")
                for i, instr in enumerate(self.code):
                    print(f"  {i}: {instr}")
            else:
                self.compile_stmt(stmt)
        # 전체 바이트코드 및 함수 레이블 정보 출력
        print("[DEBUG] Final bytecode:")
        for i, instr in enumerate(self.code):
            print(f"  {i}: {instr}")
        print("[DEBUG] Function labels:", func_labels)

def has_return(stmts):
    """stmt 리스트(중첩 포함)에 Return이 하나라도 있으면 True"""
    if isinstance(stmts, Return):
        return True
    if isinstance(stmts, list):
        return any(has_return(s) for s in stmts)
    # If, While 등 블록문 처리
    if hasattr(stmts, 'body'):
        if has_return(stmts.body):
            return True
    if hasattr(stmts, 'then_block'):
        if has_return(stmts.then_block):
            return True
    if hasattr(stmts, 'else_block'):
        if has_return(stmts.else_block):
            return True
    return False
