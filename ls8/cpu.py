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
# print(f" LDI: {LDI}, PRN: {PRN}, HLT: {HLT}" )
MUL = 0b10100010

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
        # # For now, we've just hardcoded a program:
        # LDI = 0b10000010
        # PRINT_NUM = 0b01000111 #prints R0
        # HLT = 0b00000001

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


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
        pass
    def PRN(self):
        pass
    def MUL(self):
        pass 
    def LDI(self):
        pass

    def run(self):
        """Run the CPU."""

        # LDI - load 'immediate', store a value in a register or 'set this register this value' 
        # PRN - a psuedo-instruction that prints the nuemric value stored in a register
        # HLT - halt the CPU and exit the emulator

        #Flag that says if our program is running or not
        running = True 

        while running:
            #Get the instruction from ram and store in the local instructor register
            instruction = self.ram[self.pc]
     
            # self.trace()
            
            # If instruction is HLT handle
            if instruction == HLT: 
                running = False 
                #Exit the loop
                sys.exit(0)
                self.pc += 1


            # If instruction is LDI handle
            elif instruction == LDI:
                '''
                Set the value of a register to an integer
                Takes 3 args 1) immediate 2) register number 3) 8 bit immediate value 
                
                '''
                reg = self.ram_read(self.pc + 1)
                num = self.ram_read(self.pc + 2)
                #write to register
                self.reg[reg] = num
                # print(f'reg:{reg}, num: {num}')
                self.pc += 3 

            # If instruction is PRN handle 
            elif instruction == PRN:
                reg = self.ram_read(self.pc + 1)
                print(self.reg[reg])
                self.pc += 2

            ##extract out
            elif instruction == MUL:
                reg_a = self.ram_read(self.pc + 1)
                reg_b = self.ram_read(self.pc + 2)
                self.alu("MUL", reg_a, reg_b )
                self.pc += 3

            else:
                raise Exception(f"Error: Instruction {instruction} does not exist")
                sys.exit(1)


