from lark import Lark
from pvm_ast import ASTBuilder
from code_gen import CodeGenerator
from vm import VirtualMachine
from pprint import pprint

grammar = """
    stmt_list: stmt+
    stmt: assign_stmt
        | print_stmt
        | if_stmt
        | while_stmt

    assign_stmt: NAME "=" expr           -> assign_stmt
    print_stmt: "print" "(" expr ")"     -> print_stmt
    if_stmt: "if" expr ":" stmt_block ("else" ":" stmt_block)? -> if_stmt
    while_stmt: "while" expr ":" stmt_block                    -> while_stmt

    LBRACE: "{"      // ← 추가
    RBRACE: "}"      // ← 추가
    stmt_block: LBRACE stmt_list RBRACE
    
    ?expr: expr "+" term                 -> add
         | expr "-" term                 -> sub
         | term
    ?term: term "*" factor               -> mul
         | factor
    ?factor: NUMBER                      -> number
           | NAME                        -> var
           | "(" expr ")"

    %import common.CNAME -> NAME
    %import common.NUMBER
    %import common.WS
    %ignore WS    
"""

sample_code = """
a = 3
b = 0
while a: {
    b = b + a
    a = a - 1
}
if b: {
    print(b)
} else: {
    print(0)
}
"""

# 1. 파싱
parser = Lark(grammar, parser="lalr", start="stmt_list")
tree = parser.parse(sample_code)

print("=== Parse Tree ===")
print(tree.pretty())

# 2. AST 생성
ast = ASTBuilder().transform(tree)

print("\n=== AST ===")
pprint(ast)

# 3. 바이트코드 생성
gen = CodeGenerator()
gen.compile_program(ast)

print("\n=== Bytecode ===")
for instr in gen.code:
    print(instr)

# 4. 실행
print("\n=== 결과 ===")
vm = VirtualMachine()
vm.run(gen.code)
