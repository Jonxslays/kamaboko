from __future__ import annotations

import importlib
import pathlib
import typing as t

import quart

from config import Config
from database import Database
from .utils import *

class _BlueprintT(t.Protocol):
    def register(self, app: App) -> None:
        ...

class App(quart.Quart):
    def __init__(self) -> None:
        super().__init__(__name__)

        self.secret_key = Config.env('SECRET_KEY')

        self.pool = Database()
        self.rest = OAuth2(self)

        self.load_blueprints(*pathlib.Path('dashboard/blueprints').glob('*.py'))

        @self.before_serving
        async def on_starting() -> None:
            await self.pool.connect()

        @self.after_serving
        async def on_stopping() -> None:
            await self.pool.close()

    def load_blueprints(self, *blueprints: pathlib.Path) -> None:
        for blueprint in blueprints:
            blueprint = f'{blueprint.parent}.{blueprint.stem}'.replace('\\', '.')
            module = importlib.import_module(blueprint)
            ext = t.cast(_BlueprintT, module)
            ext.register(self)