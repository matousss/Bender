import os
import importlib

__all__ = []

for file in os.listdir("./modules/"):
    if not file.startswith('__'):
        if file.endswith(".py"):
            __all__.append(str(file).replace('.py', ''))
            continue

        if not os.path.isdir(os.path.join(".", str(file))):
            __all__.append(file)
            # package = importlib.import_module(f'{__name__}.{file}')
            # a = package.__name__.replace(f'{__name__}.', '')
            # for module in package.__all__:
            #     __all__.append(f"{a}.{module}")

__cogs__ = []
