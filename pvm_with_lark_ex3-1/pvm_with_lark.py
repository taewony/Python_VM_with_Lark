from lark import Lark
from pvm_ast import *
from code_gen import CodeGenerator
from vm import VirtualMachine

# === 문법 불러오기 ===
with open("grammar.lark") as f:
    grammar = f.read()
parser = Lark(grammar, parser="lalr", start="start")

# === 샘플 코드 ===
sample_code = """
def add(x, y): {
    result = x + y
    print(result)
    return result
}

a = 5
b = 7
c = add(a, b)
print(c)
"""

# === 파싱
tree = parser.parse(sample_code)
print("=== Parse Tree ===")
print(tree.pretty())

# === AST 생성
ast_builder = ASTBuilder()
ast = ast_builder.transform(tree)

# Tree 또는 중첩 리스트 제거
def flatten_and_transform_all(ast, ast_builder):
    from lark.tree import Tree
    while isinstance(ast, Tree):
        ast = ast_builder.transform(ast)
    if isinstance(ast, list):
        result = []
        for item in ast:
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

print("\n=== Bytecode ===")
for instr in codegen.code:
    print(instr)

# === VM 실행
print("\n=== VM Result ===")
vm = VirtualMachine()
vm.run(codegen.code)
