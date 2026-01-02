import unittest
import os
import sys
import re

# Use standard imports assuming tests are run from the project root
from src.sgf_to_anki import clean_sgf_comment, process_sgf_content, natural_sort_key


class TestSgfToAnki(unittest.TestCase):

    def test_clean_sgf_comment_basic(self):
        self.assertEqual(clean_sgf_comment("Black to kill"), "Black to kill")

    def test_clean_sgf_comment_newlines(self):
        self.assertEqual(clean_sgf_comment("Black to kill\n\nWhite is dead."), "Black to kill. White is dead.")

    def test_clean_sgf_comment_html_tags(self):
        self.assertEqual(clean_sgf_comment("CORRECT\n\n<b>CORRECT!</b>\n\nWhite is dead"), "CORRECT. White is dead")

    def test_clean_sgf_comment_html_tags_and_link(self):
        self.assertEqual(clean_sgf_comment("WRONG\n\n<b>WRONG!</b>\n\nBlack is dead by <a href=\"https://senseis.xmp.net/?BentFourInTheCorner\">Bent four in the corner</a>"), "WRONG. Black is dead by Bent four in the corner")

    def test_clean_sgf_comment_html_br(self):
        self.assertEqual(clean_sgf_comment("This is a comment.<br><br>With line breaks."), "This is a comment.. With line breaks.")

    def test_clean_sgf_comment_only_html_tags(self):
        self.assertEqual(clean_sgf_comment("<b></b>"), "")

    def test_clean_sgf_comment_html_and_text(self):
        self.assertEqual(clean_sgf_comment("A <b>bold</b> statement."), "A bold statement.")

    def test_remove_duplicate_correct_wrong_case_insensitive(self):
        self.assertEqual(clean_sgf_comment("CORRECT\n\n<b>CORRECT!</b>\nTest."), "CORRECT. Test.")
        self.assertEqual(clean_sgf_comment("WRONG\n\n<b>WRONG!</b>\nTest."), "WRONG. Test.")
        self.assertEqual(clean_sgf_comment("CORRECT\nCORRECT. Test."), "CORRECT. Test.")
        self.assertEqual(clean_sgf_comment("CORRECT\nThis is good."), "CORRECT. This is good.")
        self.assertEqual(clean_sgf_comment("<b>WRONG!</b>. This is bad."), "WRONG!. This is bad.")
        self.assertEqual(clean_sgf_comment("WRONG. This is bad."), "WRONG. This is bad.")

    # Tests for process_sgf_content (full SGF string processing)
    def test_process_sgf_content_basic(self):
        sgf_content = "(;FF[4]CA[UTF-8]AP[puzzle2sgf:0.1]GM[1]GN[1 / 900]SZ[19]AB[bc][be][cc][dc][eb][fb]AW[ab][bb][cb][da][db]PL[B]C[Black to kill](;B[ba]TR[aa]TR[ca]C[CORRECT\n\n<b>CORRECT!</b>\n\nWhite is dead\n\nWhite can not make two eyes.])(;B[ca]C[<b>WRONG!</b>];W[ba]TR[aa]TR[ca]C[WRONG\n\n<b>WRONG!</b>\n\nWhite is alive\n\nWhite has two real eyes.]))"
        expected = "(;FF[4]CA[UTF-8]AP[puzzle2sgf:0.1]GM[1]GN[1 / 900]SZ[19]AB[bc][be][cc][dc][eb][fb]AW[ab][bb][cb][da][db]PL[B]C[Black to kill](;B[ba]TR[aa]TR[ca]C[CORRECT. White is dead. White can not make two eyes.])(;B[ca]C[WRONG!];W[ba]TR[aa]TR[ca]C[WRONG. White is alive. White has two real eyes.]))"
        # Note: The expected string still reflects my understanding of how clean_sgf_comment works.
        # It should correctly process each C[] independently.
        self.assertEqual(process_sgf_content(sgf_content), expected)

    def test_process_sgf_content_no_comment(self):
        sgf_content = "(;FF[4]GM[1]GN[Test])"
        expected = "(;FF[4]GM[1]GN[Test])"
        self.assertEqual(process_sgf_content(sgf_content), expected)

    def test_process_sgf_content_multiple_comments(self):
        sgf_content = "(;C[First comment.\nNew line.];AB[aa]C[Second comment.\nAnother line.])"
        expected = "(;C[First comment.. New line.];AB[aa]C[Second comment.. Another line.])"
        self.assertEqual(process_sgf_content(sgf_content), expected)

    def test_natural_sort_key(self):
        files = ['10.sgf', '1.sgf', '2.sgf', '20.sgf', '100.sgf']
        expected = ['1.sgf', '2.sgf', '10.sgf', '20.sgf', '100.sgf']
        files.sort(key=natural_sort_key)
        self.assertEqual(files, expected)
        
        # Test with prefix
        files = ['file10.txt', 'file1.txt', 'file2.txt']
        expected = ['file1.txt', 'file2.txt', 'file10.txt']
        files.sort(key=natural_sort_key)
        self.assertEqual(files, expected)

if __name__ == '__main__':
    unittest.main()
