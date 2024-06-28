# VHDL Testbench Generator

---

A simple python script to generate a  VHDL testbench template  given an entity-architecture declaration  passed as argument(s) file(s).

# Demo

# Usage

- download the python script
  
  ```bash
   git clone https://github.com/Var7600/VHDL-TestBench.git
   cd VHDL-TestBench
  ```
  
  

- you can launch the script without a argument to see the Help and example of usages
  
  ```
  > python3 testbench_generator.py
  Usage: python3 testbench_generator.py [VHDL FILE]. . .
  
      generate testbench template of VHDL FILE(s) to current working directory
  
      Examples:
       python3 testbench_generator.py adder.vhdl mux.vhdl
  ```

- you can launch it with multiples VHDL files in arguments
  
  1. with one VHDL file
  
  2. with multiples VHDL files in arguments
     
     ```bash
     python3 testbench_generator.py examples\Decoder3_8.vhdl examples\Mux2_1.vhdl
     ```

# run unittest

```bash
python3 -m unittest tests\test_testbench_generator.py
```



# License

 **MIT License**
