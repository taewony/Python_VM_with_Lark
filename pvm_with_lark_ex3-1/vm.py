# 주요 변경점 요약 (Summary of Key Changes):
# 1. PC의 선행 증가 (Pre-increment of PC):
#    - 메인 루프에서 명령어 실행 *전에* 현재 프레임의 PC를 먼저 증가시킵니다.
#    - JUMP 계열 명령어는 PC를 직접 설정하여 선행 증가된 PC 값을 덮어씁니다.
# 2. 점프 및 컨텍스트 스위칭 (Jumps and Context Switching):
#    - CALL_FUNCTION 및 RETURN 명령어는 프레임 스택을 변경한 후 'continue'를 사용하여
#      루프를 다시 시작하고 새 현재 프레임에서 실행을 이어갑니다.
# 3. 전역 바이트코드 사용 (Global Bytecode Usage):
#    - 모든 프레임(메인 프레임, 함수 프레임)이 동일한 전역 바이트코드 배열을 참조합니다.
#    - resolve_labels를 통해 한 번 처리된 바이트코드를 VM 인스턴스 변수에 저장하고
#      모든 프레임 생성 시 이 코드를 사용합니다.
# 4. 오류 보고용 PC 저장 (PC storage for error reporting):
#    - 명령어 실행 전의 PC 값을 별도로 저장하여 오류 메시지 출력 시 정확한 위치를 표시합니다.

class Frame:
    def __init__(self, code, env, pc=0):
        self.code = code  # Should be the globally resolved bytecode array
        self.env = env    # Local environment for this frame
        self.stack = []   # Operand stack for this frame
        self.pc = pc      # Program Counter for this frame

