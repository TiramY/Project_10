import os
import json
import datetime
import time

from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from msrest.authentication import CognitiveServicesCredentials

class LuisBookFlight():

    def __init__(self, LUIS_SUB_KEY : str, LUIS_EP : str, APP_NAME=None):
        self.LUIS_SUB_KEY = LUIS_SUB_KEY
        self.LUIS_EP = LUIS_EP

        self.init_luis_application(APP_NAME)
        self.define_mlentities()

    def init_luis_application(self, APP_NAME):
        client = LUISAuthoringClient(
            self.LUIS_EP,
            CognitiveServicesCredentials(self.LUIS_SUB_KEY),
        )

        try:
            if APP_NAME == None:
                # Create a LUIS app
                default_app_name = "Bookflight-{}".format(datetime.datetime.now())
            else:
                default_app_name = "{}-{}".format(APP_NAME, datetime.datetime.now())
            
            version_id = "1.0"
            print("Creating App {}, version {}".format(
                default_app_name, version_id))

            #Create application
            app_id = client.apps.add({
                'name': default_app_name,
                'initial_version_id': version_id,
                'description': "BookFlight Application",
                'culture': 'en-us',
            })

            print("Created app {}".format(app_id))

            self.intentName = "BookFlightIntent"
            client.model.add_intent(app_id=app_id, version_id=version_id, name=self.intentName)

            self.client = client
            self.app_id = app_id
            self.version_id = version_id

        except Exception as err:
            print("Encountered exception. {}".format(err))
            raise err

    def get_children(self, model, childName):	
        theseChildren = next(filter((lambda child: child.name == childName), model.children))

        return theseChildren.id

    def define_mlentities(self):
        # define machine-learned entity
        mlEntityDefinition = [
            {"name": "budget"},
            {"name": "str_date"},
            {"name": "end_date"},
            {"name": "or_city"},
            {"name": "dst_city"},
        ]

        self.model_id = self.client.model.add_entity(app_id=self.app_id,
                                                     version_id=self.version_id,
                                                     name="BookFlight",
                                                     children=mlEntityDefinition)
        

        # Add Prebuilt entity
        self.client.model.add_prebuilt(self.app_id, self.version_id, prebuilt_extractor_names=["number", "datetimeV2", "geographyV2"])

        # Get Models object
        modelObject = self.client.model.get_entity(self.app_id, self.version_id, self.model_id)

        # Get entity and subentities
        budget_id   = self.get_children(modelObject, "budget")
    
        str_date_id = self.get_children(modelObject, "str_date")
        end_date_id = self.get_children(modelObject, "end_date")

        or_city_id  = self.get_children(modelObject, "or_city")
        dst_city_id = self.get_children(modelObject, "dst_city")

        #add model as feature to subentity model Number
        prebuiltFeatureRequiredDefinitionNb = { "model_name": "number"}

        #add model as feature to subentity model Date
        prebuiltFeatureRequiredDefinitionDate = { "model_name": "datetimeV2"}

        #add model as feature to subentity model Geo
        prebuiltFeatureRequiredDefinitionGeo = { "model_name": "geographyV2"}


        #add entity feature
        try:
            self.client.features.add_entity_feature(self.app_id, self.version_id, budget_id, prebuiltFeatureRequiredDefinitionNb)

            self.client.features.add_entity_feature(self.app_id, self.version_id, str_date_id, prebuiltFeatureRequiredDefinitionDate)
            self.client.features.add_entity_feature(self.app_id, self.version_id, end_date_id, prebuiltFeatureRequiredDefinitionDate)

            self.client.features.add_entity_feature(self.app_id, self.version_id, or_city_id, prebuiltFeatureRequiredDefinitionGeo)
            self.client.features.add_entity_feature(self.app_id, self.version_id, dst_city_id, prebuiltFeatureRequiredDefinitionGeo)
        except Exception as err:
            print(err)


    def get_example_label(self, utterance, entity_name, value):
        return {
            'entityName': entity_name,
            'startCharIndex': utterance.find(value),
            'endCharIndex': utterance.find(value) + len(value)
        }

    def send_training_sample(self, data):
        utterances = []
        BATCH_SIZE = 50
        childs = ('budget', 'str_date', 'end_date', 'or_city', 'dst_city')

        for key, val in data.items():
            
            utterances.append({
                'text': key,
                'intentName': self.intentName,
                "entityLabels": [{
                    "startCharIndex": 0 if key.find(val['intent']) == -1 else key.find(val['intent']),
                    "endCharIndex": len(key),
                    "entityName": "BookFlight",
                    "children" : 
                        [self.get_example_label(key, x, val[x]) for x in childs if val[x] != None]
            }]})
            
                    
            if (len(utterances) == BATCH_SIZE):
                #Try to send batch to LUIS
                self.client.examples.batch( app_id=self.app_id,
                                            version_id=self.version_id,
                                            example_label_object_array=utterances)

                utterances = []
        
    def train_app(self, train):
        self.send_training_sample(train)

        async_training = self.client.train.train_version(self.app_id, self.version_id)
        is_trained = async_training.status == "UpToDate"

        trained_status = ["UpToDate", "Success"]
        print ("[Application] : Start Training...")
        while not is_trained:
            time.sleep(1)
            status = self.client.train.get_status(self.app_id, self.version_id)
            is_trained = all(m.details.status in trained_status for m in status)
        print ("[Application] : Application trained.")


    def publish_app(self):
        self.client.apps.update_settings(app_id=self.app_id, is_public=True)
        
        responseEndpointInfo = self.client.apps.publish(self.app_id,
                                                        self.version_id,
                                                        is_staging=False)

        self.endpoint = responseEndpointInfo