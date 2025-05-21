class VirtualMachine:
    def __init__(self):
        self.stack = []
        self.env = {}
        self.labels = {}
        self.pc = 0

    def resolve_labels(self, code):
        labels = {}
        new_code = []
        for i, instr in enumerate(code):
            if instr[0] == "LABEL":
                labels[instr[1]] = len(new_code)
            else:
                new_code.append(instr)
        return new_code, labels

    def run(self, code):
        code, self.labels = self.resolve_labels(code)
        self.pc = 0
        while self.pc < len(code):
            instr = code[self.pc]
            op = instr[0]
            arg = instr[1] if len(instr) > 1 else None

            if op == "LOAD_CONST":
                self.stack.append(arg)
            elif op == "LOAD_NAME":
                self.stack.append(self.env.get(arg, 0))
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
            elif op == "JUMP_IF_FALSE":
                cond = self.stack.pop()
                if not cond:
                    self.pc = self.labels[arg]
                    continue
            elif op == "JUMP":
                self.pc = self.labels[arg]
                continue

            self.pc += 1
