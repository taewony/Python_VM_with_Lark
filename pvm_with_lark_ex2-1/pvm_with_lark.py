from lark import Lark 
from pvm_ast import ASTBuilder
from code_gen import CodeGenerator
from vm import VirtualMachine
from pprint import pprint

grammar = """
    stmt_list: (assign_stmt | print_stmt)+
    assign_stmt: NAME "=" expr           -> assign_stmt
    print_stmt: "print" "(" expr ")"     -> print_stmt
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
a = 10
b = 20
c = a + b * 2
print(c)
print(a - 5)
"""

parser = Lark(grammar, parser="lalr", start="stmt_list")

# 1. 파시
tree = parser.parse(sample_code)

# 2. AST 생성
ast = ASTBuilder().transform(tree)
print("=== AST ===")
pprint(ast)

# 3. 바이트코드 컴파일
gen = CodeGenerator()
gen.compile_program(ast)
print("\n=== Bytecode ===")
for instr in gen.code:
    print(instr)
    
# 4. 실행
print("\n=== run ===")
vm = VirtualMachine()
vm.run(gen.code)
