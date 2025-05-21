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

            try:
                if op == "LOAD_CONST":
                    self.stack.append(arg)
                elif op == "LOAD_NAME":
                    if arg not in self.env:
                        raise RuntimeError(f"Undefined variable: {arg}")
                    self.stack.append(self.env[arg])
                elif op == "STORE_NAME":
                    if not self.stack:
                        raise RuntimeError("Stack underflow on STORE_NAME")
                    self.env[arg] = self.stack.pop()
                elif op == "BINARY_ADD":
                    if len(self.stack) < 2:
                        raise RuntimeError("Stack underflow on BINARY_ADD")
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
                    if not self.stack:
                        raise RuntimeError("Stack underflow on JUMP_IF_FALSE")
                    cond = self.stack.pop()
                    if not cond:
                        self.pc = self.labels[arg]
                        continue
                elif op == "JUMP":
                    self.pc = self.labels[arg]
                    continue
                else:
                    raise RuntimeError(f"Unknown opcode: {op}")
            except Exception as e:
                print(f"VM Error at pc={self.pc}, instr={instr}: {e}")
                break

            self.pc += 1
