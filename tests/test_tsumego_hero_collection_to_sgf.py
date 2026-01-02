import unittest
from unittest.mock import patch, MagicMock
import os
import re
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Use standard imports assuming tests are run from the project root
from src.tsumego_hero_collection_to_sgf import get_problem_details, clean_sgf_js, main, create_session

class TestTsumegoHeroCollectionToSgf(unittest.TestCase):
    def setUp(self):
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')

    def read_test_file(self, filename):
        with open(os.path.join(self.test_data_dir, filename), 'r', encoding='utf-8') as f:
            return f.read()

    def test_create_session_configuration(self):
        """Test that the session is configured with the correct retry strategy."""
        session = create_session()
        
        # Check headers
        self.assertIn("User-Agent", session.headers)
        self.assertIn("Referer", session.headers)
        
        # Check HTTPAdapter configuration
        self.assertIn("https://", session.adapters)
        self.assertIn("http://", session.adapters)
        
        adapter = session.adapters["https://"]
        self.assertIsInstance(adapter, HTTPAdapter)
        
        # Verify Retry object configuration
        retry = adapter.max_retries
        self.assertIsInstance(retry, Retry)
        self.assertEqual(retry.total, 5)
        self.assertEqual(retry.backoff_factor, 1)
        self.assertIn(429, retry.status_forcelist)
        self.assertIn(500, retry.status_forcelist)
        self.assertIn(502, retry.status_forcelist)
        self.assertIn(503, retry.status_forcelist)
        self.assertIn(504, retry.status_forcelist)
        self.assertIn("GET", retry.allowed_methods)

    def test_get_problem_details_1447(self):
        # Setup mock for 1447
        html_content = self.read_test_file('1447')
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html_content
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        url = "https://tsumego.com/1447"
        title, sgf_content = get_problem_details(mock_session, url)

        expected_title = "Life & Death - Elementary  #1 1/900"
        expected_sgf_start = "(;GM[1]FF[4]CA[UTF-8]AP[CGoban:3]ST[2]\nRU[Japanese]"

        self.assertEqual(title, expected_title)
        self.assertIsNotNone(sgf_content)
        self.assertTrue(sgf_content.strip().startswith(expected_sgf_start))
        self.assertIn("PW[white]PB[black]", sgf_content)

    def test_get_problem_details_13780(self):
        # Setup mock for 13780
        html_content = self.read_test_file('13780')
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = html_content
        
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response

        url = "https://tsumego.com/13780"
        title, sgf_content = get_problem_details(mock_session, url)

        expected_title = "Life & Death - Elementary  #1 177/900"
        
        # Verify SGF extraction for 13780
        self.assertEqual(title, expected_title)
        self.assertIsNotNone(sgf_content)
        self.assertIn("AW[aa][ea][cb][db][eb][ac][bc][cc]", sgf_content)
        self.assertIn("AB[ca][fa][fb][dc][ec][fc][ad][bd][cd]", sgf_content)

    def test_collection_name_extraction(self):
        # Test extraction of collection name from file '1'
        html_content = self.read_test_file('1')
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Logic from main() in tsumego_hero_collection_to_sgf.py
        collection_name_tag = soup.select_one('.homeLeft .title4')
        collection_name = collection_name_tag.text.strip() if collection_name_tag else "Tsumego_Collection"
        
        self.assertEqual(collection_name, "Life & Death - Elementary #1")

    def test_clean_sgf_js_logic(self):
        raw_js = '"(;GM[1]FF[4]CA[UTF-8]AP[CGoban:3]ST[2]"+"\n"+"RU[Japanese]SZ[19]KM[0.00]"+"\n"+"PW[white]PB[black]AW[da][ab][bb][cb][db]AB[eb][fb][bc][cc][dc][be]"+"\n"+";B[ba]C[+])"+"\n"+""'
        cleaned = clean_sgf_js(raw_js)
        expected_sgf = (
            "(;GM[1]FF[4]CA[UTF-8]AP[CGoban:3]ST[2]\n"
            "RU[Japanese]SZ[19]KM[0.00]\n"
            "PW[white]PB[black]AW[da][ab][bb][cb][db]AB[eb][fb][bc][cc][dc][be]\n"
            ";B[ba]C[+])"
        )
        self.assertEqual(cleaned.strip(), expected_sgf.strip())

if __name__ == "__main__":
    unittest.main()
