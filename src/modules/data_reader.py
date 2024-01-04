import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from collections import OrderedDict
import numpy as np
import modules.base64_thermal_decoder as decoder


class DataReader:
    """Singleton class for reading data from json file"""
    __instance = None
    def __new__(cls, *args, **kwargs):
        if DataReader.__instance is None:
            DataReader.__instance = object.__new__(cls)
        return DataReader.__instance
    
    def __init__(self, samples_path='data/samples.json'):
        self.samples_path = samples_path
        self.samples = None
    
    def read_samples(self) -> None:
        with open(self.samples_path, 'r') as f:
            samples = json.load(f)
        # Decode base64 strings
        decoded_samples = OrderedDict()
        for timestamp, encoded_string in samples.items():
            values = decoder.decode_base64(encoded_string, 0, 100.0)
            decoded_samples[timestamp] = np.array(values, dtype=np.float32).reshape(24, 32)
        # Save decoded samples
        self.samples = decoded_samples
    
    @property
    def data(self) -> OrderedDict:
        if self.samples is None:
            self.read_samples()
        return self.samples


class FirebaseReader:
    """Singleton class for reading data from Firebase"""
    __instance = None
    def __new__(cls, *args, **kwargs):
        if FirebaseReader.__instance is None:
            FirebaseReader.__instance = object.__new__(cls)
    
            # check if the app has already been initialized
            if not firebase_admin._apps:
                # initialize the Firebase app
                cred = credentials.Certificate("serviceAccountKey.json")
                firebase_admin.initialize_app(cred, {'databaseURL': 'https://esp32test-115a2-default-rtdb.firebaseio.com'})

        return FirebaseReader.__instance
    
    def __init__(self, db_ref='thermal_cam'):
        self.root_ref = db.reference(db_ref)
        self.samples = {}
        self.date = None
        self.dates_avaialbe = None
    
    def read_samples_by_date(self, date: str, debug_mode: bool) -> OrderedDict:
        """
        Get all the data for a given date
        :param date: the date to get the data for
        :return: a pandas dataframe with the data
        """
        # Get the data for the given date
        if debug_mode: # Only get 100 samples for debug mode
            samples = self.root_ref.child(date).order_by_key().limit_to_first(100).get()
        else:
            samples = self.root_ref.child(date).order_by_key().get()
    
        # Decode base64 strings
        decoded_samples = OrderedDict()
        for timestamp, encoded_string in samples.items():
            values = decoder.decode_base64(encoded_string, 0, 100.0)
            decoded_samples[timestamp] = np.array(values, dtype=np.float32).reshape(24, 32)

        # Save decoded samples
        self.samples[date] = decoded_samples

    def set_date(self, date: str, debug_mode: bool) -> None:
        self.date = date
        if date not in self.samples.keys():
            self.read_samples_by_date(date, debug_mode)


    @property
    def data(self) -> OrderedDict:
        return self.samples[self.date]
    
    @property
    def dates(self) -> list:
        if self.dates_avaialbe is None:
            self.dates_avaialbe = sorted(list(self.root_ref.get(shallow=True).keys()))
        return self.dates_avaialbe