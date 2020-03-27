"""CPU functionality."""


'''
RAM - an array of zeros and 1s
-  big array of bytes that can be retrieved by index, just like a regular array.
- 1 byte = 8 bits = 256 possible decimal values 

1 byte =8 bits

Each bit can contain either 0 or 1 so we have 2 possibilities for each bit and 2^8 =256 possibilities for 8 bits and the numbers are from 0 to 255 .

- Use hex (0 to FF) to represent large binary numbers 
- Assuming there are eight bits in one byte (and historically, that hasn’t always been the case), then the number of unique values you can represent using one eight-bit byte is 2828 or 256. The values in decimal range from 0 through 255 (i.e., the bit patterns ranging from 00000000 through 11111111).

Register- baked into hardware, very fast, but small and can only hold 1 word
Word-

LDI - load 'immediate', store a value in a register or 'set this register this value' 
PRN - a psuedo-instruction that prints the nuemric value stored in a register
HLT - halt the CPU and exit the emulator
'''



import sys

LDI = 0b10000010
PRN= 0b01000111 # PRN R0
HLT = 0b00000001 # HLT
MUL = 0b10100010
ADD = 0b10100000    
SUB = 0b10100011    

# 10000010 # LDI R0,8
# 00000000
# 00001000
# 10000010 # LDI R1,9
# 00000001
# 00001001
# 10100010 # MUL R0,R1
# 00000000
# 00000001
# 01000111 # PRN R0
# 00000000
# 00000001 # HLT



class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU.
        
        Add list properties to the CPU class to hold 256 bytes of memory and 8 general-purpose registers.
        - CPU Instruction
        - CPU Register
        -  RAM
        - CPU Program Counter

        """
        self.pc = 0 # Program counter/current instructor
        self.ir = None #Instruction Register,part of a CPU's control unit that holds the currently running instruction
        
        self.ram = [0] * 256  # Init RAM - 1 8-bit byte can store 256 possible values (0 to 255 in decimal or 0 to FF in hex base16

        self.reg = [0]* 8 #preallocate our register with 8, R0 -> R7
        self.halted = False 
        self.instruction = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100000: self.ADD
        } 

        self.sp = 7 #stack pointer location in registers
        self.reg[self.sp] = 0xF4 #initialize stack pointer at sp (7) to 0xF4

    def load(self, filename):
        """Load a program into memory."""
        #First method called from ls8
        address = 0

        try:
            with open(filename) as f:
                for line in f:
                    #ignore comments
                    comment_split = line.split("#")

                    #Strip whitespace
                    num = comment_split[0].strip()

                    #Ignore blank lines
                    if num == '':
                        continue 

                    
                    # val = eval(f"0b{num}")
                    val = int(num, 2) #base 2
                    print(f'num: {num}, val: {val}')
                    self.ram_write(address, val)

                    print(f"RAM has been written to ---> val: {val}, address: {address}")
        
                    address += 1

        except FileNotFoundError:
            print(f" {sys.argv[0]}: {filename}not found")
            sys.exit(2)

        f.close()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        #Arithmetic and Logic

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL": 
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")


    # MAR: Memory Address Register, holds the memory address we're reading or writing
    # MDR: Memory Data Register, holds the value to write or the value just read
    def ram_read(self, MAR):
        '''
        ram_read() should accept the address to read and return the value stored there.
        '''
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        '''
        raw_write() should accept a value to write, and the address to write it to.
        '''
        self.ram[MAR] = MDR 

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc, #0
            #self.fl, #Flags
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def HLT(self):
        self.halted = True 
        self.pc +=1
        sys.exit(0)

    def PRN(self):
        reg = self.ram_read(self.pc + 1)
        print(self.reg[reg])
        self.pc += 2

    def MUL(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("MUL", reg_a, reg_b )
        self.pc += 3 
    
    def ADD(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("ADD", reg_a, reg_b)
        self.pc += 3

    def LDI(self): 
        '''
        Set the value of a register to an integer
        Takes 3 args 1) immediate 2) register number 3) 8 bit immediate value 
        '''
        reg = self.ram_read(self.pc + 1)
        num = self.ram_read(self.pc + 2)
        #write to register
        self.reg[reg] = num
        self.pc += 3  

    def PUSH(self, MDR=None):
        '''
        PUSH register-
        Pushes the value in the given register on the stack - arg: MDR (memory data register)
        '''
        #Decrement SP by 1
        self.reg[self.sp] -= 1 

        #Get register arg from push
        data = MDR if MDR else self.reg[self.ram_read(self.pc + 1)]
        
        #Copy the value in the given register to the address pointed at by SP 
        # 
        
        self.ram_write(self.reg[self.sp], data)
        #Increment program counter by 2
        self.pc +=2
      
    def POP(self):
        '''
        POP register -
        Pops the value at the top of the stack into the given register
        '''
        #Get register arg from push 
        reg_a = self.ram_read(self.pc + 1)

        #Copy the value from the address pointed to by SP to the given register
        val = self.ram_read(self.reg[self.sp])

        #Copy the value - i.e. at register, add the value
        self.reg[reg_a] = val 
        #Increment SP
        self.reg[self.sp] +=1
        #Increment program counter by 2
        self.pc += 2

    def CALL(self):
        '''
        CALL register- Calls a subroutine (function) at the address stored in the register.

        1. The address of the instruction directly after CALL is pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.
        2. The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location.
        '''
        self.PUSH(self.pc+2)
        self.pc = self.reg[self.ram_read(self.pc-1)]

    def RET(self):
        '''
        RET- Return from subroutine.
        Pop the value from the top of the stack and store it in the PC.

        '''

        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def run(self):
        """Run the CPU."""

        # LDI - load 'immediate', store a value in a register or 'set this register this value' 
        # PRN - a psuedo-instruction that prints the nuemric value stored in a register
        # HLT - halt the CPU and exit the emulator

        #Flag that says if our program is running or not
        running = True 

        # a = self.ram_read(self.pc + 1)
        # b = self.ram_read(self.pc + 2)

        #While not halted..
        while not self.halted:
            #Get the instruction from ram and store in the local instructor register
            instruction = self.ram[self.pc]
            self.instruction[instruction]()

            # If instruction is HLT handle
            # if instruction == HLT or instruction == LDI or instruction == PRN or instruction == MUL or instruction == PUSH or instruction == POP: 
            #     self.instruction[instruction]()
            # else:
            #     raise Exception(f"Error: Instruction {instruction} does not exist")
            #     sys.exit(1)

            
