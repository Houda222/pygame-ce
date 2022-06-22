"""
buildconfig/stubs/gen_stubs.py
A script to auto-generate constants.pyi and __init__.pyi typestubs
"""

import pathlib
from typing import Any

import pygame.constants

HEADER_DOCSTRING = f"{__doc__}\nIMPORTANT NOTE: Do not edit this file by hand!\n"


# pygame submodules that are auto-imported must be kept in this list
# keep in mind that not all pygame modules are auto-imported, hence not all
# pygame submodules make it to this list
PG_AUTOIMPORT_SUBMODS = [
    "display",
    "draw",
    "event",
    "font",
    "image",
    "key",
    "mixer",
    "mouse",
    "time",
    "cursors",
    "joystick",
    "math",
    "mask",
    "pixelcopy",
    "sndarray",
    "sprite",
    "surfarray",
    "transform",
    "fastevent",
    "scrap",
    "threads",
    "version",
    "base",
    "bufferproxy",
    "color",
    "colordict",
    "mixer_music",
    "pixelarray",
    "rect",
    "rwobject",
    "surface",
    "surflock",
    "sysfont",
    "context"
]

# pygame classes that are autoimported into main namespace are kept in this dict
PG_AUTOIMPORT_CLASSES = {
    "rect": ["Rect", "FRect"],
    "surface": ["Surface", "SurfaceType"],
    "color": ["Color"],
    "pixelarray": ["PixelArray"],
    "math": ["Vector2", "Vector3"],
    "cursors": ["Cursor"],
    "bufferproxy": ["BufferProxy"],
    "mask": ["Mask"],
}

# pygame modules from which __init__.py does the equivalent of
# from submod import *
# should be kept here
PG_STAR_IMPORTS = ("base", "rwobject", "version", "constants")


def get_all(mod: Any):
    """
    Get the attributes that are imported from 'mod' when 'from mod import *'
    First try to use '__all__' if it is defined, else fallback to 'dir'
    """
    if hasattr(mod, "__all__") and isinstance(mod.__all__, list):
        return sorted({str(i) for i in mod.__all__})

    return [i for i in dir(mod) if not i.startswith("_")]


# store all imports of __init__.pyi
pygame_all_imports = {"pygame": PG_AUTOIMPORT_SUBMODS}
for k, v in PG_AUTOIMPORT_CLASSES.items():
    pygame_all_imports[f".{k}"] = v

for k in PG_STAR_IMPORTS:
    pygame_all_imports[f".{k}"] = get_all(getattr(pygame, k))

# misc stubs that must be added to __init__.pyi
misc_stubs = """
from typing import Tuple, NoReturn

def Overlay(format: int, size: Tuple[int, int]) -> NoReturn: ...
"""

# write constants.pyi file
constants_file = pathlib.Path(__file__).parent / "pygame" / "constants.pyi"
with open(constants_file, "w") as f:
    # write the module docstring of this file in the generated file, so that
    # people know this file exists
    f.write(f'"""{HEADER_DOCSTRING}"""\n\n')
    f.write("from typing import List\n\n")

    for element in pygame_all_imports[".constants"]:
        constant_type = getattr(pygame.constants, element).__class__.__name__
        f.write(f"{element}: {constant_type}\n")

    f.write("\n__all__: List[str]\n")


# write __init__.pyi file
init_file = pathlib.Path(__file__).parent / "pygame" / "__init__.pyi"
with open(init_file, "w") as f:
    # write the module docstring of this file in the generated file, so that
    # people know this file exists
    f.write(f'"""{HEADER_DOCSTRING}"""\n')
    f.write(misc_stubs)

    for mod, items in pygame_all_imports.items():
        if len(items) <= 4:
            # try to write imports in a single line if it can fit the line limit
            import_items = map(lambda string: f"{string} as {string}", items)
            import_line = f"\nfrom {mod} import {', '.join(import_items)}"
            if len(import_line) <= 88:
                f.write(import_line)
                continue

        f.write(f"\nfrom {mod} import (\n")
        for item in items:
            f.write(f"    {item} as {item},\n")
        f.write(")\n")
