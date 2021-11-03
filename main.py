# standart libraries
import json
import os

# Imports
from src.LuisBookFlight import LuisBookFlight
from src.DataPreparation import data_preparation as dp

# Load AuthKeys
with open(".auth") as f:
    auth_info = json.load(f)

# Store Keys
LUIS_SUBSCRIPTION_KEY = auth_info.get('luis_subscription_key')
LUIS_ENDPOINT = auth_info.get('luis_ep')
INSTRUMENTATION_KEY = auth_info.get('InstrumentationKey')
MS_ID = auth_info.get('MicrosoftAppId')
MS_PASSWORD = auth_info.get('MicrosoftAppPassword')

def create_env_file(LUIS_SUBSCRIPTION_KEY, LUIS_ENDPOINT, INSTRUMENTATION_KEY, APP_ID, MS_ID, MS_PASSWORD):
    EP = LUIS_ENDPOINT.split('/')[2]
    ENV_KEYS = f'MicrosoftAppId="{MS_ID}"\nMicrosoftAppPassword="{MS_PASSWORD}"\nLuisAppId="{APP_ID}"\nLuisAPIKey="{LUIS_SUBSCRIPTION_KEY}"\nLuisAPIHostName="{EP}"\nInstrumentationKey="{INSTRUMENTATION_KEY}"'

    with open('.env', 'w') as output:
        output.write(ENV_KEYS)



if __name__ == '__main__':
    BookFlight = LuisBookFlight(LUIS_SUBSCRIPTION_KEY, LUIS_ENDPOINT)
    train, test = dp('./dataset/frames.json')
    
    #Create Output directory
    if os.path.exists('./output') == False: 
        os.mkdir('output')

    with open("./output/test.json", 'w') as output:
        json.dump(test, output)

    BookFlight.train_app(train)
    BookFlight.publish_app()

    create_env_file(LUIS_SUBSCRIPTION_KEY, LUIS_ENDPOINT, INSTRUMENTATION_KEY, BookFlight.app_id, MS_ID, MS_PASSWORD)