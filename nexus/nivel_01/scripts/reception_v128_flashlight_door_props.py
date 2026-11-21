"""recepción v128 - estudio sobre props sin escritura.

Lectura únicamente: lee la colección NEXUS_V05_REC_PLAY y reporta los
objetos que tengan props: linterna, puertas de oficina y aseo, y demás.
No escribe nada.

Salida: fichero de estudio de blend.
"""

import bpy
from pathlib import Path


REC_PLAY = "NEXUS_V05_REC_PLAY"


def read_props():
    coll = None
    for c in bpy.data.collections:
        if c.name == REC_PLAY:
            coll = c
            break
    if coll is None:
        print("NO_COLLECTION")
        return
    print("COLLECTION_FOUND", REC_PLAY)
    print("PLAY_COUNT", len(coll.objects))
    named = [(o.name, dict(o)) for o in coll.objects if o.keys()]
    print("NAMED_PROPS_COUNT", len(named))
    for name, props in named:
        print("PROP", name, props)


def main():
    read_props()


main()
