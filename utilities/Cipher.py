
"""Cipher.py: 

    TODO: This code is very old. It needs to be rewritten."""

__author__ = "Jacob Taylor Casasdy"
__email__ = "jacobtaylorcassady@outlook.com"

from unittest import main, TestCase
from abc import ABC, abstractmethod

class Cipher(ABC):
    """[summary]"""

    @abstractmethod
    def encode(self, message: str) -> str:
        """[summary]

        Args:
            message (str): [description]

        Returns:
            str: [description]"""
        pass

    @abstractmethod
    def decode(self, message: str) -> str:
        """[summary]

        Args:
            message (str): [description]

        Returns:
            str: [description]"""
        pass


class VigenereCipher(Cipher):
    """[summary]"""

    def __init__(self, key: str, alphabet: str):
        """Constructor.

        Args:
            key (str): [description]
            alphabet (str): [description]"""
        self.key = key
        self.alphabet = alphabet

    def __str__(self) -> str:
        """[summary]

        Returns:
            str: [description]"""
        return self.alphabet

    def encode(self, message: str) -> str:
        """[summary]

        Args:
            message (str): [description]

        Returns:
            str: [description]"""
        result = ""
        fullKey = self.stretchKey(message)

        for character_i in range(0, len(message)):
            if(self.alphabet.find(message[character_i]) != -1):
                result += self.shiftChar(message[character_i], fullKey[character_i])
            else:
                result += message[character_i]
        return result

    def decode(self, message: str) -> str:
        """[summary]

        Args:
            message (str): [description]

        Returns:
            str: [description]"""
        result = ""
        fullKey = self.stretchKey(message)

        for character_i in range(0, len(message)):
            if(self.alphabet.find(message[character_i]) != -1):
                result += self.deshiftChar(message[character_i], fullKey[character_i])
            else:
                result += message[character_i]
        return result
        
    def stretchKey(self, message: str) -> str:
        """[summary]

        Args:
            message (str): [description]

        Returns:
            str: [description]"""
        result = ""

        while(len(result) <= len(message)):
            result += self.key

        return result[0:len(message)]

    def shiftChar(self, char: str, shiftChar: str) -> str:
        """[summary]

        Args:
            char (str): [description]
            shiftChar (str): [description]

        Returns:
            str: [description]"""
        shift = self.alphabet.find(shiftChar)
        shiftedValue = self.alphabet.find(char)+shift

        if(shiftedValue >= len(self.alphabet)):
            shiftedValue -= len(self.alphabet)

        return self.alphabet[shiftedValue]

    def deshiftChar(self, char: str, shiftChar: str) -> str:
        """[summary]

        Args:
            char (str): [description]
            shiftChar (str): [description]

        Returns:
            str: [description]"""
        shift = self.alphabet.find(shiftChar)
        shiftedValue = self.alphabet.find(char)-shift

        if(shiftedValue < 0):
            shiftedValue += len(self.alphabet)

        return self.alphabet[shiftedValue]


class Test_VigenereCipher(TestCase):
    def test_initialization(self):
        pass


if __name__ == "__main__":
    main()
