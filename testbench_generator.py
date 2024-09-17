#!/usr/bin/env python3

# -----------------------------------------------------------------------------
# Name:        testbench_generator
# Purpose:     A program that  generates a testbench template of VHDL file(s)
# passed in argument
# python_version: 3.8.10
# Author:      DOUDOU DIAWARA
#
# Created:     16/02/2024
# License:     MIT License
# -----------------------------------------------------------------------------

"""
    This module generates a testbench template of a VHDL file(s) passed in Argument(s).

    Functions:
    parse_file(file_name):
        parse the VHDL file passed in Argument.

    component_interface(str):
        Extract the component declaration in the VHDL File(entity declaration).

    remove_directional_signals(str):
        Remove  directional signals "in" and "out" and "buffer" from the string.

    parse_signals(str):
        Get the input and output signal
        and generic constant declared in the entity VHDL file.

    map_signals(str):
        Map signals declaration to component.

    write_testbench(component):
        Write the testbench file of the component interface.

"""
import sys
import os
import re

class bcolors:
    """ colors foe the terminal """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    

def parse_file(file_name):
    """
        Parse the VHDL file to look for the entity declaration in the file.

        Args:
            file_name (file): the VHDL file to parse.
                if the VHDL file doesn't exit, the function will terminate.

        Returns:
            (str): the entity declaration of the VHDL file.

    """
    found_entity = False
    entity_lines = []
    try:
        with open(file_name, 'r', encoding="utf-8") as file:
            # reading file line by line
            for line in file:
                line = line.lower().strip()

                # line of the entity declaration
                if line.startswith("entity"):
                    found_entity = True

                if found_entity:
                    entity_lines.append(line)

                if found_entity and line.startswith("end"):
                    break

            if not found_entity:
                print(bcolors.WARNING + f"""not able to find the entity declaration in your VHDL file!
                      end of processing:  {file_name} """)
                return 0

        return "\n".join(entity_lines)

    except FileNotFoundError as e:
        print( bcolors.WARNING + "Unable to open the file " + file_name + ": " + str(e) + bcolors.ENDC)

    except PermissionError:
        print(bcolors.WARNING + "Permission denied! Unable to read the file."+ bcolors.ENDC)

    except Exception as e:
        print(bcolors.FAIL + f"An error occurred: {e}"+ bcolors.ENDC)

    return -1


def component_interface(entity_lines):
    """
       Return the component of the entity declaration.

        Args:
            entity_lines(str): entity declaration.

        Returns:
            (str):  the component to map
    """
    # replace entity by component  
    entity_lines_component =  entity_lines.replace("entity", "component")
    # to check if component end with "end <entity_name>" or "end component <entity_name>"
    if "end component" not in entity_lines_component:
        entity_lines_component = entity_lines_component.replace("end" , "end component")
   
    return entity_lines_component


def remove_directional_signals(signals):
    """
        Removes directional signals "in" and "out" and "buffer" from the string.

        Args:
            signals(str): the component interface.

        Returns:
            str: The content with directional signals removed.
  """

    words = signals.split()
    filtered_lines = []
    for word in words:
        if word.lower() not in ("in", "out", "buffer"):
            filtered_lines.append(word)

    return " ".join(filtered_lines)


def parse_signals(component):
    """
    Get the input and output signals and generic constants declared in the entity VHDL file.

    Args:
        component (str): The component declaration content

    Returns:
        String of the VHDL signal and generic constant to define in the testbench file.
    """

    semicolon_newline = ";\n"
    # add variable type signal
    data_type_signal = []
    # extract generic constant declaration if exists
    if "generic" in component:
        temp_before = component.find("(") + 1
        temp_after = component.find(");", temp_before)
        generic_const = component[temp_before:temp_after]

        # if no default value is given for the generic constant
        find = re.search(r"\d+", generic_const)
        if find is None:
            # add default value
            generic_const = generic_const + " := 8"

        # declaration const generic
        declaration_generic_const = "constant " + generic_const + semicolon_newline

        data_type_signal.append(declaration_generic_const)

    # extract input,output signals
    # find port substring start
    port_substring = component.find("port") + len("port")
    if port_substring >= 0:
        first_parenthese = component.find("(", port_substring) + 1
        last_parenthese = component.rfind(");", first_parenthese)
        signal_declaration = component[first_parenthese:last_parenthese]

        # removing in/out/buffer directional signal
        signals = remove_directional_signals(signal_declaration)
        signals = signals.split(";")

        for signal in signals:
            data_type_signal.append("signal " + signal + semicolon_newline)

        return " ".join(data_type_signal)

    return "port declaration not found in file!"


