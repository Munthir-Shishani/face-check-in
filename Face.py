import asyncio
import io
import glob
import os
import sys
import time
import uuid
import requests
from datetime import datetime
import pytz
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person, SnapshotObjectType, OperationStatusType
from urllib3.exceptions import NewConnectionError
from azure.cognitiveservices.vision.face.models._models_py3 import APIErrorException

KEY = os.environ['FACE_SUBSCRIPTION_KEY']
ENDPOINT = os.environ['FACE_ENDPOINT']
PERSON_GROUP_ID = 'employees'

face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

def add_new(image, name=None, human_id=None):
    try:
        print('Person group:', PERSON_GROUP_ID)
        if human_id is None:
            human = face_client.person_group_person.create(PERSON_GROUP_ID, name)
            human_id = human.person_id

        if name is not None and human_id is not None:
            face_client.person_group_person.update(PERSON_GROUP_ID, human_id, name)

        face_client.person_group_person.add_face_from_stream(PERSON_GROUP_ID, human_id, image, detection_model="detection_02")
        face_client.person_group.train(PERSON_GROUP_ID)

        while (True):
            training_status = face_client.person_group.get_training_status(PERSON_GROUP_ID)
            print("Training status: {}.".format(training_status.status))
            print()
            if (training_status.status is TrainingStatusType.succeeded):
                break
            elif (training_status.status is TrainingStatusType.failed):
                sys.exit('Training the person group has failed.')
            time.sleep(5)
        return training_status.status
    except NewConnectionError as error:
        print(error)
        return error
    except APIErrorException as error:
        print(error)
        return error
    except IndexError as error:
        print(error)
        return error


def default_dict(counter, name='Unknown', confidence=0.0, person_id='', face_id=''):
    now = datetime.now(pytz.timezone('Asia/Amman'))
    _buffer = {}
    result = {}
    _buffer['Name'] = name
    _buffer['Date'] = now.strftime("%d/%m/%Y")
    _buffer['Time'] = now.strftime("%H:%M:%S")
    _buffer['Confidence'] = confidence
    _buffer['Person ID'] = person_id
    _buffer['Face ID'] = face_id

    result[counter] = _buffer
    return result


def who_is_it(image):
    counter = 0
    face_ids = []
    result = {}
    try:
        faces = face_client.face.detect_with_stream(image, recognition_model="recognition_02", detection_model="detection_02")
        if not faces:
            return 'No face'
        else:
            for face in faces:
                face_ids.append(face.face_id)

            results = face_client.face.identify(face_ids, PERSON_GROUP_ID, max_num_of_candidates_returned=1, confidence_threshold=0.6)
            if not results:
                result = default_dict(counter)
                return result
            else:
                for candidate in results:
                    person = face_client.person_group_person.get(PERSON_GROUP_ID, candidate.candidates[0].person_id)
                    result.update(default_dict(counter, person.name, candidate.candidates[0].confidence, person.person_id, face_ids[counter]))
                    counter += 1
                return result

    except NewConnectionError as error:
        print(error)
        return error
    except APIErrorException as error:
        print(error)
        return error
    except IndexError as error:
        print(error)
        return error