class VirtualMachine:
    def __init__(self):
        self.frames = []              # Frame stack
        self.labels = {}              # Resolved labels (name -> pc_index in global_bytecode)
        self.functions = {}           # Registered functions (name -> (param_names, body_label_name))
        self.global_bytecode = []     # Stores the bytecode array after resolving labels (Global Bytecode Usage)

    def resolve_labels(self, code_with_labels):
        """
        Resolves LABEL instructions into a mapping and returns bytecode without labels.
        Labels are converted to PC indices in the new_code.
        """
        labels = {}
        new_code = []
        for instr in code_with_labels:
            if instr[0] == "LABEL":
                labels[instr[1]] = len(new_code) # Label name maps to its index in new_code
            else:
                new_code.append(instr)
        return new_code, labels

    def run(self, code_input):
        """
        Runs the provided bytecode.
        'code_input' is expected to be a list of instruction tuples, potentially with labels.
        """
        # Resolve labels and store the processed bytecode globally for all frames (Global Bytecode Usage)
        self.global_bytecode, self.labels = self.resolve_labels(code_input)
        self.functions = {}  # Reset functions if run is called multiple times

        # Create the main frame using the global bytecode
        main_frame = Frame(self.global_bytecode, {}, pc=0)
        self.frames.append(main_frame)

        while self.frames:
            current_frame = self.frames[-1]
            frame_index = len(self.frames) - 1

            # Check if current frame's PC is out of bounds (end of its code segment or program)
            if current_frame.pc >= len(current_frame.code): # current_frame.code is self.global_bytecode
                self.frames.pop() # Pop the completed frame
                if not self.frames: # If all frames are processed
                    print("[DEBUG] VM execution finished: All frames popped.")
                    break # Exit the VM loop
                print(f"[DEBUG] FRAME_POP: Popped frame. Current frame is now Frame {len(self.frames) -1}.")
                continue # Continue with the next frame (caller or next task)

            # PC storage for error reporting & fetching current instruction
            instr_pc_for_error = current_frame.pc
            instr = current_frame.code[instr_pc_for_error]

            # Pre-increment of PC: Advance PC for the current frame *before* executing the instruction.
            # Jumps or context switches (CALL, RETURN) will manage PC flow accordingly.
            current_frame.pc += 1

            op = instr[0]
            arg = instr[1] if len(instr) > 1 else None

            # Debug print for bytecode flow
            stack_top_str = str(current_frame.stack[-1]) if current_frame.stack else "EMPTY"
            print(f"[DEBUG] EXEC: PC={instr_pc_for_error} FRAME={frame_index} INSTR=({op}, {arg if arg is not None else ''}) STACK_TOP={stack_top_str}")

            try:
                if op == "LOAD_CONST":
                    current_frame.stack.append(arg)
                elif op == "LOAD_NAME":
                    value_found = False
                    # Search for the variable in the environment of frames from innermost to outermost
                    for f_search_idx, f_search in enumerate(reversed(self.frames)):
                        if arg in f_search.env:
                            current_frame.stack.append(f_search.env[arg]) # Push to current frame's stack
                            value_found = True
                            # print(f"[DEBUG] LOAD_NAME: Found '{arg}' = {f_search.env[arg]} in Frame {-f_search_idx-1} env.")
                            break
                    if not value_found:
                        raise RuntimeError(f"Undefined variable: {arg}")

                elif op == "STORE_NAME":
                    if not current_frame.stack:
                        raise RuntimeError("Stack underflow on STORE_NAME")
                    current_frame.env[arg] = current_frame.stack.pop() # Store in the current frame's environment

                elif op == "BINARY_ADD":
                    if len(current_frame.stack) < 2:
                        raise RuntimeError("Stack underflow for BINARY_ADD")
                    b = current_frame.stack.pop()
                    a = current_frame.stack.pop()
                    current_frame.stack.append(a + b)

                elif op == "BINARY_SUB":
                    if len(current_frame.stack) < 2:
                        raise RuntimeError("Stack underflow for BINARY_SUB")
                    b = current_frame.stack.pop()
                    a = current_frame.stack.pop()
                    current_frame.stack.append(a - b)

                elif op == "BINARY_MUL":
                    if len(current_frame.stack) < 2:
                        raise RuntimeError("Stack underflow for BINARY_MUL")
                    b = current_frame.stack.pop()
                    a = current_frame.stack.pop()
                    current_frame.stack.append(a * b)
                
                elif op == "PRINT":
                    if not current_frame.stack:
                        raise RuntimeError("Stack underflow for PRINT")
                    print(f"OUTPUT: {current_frame.stack.pop()}") # Clearly mark user-facing output

                elif op == "JUMP_IF_FALSE": # Jumps and Context Switching
                    if not current_frame.stack:
                        raise RuntimeError("Stack underflow for JUMP_IF_FALSE condition")
                    cond = current_frame.stack.pop()
                    if not cond:
                        target_pc = self.labels[arg]
                        # print(f"[DEBUG] JUMP_IF_FALSE: Condition FALSE. Jumping to PC={target_pc} (Label: {arg})")
                        current_frame.pc = target_pc # PC is set directly
                    # else:
                        # print(f"[DEBUG] JUMP_IF_FALSE: Condition TRUE. Proceeding to next instruction PC={current_frame.pc}")
                    # No 'continue' needed; loop will use the (potentially new) current_frame.pc

                elif op == "JUMP": # Jumps and Context Switching
                    target_pc = self.labels[arg]
                    # print(f"[DEBUG] JUMP: Jumping to PC={target_pc} (Label: {arg})")
                    current_frame.pc = target_pc # PC is set directly
                    # No 'continue' needed

                elif op == "DEF_FUNC":
                    name, params, label_name = arg
                    self.functions[name] = (params, label_name)
                    # print(f"[DEBUG] DEF_FUNC: Defined function '{name}' with params {params} at label '{label_name}'.")
                
                elif op == "CALL_FUNCTION": # Jumps and Context Switching
                    func_name, argc = arg
                    if func_name not in self.functions:
                        raise RuntimeError(f"Undefined function: {func_name}")
                    
                    param_names, label_name = self.functions[func_name]
                    
                    if len(param_names) != argc:
                        raise RuntimeError(f"Argument count mismatch in call to {func_name}. Expected {len(param_names)}, got {argc}")

                    if len(current_frame.stack) < argc:
                        raise RuntimeError(f"Stack underflow: not enough arguments on stack for function call {func_name}. Expected {argc}, got {len(current_frame.stack)}")
                    
                    args_values = [current_frame.stack.pop() for _ in range(argc)][::-1] # Pop in reverse order of appearance
                    new_env = dict(zip(param_names, args_values))
                    
                    # print(f"[DEBUG] CALL_FUNCTION: Calling '{func_name}' with args {args_values}. Caller PC was {instr_pc_for_error}, next is {current_frame.pc}.")

                    function_start_pc = self.labels[label_name]
                    new_function_frame = Frame(self.global_bytecode, new_env, pc=function_start_pc)
                    self.frames.append(new_function_frame)
                    # print(f"[DEBUG] FRAME_PUSH: Pushed new frame for '{func_name}'. Total frames: {len(self.frames)}.")
                    
                    continue # Must 'continue' to switch execution to the new_function_frame.
                
                elif op == "RETURN": # Jumps and Context Switching
                    return_value = current_frame.stack.pop() if current_frame.stack else None
                    
                    self.frames.pop() # Pop the current function's frame (callee)
                    
                    # print(f"[DEBUG] RETURN: Returning value {return_value}. Popped frame. Total frames: {len(self.frames)}.")

                    if self.frames: # If there is a caller frame remaining
                        caller_frame = self.frames[-1]
                        caller_frame.stack.append(return_value) # Push return value onto caller's stack
                        # print(f"[DEBUG] RETURN: Pushed return value to Frame {len(self.frames)-1}'s stack.")
                    
                    if not self.frames: # If that was the last frame (e.g., return from main script)
                        print(f"[DEBUG] RETURN: Last frame returned. Value: {return_value}")
                        break # Exit VM loop
                    
                    continue # Must 'continue' to switch execution back to the caller_frame.
                
                else:
                    raise RuntimeError(f"Unknown opcode: {op}")
            
            except IndexError as e: # Specifically for "pop from empty list" or other index errors
                print(f"VM Error (IndexError) in FRAME={frame_index} PC={instr_pc_for_error}, INSTR={instr}: {e}")
                break # Exit VM loop on error
            except Exception as e:
                print(f"VM Error in FRAME={frame_index} PC={instr_pc_for_error}, INSTR={instr}: {e}")
                break # Exit VM loop on error
