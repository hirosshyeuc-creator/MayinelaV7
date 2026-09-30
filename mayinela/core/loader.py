import importlib
import pkgutil
from mayinela import plugins

async def load_plugins():
    for info in pkgutil.iter_modules(plugins.__path__):
        importlib.import_module(f"mayinela.plugins.{info.name}")
