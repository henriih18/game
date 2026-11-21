"""recepción v128 - estudio final sin escritura.

Lee la colección NEXUS_V05_REC_PLAY y reporta:
- número total de objetos,
- objetos con props y sus valores,
- si los targets esperados (linterna, oficina, aseo) están presentes y
  con qué props.

No escribe nada. Solo lee y reporta.

Salida: estudio de estudio de blend.
"""

import bpy
from pathlib import Path

REC_PLAY = "NEXUS_V05_REC_PLAY"
TARGETS = {
    "NEXUS_V05_REC_FLASHLIGHT",
    "NEXUS_V05_OFFICE_DOOR_PIVOT",
    "NEXUS_V05_REST_DOOR_PIVOT",
}


def run():
    coll = None
    for c in bpy.data.collections:
        if c.name == REC_PLAY:
            coll = c
            break
    if coll is None:
        print("NO_COLLECTION", REC_PLAY)
        return
    print("PLAY_FOUND", REC_PLAY)
    print("PLAY_COUNT", len(coll.objects))
    named = [(o.name, dict(o)) for o in coll.objects if o.keys()]
    print("NAMED_WITH_PROPS_COUNT", len(named))
    for name, props in named:
        if name in TARGETS or name.startswith(
            ("NEXUS_V05_REC_LOOT", "NEXUS_V05_REC_TRAP",
             "NEXUS_V05_REC_HIDE", "NEXUS_V05_REC_DOOR_PIVOT",
             "NEXUS_V05_REC_SPILL")
        ):
            print("PROP", name, props)
    present = TARGETS & {o.name for o in coll.objects}
    missing = TARGETS - {o.name for o in coll.objects}
    print("TARGETS_PRESENT", sorted(present))
    print("TARGETS_MISSING", sorted(missing))
    print("TARGETS_OK", present == TARGETS)


def main():
    run()


main()
