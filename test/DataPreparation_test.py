import pandas as pd
import unittest
import os

from src.DataPreparation import data_preparation

class unitTest(unittest.TestCase):
    def test_DataPreparation(self):
        # Load AuthKeys
        train, test = data_preparation('./dataset/frames.json')
    
        # Check if it's the right type.
        self.assertTrue(isinstance(train, dict), True)
        self.assertTrue(isinstance(test, list), True)


if __name__ == '__main__':
    unittest.main()