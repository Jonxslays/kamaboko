import typing as t
from os import environ
from dotenv import load_dotenv

load_dotenv()

class Config():
    @staticmethod
    def env(value: str, conversion: type = str) -> t.Any:
        return conversion(environ[value])
