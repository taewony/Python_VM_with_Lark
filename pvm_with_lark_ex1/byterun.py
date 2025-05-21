class Interpreter:
    def __init__(self):
        self.stack = []
        self.environment = {}

        self.num_fns = {'LOAD_VALUE'}
        self.name_fns = {'STORE_NAME', 'LOAD_NAME'}

    def run(self, program):
        instructions = program['instructions']
        numbers = program['numbers']
        names = program['names']
        for instruction, arg in instructions:
            if instruction in self.num_fns:
                getattr(self, instruction)(numbers[arg])
            elif instruction in self.name_fns:
                getattr(self, instruction)(names[arg])
            else:
                getattr(self, instruction)()

    def clear(self):
        self.stack = []
        self.environment = {}

    def LOAD_VALUE(self, number):
        self.stack.append(number)

    def PRINT_ANSWER(self):
        answer = self.stack.pop()
        print(answer)

    def ADD_TWO_VALUES(self):
        x = self.stack.pop()
        y = self.stack.pop()
        self.stack.append(x+y)

    def STORE_NAME(self, name):
        val = self.stack.pop()
        self.environment[name] = val

    def LOAD_NAME(self, name):
        val = self.environment[name]
        self.stack.append(val)

def test1():
    instructions = [
            ("LOAD_VALUE", 0),
            ("LOAD_VALUE", 1),
            ("ADD_TWO_VALUES", None),
            ("LOAD_VALUE", 2),
            ("ADD_TWO_VALUES", None),
            ("PRINT_ANSWER", None),
            ]
    numbers = [7, 5, 8]
    names = []
    program = {'instructions':instructions, 'numbers':numbers, 'names':names}
    return program

def test2():
    instructions = [
            ('LOAD_VALUE', 0),
            ('STORE_NAME', 0),
            ('LOAD_VALUE', 1),
            ('STORE_NAME', 1),
            ('LOAD_NAME', 0),
            ('LOAD_NAME', 1),
            ('ADD_TWO_VALUES', None),
            ('PRINT_ANSWER', None),
            ]
    numbers = [1, 2]
    names = ['a', 'b']
    program = {'instructions':instructions, 'numbers':numbers, 'names':names}
    return program

if __name__=='__main__':
    program1 = test1()
    program2 = test2()
    
    interpreter = Interpreter()
    interpreter.run(program1)
    interpreter.clear()
    interpreter.run(program2)