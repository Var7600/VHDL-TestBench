# -----------------------------------------------------------------------------
# Name:        test_testbench_generator
# Purpose:     unit test for module testbench_generator
# python_version: 3.8.10
# Author:      DOUDOU DIAWARA
#
# Created:     27/05/2024
# License:     MIT License
# -----------------------------------------------------------------------------

import unittest
from unittest.mock import mock_open, patch
from testbench_generator import parse_file, component_interface, remove_directional_signals, parse_signals, map_signals, write_testbench

class TestGlobalFunctions(unittest.TestCase):


    VHDL_CONTENT =  """
        entity adder is
            port ( A : in std_logic;
            B : in std_logic_vector(7 downto 0);
            C : in bit;
        end adder;
        """
    COMPONENT_INTERFACE = """
        component test is
        port ( A : in std_logic;
        B : in  std_logic_vector(7 downto 0);
        C : out bit);
        end component test
        """

    SIGNALS = """
signal A : std_logic;
signal B : std_logic_vector(7 downto 0);
signal C : bit;
"""


    @patch("builtins.open", side_effect=FileNotFoundError)
    def testparse_file_not_exists(self, mock_file):
        self.assertEqual(parse_file("nonexistent.vhdl"), -1)


    @patch("builtins.open", new_callable=mock_open, read_data=VHDL_CONTENT)
    def testparse_file_exists(self, mock_file):
        result = parse_file("adder.vhdl")
        self.assertIn("entity adder is", result)
        self.assertIn("end adder;", result)


    def testcomponent_interface(self):
        result = component_interface(self.VHDL_CONTENT)
        self.assertIn("component adder is", result)
        self.assertIn("end component adder", result)

    def testremove_directional_signals(self):
        result = remove_directional_signals(self.COMPONENT_INTERFACE)
        self.assertNotIn("in", result)
        self.assertNotIn("out", result)
        self.assertNotIn("buffer", result)

    def testparse_signals(self):
        result = parse_signals(self.COMPONENT_INTERFACE)
        result = result.splitlines()
        self.assertIn("signal A : std_logic;", result[0].strip())
        self.assertIn("signal  B : std_logic_vector(7 downto 0);", result[1].strip())
        self.assertIn("signal  C : bit;", result[2].strip())
        

    def testmap_signals(self):
        result = map_signals(self.SIGNALS)
        self.assertIn("A=>A", result)
        self.assertIn("B=>B", result)
        self.assertIn("C=>C", result)
        
    @patch("builtins.open", new_callable=mock_open)
    def testwrite_testbench(self,mock_file):
        result = write_testbench(self.COMPONENT_INTERFACE)
        self.assertEqual(result,0)
        mock_file().write.assert_called_once()


if __name__ == '__main__':
    unittest.main()
