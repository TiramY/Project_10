import json
import os
import unittest
from src.LuisBookFlight import LuisBookFlight

class LuisUnitTest(unittest.TestCase):
    def test_authFileisHere(self):
        # Load AuthKeys
        self.assertTrue(os.path.isfile('.auth'))

    def test_LuisBookFlightClass(self):
        # Load AuthKeys
        with open(".auth") as f:
            auth_info = json.load(f)

        self.assertIsNotNone(auth_info.get('luis_subscription_key'))
        self.assertIsNotNone(auth_info.get('luis_ep'))
        self.assertIsNotNone(auth_info.get('InstrumentationKey'))
        self.assertIsNotNone(auth_info.get('MicrosoftAppId'))
        self.assertIsNotNone(auth_info.get('MicrosoftAppPassword'))

        self.auth_info = auth_info

        LUIS_SUBSCRIPTION_KEY = auth_info.get('luis_subscription_key')
        LUIS_ENDPOINT = auth_info.get('luis_ep')

        # Load AuthKeys
        BookFlight = LuisBookFlight(LUIS_SUBSCRIPTION_KEY, LUIS_ENDPOINT, 'Test_LuisBookflight')
        self.assertIsNotNone(BookFlight.app_id)

if __name__ == '__main__':
    unittest.main()