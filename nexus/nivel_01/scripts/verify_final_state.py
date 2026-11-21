"""verificacion final sin escritura.

Abre el blend guardado en disco y reporta qué hay en la colección
de juego, qué objetos tienen props, y si los targets esperados estan
presentes.

Solo lectura. No escribe nada.

Salida: informe de verificación.
"""

import bpy
from pathlib import Path


PLAY = "NEXUS_V05_REC_PLAY"
TARGETS = {
    "NEXUS_V05_REC_FLASHLIGHT",
    "NEXUS_V05_OFFICE_DOOR_PIVOT",
    "NEXUS_V05_REST_DOOR_PIVOT",
}


def verify():
    coll = None
    for c in bpy.data.collections:
        if c.name == PLAY:
            coll = c
            break
    if coll is None:
        print("NO_PLAY_COLLECTION")
        return
    print("PLAY_FOUND", PLAY)
    print("PLAY_COUNT", len(coll.objects))
    named = [(o.name, dict(o)) for o in coll.objects if o.keys()]
    print("NAMED_WITH_PROPS_COUNT", len(named))
    for name, props in named:
        print("PROP", name, props)
    present = TARGETS & {o.name for o in coll.objects}
    missing = TARGETS - {o.name for o in coll.objects}
    print("TARGETS_PRESENT", sorted(present))
    print("TARGETS_MISSING", sorted(missing))
    print("TARGETS_OK", present == TARGETS)


def main():
    verify()


main()
