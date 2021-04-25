
from abc import ABC, abstractclassmethod
from pandas import DataFrame

class Account(ABC):
    @abstractclassmethod
    def __init__(self, deposit_history: DataFrame, transaction_history: DataFrame, api_key: str, api_secret: str):
        pass

    class Interface(ABC):
        @abstractclassmethod
        def __init__(self, api_key: str, api_secret: str):
            pass
