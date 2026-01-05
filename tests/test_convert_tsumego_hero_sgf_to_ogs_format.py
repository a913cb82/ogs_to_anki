import unittest
import os
from src.convert_tsumego_hero_sgf_to_ogs_format import parse_sgf_to_tree, serialize_tree_to_sgf, process_node

class TestConvertSGF(unittest.TestCase):
    def test_basic_conversion(self):
        """Test basic conversion of + to CORRECT and unmarked leaves to WRONG."""
        sgf_content = "(;GM[1]FF[4]CA[UTF-8]AP[CGoban:3]ST[2]\nRU[Japanese]SZ[19]KM[0.00]\nPW[white]PB[black]AW[ca][ea][fb][ac][bc][cc][dc][ec][fc]AB[ab][bb][cb][db][eb]\n(;B[ba]\n;W[fa]\n;B[da]C[+])\n(;B[da]\n;W[ba]))"
        
        root = parse_sgf_to_tree(sgf_content)
        for child in root.children:
            process_node(child)
        new_sgf = serialize_tree_to_sgf(root)
        
        # Verify structure and content
        self.assertIn(";B[da]C[CORRECT]", new_sgf)
        self.assertIn(";W[ba]C[WRONG]", new_sgf)
        self.assertNotIn("C[+]", new_sgf)

    def test_complex_nested_variations(self):
        """Test conversion with nested variations."""
        sgf_content = "(;GM[1](;B[aa];W[ab](;B[ac]C[+])(;B[ad]))(;B[ae];W[af]C[+]))"
        
        root = parse_sgf_to_tree(sgf_content)
        for child in root.children:
            process_node(child)
        new_sgf = serialize_tree_to_sgf(root)
        
        self.assertIn(";B[ac]C[CORRECT]", new_sgf)
        self.assertIn(";B[ad]C[WRONG]", new_sgf)
        self.assertIn(";W[af]C[CORRECT]", new_sgf)

    def test_already_labeled(self):
        """Test that existing CORRECT/WRONG labels are preserved and not duplicated."""
        sgf_content = "(;GM[1](;B[aa]C[CORRECT])(;B[ab]C[WRONG]))"
        
        root = parse_sgf_to_tree(sgf_content)
        for child in root.children:
            process_node(child)
        new_sgf = serialize_tree_to_sgf(root)
        
        # Should remain unchanged or at least not have double labels
        self.assertIn(";B[aa]C[CORRECT]", new_sgf)
        self.assertIn(";B[ab]C[WRONG]", new_sgf)
        # Ensure we didn't add another WRONG to the WRONG node
        self.assertNotIn("C[WRONG][WRONG]", new_sgf) 
        # Ensure we didn't add WRONG to the CORRECT node
        self.assertNotIn("C[CORRECT][WRONG]", new_sgf)

    def test_no_variations(self):
        """Test a linear SGF (single branch)."""
        # Linear sequence marked correct at end
        sgf_correct = "(;GM[1];B[aa];W[ab];B[ac]C[+])"
        root = parse_sgf_to_tree(sgf_correct)
        for child in root.children:
            process_node(child)
        self.assertIn(";B[ac]C[CORRECT]", serialize_tree_to_sgf(root))

        # Linear sequence unmarked at end (should be WRONG)
        sgf_wrong = "(;GM[1];B[aa];W[ab];B[ac])"
        root = parse_sgf_to_tree(sgf_wrong)
        for child in root.children:
            process_node(child)
        self.assertIn(";B[ac]C[WRONG]", serialize_tree_to_sgf(root))

    def test_plus_with_comment(self):
        """Test that + at the start of a comment is replaced by CORRECT, preserving the rest."""
        sgf_content = "(;GM[1];B[aa]C[+ and some other text])"
        root = parse_sgf_to_tree(sgf_content)
        for child in root.children:
            process_node(child)
        new_sgf = serialize_tree_to_sgf(root)
        self.assertIn("C[CORRECT and some other text]", new_sgf)

    def test_wrong_with_comment(self):
        """Test that WRONG is prepended to existing comments on wrong leaves."""
        sgf_content = "(;GM[1];B[aa]C[this is wrong because...])"
        root = parse_sgf_to_tree(sgf_content)
        for child in root.children:
            process_node(child)
        new_sgf = serialize_tree_to_sgf(root)
        self.assertIn("C[WRONG this is wrong because...]", new_sgf)

    def test_wrong_without_comment(self):
        """Test that WRONG is added to wrong leaves without comments."""
        sgf_content = "(;GM[1];B[aa])"
        root = parse_sgf_to_tree(sgf_content)
        for child in root.children:
            process_node(child)
        new_sgf = serialize_tree_to_sgf(root)
        self.assertIn("C[WRONG]", new_sgf)

if __name__ == "__main__":
    unittest.main()