def map_signals(signals):
    """
        map signals declaration to component

        Args:
            signals(str): signals declared in the testbench file

        Returns:
            mapped_signals(str): signals mapped to the component to test
    """
    indentation ="\t\t\t\t"
    # signals to map to the component to test
    signals_to_map = "generic map ( "
    tmp_signals = signals.splitlines()
    # name of signal identifier
    signal_name=""
    # check if there's a generic constant declaration
    generic = False
    # generic map first
    for signal in tmp_signals:
        # remove  data type declaration
        signal = signal[: signal.find(":")]
        if "constant" in signal:
            generic = True
            signal_name = signal[len("constant") + 1:].strip()
            signal_name = signal_name + "=>" + signal_name + ",\n"
            signals_to_map += signal_name

    if generic:
        # remove last comma character
        signals_to_map = signals_to_map[:signals_to_map.rfind(",")]
        # end generic mapping
        signals_to_map = signals_to_map + ")\n"
    else:
        # no generic to map
        signals_to_map = ""
        # no indention
        indentation = ""
        
    # signal map port
    signals_to_map += indentation + "port map ( "
    for signal in tmp_signals:
        # remove  data type declaration
        signal = signal[: signal.find(":")]
        # remove variable type (signal|variable|constant)
        if "constant" in signal:
            continue

        if "signal" in signal:
            signal_name = signal[len("signal") + 1:].strip()

        elif "variable" in signal:
            signal_name = signal[len("variable") + 1:].strip()
            
        # multiples lines variables declaration
        for name in signal_name.split(","):
            if len(name) > 0 :
                # append to signal to map
                signals_to_map += name + "=>" + name + ",\n\t\t\t\t"

    # remove last comma character
    signals_to_map = signals_to_map[:signals_to_map.rfind(",")]
    # end signals mapping
    signals_to_map = signals_to_map + ");\n"

    return signals_to_map


def write_testbench(entity_lines):
    """
        Write the testbench file of the component interface.

        Args:
            component (str): The component interface declaration.

        Returns:
            int: 0 if successful, -1 otherwise.
    """

    # list of the different info of the component
    info_interface = (component_interface(entity_lines)).split("\n")
    # entity name
    before_entity = (info_interface[0].find("component") + len("component")) + 1
    after_entity = info_interface[0].find("is")
    # extract the entity name of the VHDL file
    entity_name = info_interface[0][before_entity:after_entity].strip()
    # file name
    testbench_file_name = entity_name + "_tb.vhdl".capitalize()
    # file path
    file_path = os.path.join(os.getcwd(), testbench_file_name)
    # component to test
    component_test = '\n'.join(info_interface).strip()
    # parse signals declaration in the VHDL entity
    signals = parse_signals(component_test)
    # signals to map
    mapping_signals = map_signals(signals)
    # testbench
    testbemch_template = f"""
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity {entity_name}_tb is
end entity {entity_name}_tb;

architecture Behavior of {entity_name}_tb is

    -- component to test
    {component_test}

    -- signal to map to component
    {signals}
begin
    -- map signals
    uut: {entity_name} {mapping_signals}

    stimulus: process is
    begin
     -- write your test here
    wait;
    end process;
end architecture behaviour;
    """

    # check if that file_name already exists
    override = False
    if os.path.exists(file_path):
        override = True
        answer = input(bcolors.WARNING + "file " + testbench_file_name + " already exists do you want to override it?([Yes/Y/y or No/N/n]): "+ bcolors.ENDC).lower()
    # we only need to check the value of answer when override is True
    if not (override) or answer in ("yes", "y"):
        # write the testbench file
        try:
            with open(testbench_file_name, 'w', encoding="utf-8") as writer:
                writer.write(testbemch_template)
                print(bcolors.OKGREEN + "GENERATED TESTBENCH! : " + file_path  + bcolors.ENDC)
        except Exception as e:
            print(bcolors.FAIL + f"An error occurred: {e}" + bcolors.ENDC)
            return -1
    return 0


def main():
    """
        Main start script
    """

    # help command
    help_usage = """
    Usage: python3 testbench_generator.py [VHDL FILE]...

Generate testbench template of VHDL FILE(s) to current working directory

Examples:
     python3 testbench_generator.py adder.vhdl mux.vhdl ...
"""

    if len(sys.argv) < 2:
        print(help_usage)
    else:
        # processing every arguments (except first argument(script name))
        for arg in sys.argv[1:]:
            # check if VHDL file
            if arg.endswith((".vhdl", ".vhd")):
                # processing  arguments
                entity_lines = parse_file(arg)
                # error if parse_file return a int value
                if isinstance(entity_lines, int):
                    return entity_lines
                # write the testbench file
                write_testbench(entity_lines)
            else:
                # verify with the user if VHDL file are passed in argument
                valid = False
                while not valid:
                    answer = input(bcolors.WARNING + "Are the file(s) passed as argument  VHDL file(s)? ([Yes/Y/y or No/N/n]): " +  bcolors.ENDC).lower()
                    if answer in ("yes", "y"):
                        valid = True
                        # process files arguments
                        parse_file(arg)

                    elif answer in ("no", "n"):
                        # quit
                        print("Terminated!")
                        valid = True
                    else:
                        print(bcolors.WARNING + "Please answer by (Yes/Y/y) if argument(s) are VHDL file(s) otherwise answer by (No/N/n)" + + bcolors.ENDC)
    return 0


if __name__ == '__main__':
    main()
