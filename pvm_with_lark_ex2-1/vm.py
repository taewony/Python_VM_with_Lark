class VirtualMachine:
    def __init__(self):
        self.stack = []
        self.env = {}

    def run(self, code):
        pc = 0
        while pc < len(code):
            instr = code[pc]
            op = instr[0]
            arg = instr[1] if len(instr) > 1 else None

            if op == "LOAD_CONST":
                self.stack.append(arg)
            elif op == "LOAD_NAME":
                self.stack.append(self.env[arg])
            elif op == "STORE_NAME":
                self.env[arg] = self.stack.pop()
            elif op == "BINARY_ADD":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)
            elif op == "BINARY_SUB":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a - b)
            elif op == "BINARY_MUL":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a * b)
            elif op == "PRINT":
                print(self.stack.pop())

            pc += 1
