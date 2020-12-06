
class IntCodeComputer:
    
    def __init__(self, memory, ptr=0, debug=False):
        self.memory = memory
        self.ptr = ptr
        self.__debug = debug
        self.operations = {
            1:  self.add,
            2:  self.multiply,
            3:  self.user_input,
            4:  self.user_output,
            5:  self.jump_if_true,
            6:  self.jump_if_false,
            7:  self.less_than,
            8:  self.equals,
            99: self.stop
        }

    # First we need to support parameter mode
    def parse_operation(self, oper):
        value = "{:05}".format(oper)
        a = int(value[0])
        b = int(value[1])
        c = int(value[2])
        op = int(value[3:])

        return (op, c, b, a)
    
    def format_op(self, op, input_params):
        name = self.operations[op[0]].__name__.upper()
        mode = ""
        for i in range(0, input_params):
            mode += "D" if op[i+1] == 1 else "I"
        return "{} {}".format(name, mode)
    
    def read_memory(self, op, input_params, output_params=0):
        mem_slice = self.memory[self.ptr:self.ptr+input_params+output_params+1]
        
        if self.__debug:
            print("{:3} {} {}".format(self.ptr, 
                                  self.format_op(op, input_params),mem_slice[1:]))
        
        output = []
        for i in range(1, input_params + 1):
            m = mem_slice[i]
            if op[i] == 0:
                m = self.memory[m]
            output.append(m)

        for i in range(input_params+1, input_params+output_params+1):
            m = mem_slice[i]
            output.append(m)
            
        if self.__debug:
            print("    IN: {} OUT: {}".format(output[0:input_params], output[input_params:input_params+output_params]))
        
        if len(output) == 1:
            return output[0]
        else:
            return output
        
    def write_memory(self, ptr, value):
        if self.__debug:
            print("    WRITE: ptr={} value={}".format(ptr, value))
        self.memory[ptr] = value

    def add(self, op):
        params = 3
        a, b, c = self.read_memory(op, params-1, 1)
        self.write_memory(c, a + b)
        return self.ptr + params + 1

    def multiply(self, op):
        params = 3
        a, b, c = self.read_memory(op, params-1, 1)
        self.write_memory(c, a * b)
        return self.ptr + params + 1
    
    def jump_if_true(self, op):
        params = 2
        a, b = self.read_memory(op, params)
        return self.ptr + params + 1 if a == 0 else b

    def jump_if_false(self, op):
        params = 2
        a, b = self.read_memory(op, params)
        return self.ptr + params + 1 if a != 0 else b

    def less_than(self, op):
        params = 3
        a, b, c = self.read_memory(op, params-1, 1)
        self.write_memory(c, 1 if a < b else 0)
        return self.ptr + params + 1
    
    def equals(self, op):
        params = 3
        a, b, c = self.read_memory(op, params-1, 1)
        self.write_memory(c, 1 if a == b else 0)
        return self.ptr + params + 1

    def user_input(self, op):
        """
        Checks to see if input is available. 
        
        If input returns None then the computer halts until restarted
        """
        params = 1
        a = self.read_memory(op, 0, params)
        
        input_value = self.input_value()
        if input_value is None:
            return {"ptr": self.ptr, "yield": True}
        else:
            self.write_memory(a, int(input_value))
            return self.ptr + params + 1

    def user_output(self, op):
        params = 1
        a = self.read_memory(op, params)
        self.output_value(a)
        return {"ptr": self.ptr + params + 1, "yield": True}

    def stop(self, op):
        self.read_memory(op, 0)
        return -1

    def execute(self):
        op = self.parse_operation(self.memory[self.ptr])
        operation = self.operations[op[0]]
        return operation(op)
    
    def run(self):
        if self.__debug:
            print("-----")
        
        while True:
            out = self.execute()
            try:
                self.ptr = out["ptr"]
                if out.get("yield", False):
                    return -2
            except TypeError:
                self.ptr = out

            if self.ptr < 0:
                return self.ptr
        

    def input_value(self):
        return input()
    
    def output_value(self, a):
        print("OUTPUT:", a)