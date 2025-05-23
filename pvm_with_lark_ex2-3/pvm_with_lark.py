from lark import Lark
from pvm_ast import *
from code_gen import CodeGenerator
from vm import VirtualMachine

# 파서 초기화
with open("grammar.lark") as f:
    grammar = f.read()
parser = Lark(grammar, parser="lalr")

# 샘플 코드 파싱
sample_code = """
a = 3
b = 0
while a {
    b = b + a
    a = a - 1
}
if b {
    print(b)
} else {
    print(0)
}
if a { print(a) }
"""

tree = parser.parse(sample_code)
# print(tree.pretty())  # stmt_block 구조 확인

def flatten(lst):
    for item in lst:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

# AST 변환
ast_builder = ASTBuilder()
ast = ast_builder.transform(tree)

def flatten_and_transform_all(ast, ast_builder):
    from lark.tree import Tree
    # Tree 객체가 남아있으면 계속 변환
    while isinstance(ast, Tree):
        ast = ast_builder.transform(ast)
    if isinstance(ast, list):
        result = []
        for item in ast:
            # item이 Tree이거나 list일 때만 재귀, 아니면 그대로 추가
            if isinstance(item, (Tree, list)):
                result.extend(flatten_and_transform_all(item, ast_builder))
            else:
                result.append(item)
        return result
    else:
        return [ast]

ast = flatten_and_transform_all(ast, ast_builder)

print("\n=== AST ===")
from pprint import pprint
pprint(ast)

# === 바이트코드 생성
codegen = CodeGenerator()
codegen.compile_program(ast)
bytecode = codegen.code

print("\n=== Bytecode ===")
for instr in bytecode:
    print(instr)
    
print("\n=== VM run ===")
vm = VirtualMachine()
vm.run(bytecode)