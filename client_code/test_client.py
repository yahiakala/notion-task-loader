"""Test client code."""
import unittest
import anvil.server


class TestClass(unittest.TestCase):
    """Test basic chatbot functionality"""
    def setUp(self):
        # Code to run before each test method
        print("Setting up before the test")

    def tearDown(self):
        # Code to run after each test method
        print("Cleaning up after the test")

    def test_this(self):
        print('Running test_this')
        pass