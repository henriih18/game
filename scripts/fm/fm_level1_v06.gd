extends Node3D

## FRECUENCIA MUERTA — Nivel 1 V06 (primer pase de gameplay local).
##
## Monta en el mismo origen los quince sectores exportados del V06:
##   Z10, Recepción, Seguridad, Corredor principal, pasillo de acceso a
##   Seguridad, el pasillo de servicio corredor–Vestuarios y las nueve salas
##   blockout (Control, Vestuarios, Almacén, Mantenimiento, Oficinas, Aseo y
##   los tres núcleos de escaleras).
## La alineación usa directamente las coordenadas de Blender:
##   Godot X = Blender X · Godot Y = Blender Z · Godot Z = -Blender Y.
##
## Alcance de esta escena:
##   - Reutiliza las escenas de arte aprobadas de Z10 (R8) y Recepción (R9).
##   - Carga Seguridad, Corredor, el pasillo de acceso y el tramo que faltaba
##     del ChangingConnector (suelo, muro central y cierre oeste/techo) desde
##     sus GLB con luces provisionales.
##   - Instancia las nueve salas blockout con una luz de emergencia tenue
##     propia por sala (sin luces generales).
##   - Construye colisiones estáticas por sector con FMGLBCollision.
##   - Instancia un FMPlayer, el Vigilante principal de Z10, un segundo
##     Vigilante aislado dentro de Seguridad y el HUD compartido.
##   - Primer pase de gameplay: núcleo de misión, puesto de análisis
##     desmontable, componentes/documentos, baterías, dos escondites y la
##     extracción de Recepción con los sistemas compartidos del slice.
##   - Compuertas runtime en los vanos reales de Z10, Recepción y el pasillo
##     de acceso, y marcador visual de extracción en Recepción.
##   - Enlaces NavigationLink3D en las puertas blockout de 2,44 m para que el
##     Vigilante no dependa de un perfil de agente más bajo.
##   - Mesetas inferiores de escaleras seguras: el respawn no se dispara
##     dentro de los tres núcleos verticales mientras el jugador permanezca
##     sobre su meseta (no se implementa el Nivel 2).
##
## Sin armas, sin combate y sin multijugador. No modifica ninguna escena del
## vertical slice.

const PLAYER_SCENE := preload("res://scenes/fm/fm_player.tscn")
const WATCHER_SCENE := preload("res://scenes/fm/fm_watcher.tscn")
const CARRY_ITEM_SCENE := preload("res://scenes/fm/carry_item.tscn")
const DISMANTLE_SCRIPT := preload("res://scripts/fm/fm_dismantlable.gd")
const BATTERY_SCRIPT := preload("res://scripts/fm/fm_battery.gd")
const RADIO_SUPPLY_SCRIPT := preload("res://scripts/fm/fm_radio_supply.gd")
const HIDING_SPOT_SCENE := preload("res://scenes/fm/hiding_spot.tscn")
const EXTRACTION_SCRIPT := preload("res://scripts/fm/fm_reception_extraction.gd")
const HUD_SCRIPT := preload("res://scripts/fm/fm_hud.gd")
const COLLISION_HELPER := preload("res://scripts/fm/fm_glb_collision.gd")
const GATE_SCRIPT := preload("res://scripts/fm/fm_level1_gate.gd")
const STATIC_MERGE := preload("res://scripts/fm/fm_static_merge.gd")
const SHELL_MATERIALS := preload("res://scripts/fm/fm_shell_materials.gd")
const SECURITY_MATERIALS := preload("res://scripts/fm/fm_security_materials.gd")
const OCCLUDERS := preload("res://scripts/fm/fm_occluders.gd")
const HORROR_AUDIO_SCRIPT := preload("res://scripts/fm/fm_horror_audio.gd")

## Interruptor de la primera pasada de optimización. En false el nivel vuelve
## al dibujo original sin tocar el arte ni el gameplay; sirve para comparar y
## para revertir rápido si una medición futura empeora.
const ENABLE_STATIC_MERGE := true
## Celda espacial y diagonal máxima para la fusión. Una celda más chica
## conserva mejor el culling (menos triángulos dibujados) a costa de más
## draw calls; 16 m / 30 m es el equilibrio medido en este primer pase.
const STATIC_MERGE_CELL_SIZE := 16.0
const STATIC_MERGE_MAX_DIAGONAL := 30.0
## Las superficies transparentes (polvo, calcomanías, cristales) se pueden
## fusionar; en las capturas A/B no se detectaron cambios y se ganaron ~95
## draw calls en la vista de acceso. El interruptor permite dejarlas intactas
## si una vista futura muestra un problema de orden.
const STATIC_MERGE_SKIP_TRANSPARENT := false
## Pase de materiales del shell de pasillos, conectores y escaleras. Las
## mallas del shell no tienen UVs: se usa un set triplanar compartido.
const ENABLE_SHELL_MATERIALS := true
## Oclusión estática del shell. Se construye antes de la fusión, con los
## triángulos reales de muros/suelos/techos para respetar vanos y puertas.
const ENABLE_OCCLUDERS := true
## Consolidación de materiales de Seguridad. El GLB usa 123 materiales, con
## familias casi idénticas; agruparlas reduce draws por celda sin tocar el
## arte. Desactivable para comparar o revertir.
const ENABLE_SECURITY_MATERIALS := true

## Loot, recursos y escondites. Las posiciones de Z10 y Recepción provienen
## del vertical slice validado sobre las mismas escenas de arte R8/R9.
const CORE_POSITION := Vector3(57.4, 0.36, -21.4)
const DISMANTLE_POSITION := Vector3(51.2, 0.0, -17.2)
const Z10_HIDE_POSITION := Vector3(42.5, 0.05, -9.4)
const RECEPTION_HIDE_POSITION := Vector3(-106.0, 0.05, 38.8)
## Taquillas de la pared sur de Seguridad. El escondite es solo un área de
## interacción: no añade geometría ni modifica el banco de taquillas.
const SECURITY_HIDE_POSITION := Vector3(-78.4, 0.05, -11.85)
const BATTERY_Z10_POSITION := Vector3(53.4, 0.16, -25.4)
const BATTERY_RECEPTION_POSITION := Vector3(-104.0, 0.16, 20.2)
## Suministros de radio: cargadores fijos y pilas recogibles. Son recursos
## funcionales, no objetos narrativos; no añaden colisión ni alteran el navmesh.
const RADIO_STATION_Z10 := Vector3(44.0, 0.0, -25.4)
const RADIO_STATION_CONTROL := Vector3(-99.0, 0.0, -45.0)
const RADIO_STATION_WAREHOUSE := Vector3(90.0, 0.0, -26.0)
const RADIO_STATION_MAINTENANCE := Vector3(84.0, 0.0, 28.0)
const RADIO_STATION_OFFICES := Vector3(-10.5, 0.0, -40.0)
const RADIO_STATION_STAIRS := Vector3(5.5, 0.0, 40.0)
const RADIO_STATION_NWSTAIR := Vector3(-72.0, -4.5, -67.0)
## Extra: documento y componente en Recepción, documento sobre la mesa de
## briefing de Seguridad. Todos fuera de las rutas directas de paso.
const LOOT_RECEPTION_DOC_POSITION := Vector3(-90.0, 0.12, 18.0)
const LOOT_RECEPTION_COMPONENT_POSITION := Vector3(-93.0, 0.14, 24.0)
const LOOT_SECURITY_DOC_POSITION := Vector3(-96.8, 0.91, -20.4)
const EXTRACTION_POSITION := Vector3(-94.0, 1.3, 36.0)
const EXTRACTION_CENTER := Vector3(-94.0, 0.3, 37.6)
const EXTRACTION_ZONE_SIZE := Vector3(9.0, 2.6, 8.0)
const EXTRACTION_MARKER_POSITION := Vector3(-94.0, 0.0, 37.6)

## Spawn del vertical slice: dentro de Z10, sobre el suelo útil (y≈0).
const Z10_SPAWN := Vector3(42.2, 0.12, -22.0)
const Z10_SPAWN_YAW := -PI * 0.5  # mirando +X, hacia el interior de Z10

## Segundo Vigilante: Seguridad queda aislada del principal por el pasillo de
## servicio de 1.4 m (la cápsula del Vigilante mide 2.35 m). Este Vigilante
## patrulla solo el interior de la sala, sobre la malla principal (capa 1).
const SECURITY_WATCHER_SPAWN := Vector3(-88.0, 0.12, -23.0)

## Compuertas runtime. Los anchos salen de la luz libre de cada vano del GLB
## menos la holgura de las guías; no se inventan vanos nuevos.
##   Z10:             x 40,16…45,84 (6,0 m de poste a poste)
##   Recepción N:     x -93,84…-86,16 (8,0 m)
##   Recepción hall:  x -93,84…-86,16 (8,0 m), 4 m al sur del anterior
##   Acceso:          x -38,20…-36,80 (1,4 m)
const GATE_Z10_POSITION := Vector3(43.0, 0.0, -4.0)
const GATE_RECEPTION_NORTH_POSITION := Vector3(-90.0, 0.0, 4.0)
const GATE_RECEPTION_HALL_POSITION := Vector3(-90.0, 0.0, 8.0)
const GATE_ACCESS_POSITION := Vector3(-37.5, 0.0, -4.0)

## Límites de colisión por sector, en coordenadas Godot.
## Z10 cubre el volumen completo del GLB (incluido su enlace norte al corredor).
const Z10_BOUNDS := AABB(Vector3(39.4, -1.6, -35.4), Vector3(31.2, 8.4, 37.8))
const RECEPTION_BOUNDS := AABB(Vector3(-110.5, -1.6, 3.6), Vector3(41.0, 8.0, 37.0))
## Incluye el conector Seguridad-corredor (z -37.2..-4.0): su suelo y muros
## se exportaron a security_connector.glb porque nunca estuvieron en el V06.
const SECURITY_BOUNDS := AABB(Vector3(-106.2, -1.6, -37.2), Vector3(36.2, 8.0, 33.2))
const CORRIDOR_BOUNDS := AABB(Vector3(-100.5, -1.6, -4.5), Vector3(175.0, 8.0, 9.0))
## Pasillo de acceso Seguridad ↔ corredor: AABB exacta del GLB validado
## (security_access_sector.glb). Es una L: tramo largo E-O y tramo N-S.
const SECURITY_ACCESS_BOUNDS := AABB(Vector3(-71.0, -0.2, -11.8), Vector3(34.4, 2.6, 7.8))

## Pasillo de servicio corredor–Vestuarios (ChangingConnector). El máster ya
## tenía el suelo y el muro central de este tramo como kit hero de Z10, pero
## no se habían exportado. Se exportó solo y=30,15…40,15 (Godot z=-40,15…-30,15)
## a lockers_corridor_kit.glb, sin duplicar el kit ya montado de Z10.
const LOCKERS_CORRIDOR_BOUNDS := AABB(Vector3(39.85, -0.2, -39.98), Vector3(6.31, 4.4, 10.14))

## Salas blockout V06. AABB exactas de docs/fm_blockout_rooms_export.json.
## Los GLB ya vienen en coordenadas de mundo: se instancian sin transformar,
## no se recentra ni se escala ninguna malla y no se inventa geometría.
const CONTROL_BOUNDS := AABB(Vector3(-105.15, -0.2, -60.15), Vector3(28.33, 6.2, 24.15))
const LOCKERS_BOUNDS := AABB(Vector3(29.804, -0.2, -64.15), Vector3(30.346, 4.7, 24.33))
const WAREHOUSE_BOUNDS := AABB(Vector3(62.0, -0.2, -38.15), Vector3(48.18, 6.2, 34.15))
const MAINTENANCE_BOUNDS := AABB(Vector3(55.85, -0.2, 4.0), Vector3(56.33, 6.2, 44.15))
const OFFICES_BOUNDS := AABB(Vector3(-30.15, -0.2, -70.15), Vector3(45.34, 4.7, 66.15))
const RESTROOM_BOUNDS := AABB(Vector3(15.0, -0.2, -58.15), Vector3(15.0, 4.2, 16.3))
const STAIRS_MAIN_BOUNDS := AABB(Vector3(-12.15, -4.8, 4.0), Vector3(20.3, 11.8, 46.15))
const STAIRS_E1_BOUNDS := AABB(Vector3(110.0, -4.8, -26.15), Vector3(10.15, 10.8, 18.3))
const STAIRS_E2_BOUNDS := AABB(Vector3(112.0, -4.8, 25.85), Vector3(10.15, 10.8, 18.3))

## Red de rutas alternativas ya modelada en el máster. Se integra fuera de
## `Sectors` porque no es una sala: son túneles de servicio de 1,25 m que
## conectan salas existentes y que el perfil de IA principal no puede usar.
## La AABB cubre las ocho rutas exportadas (EastGallery, MaintCorridor,
## NorthConnector/NorthGallery, OfficesCrawl, ReceptionStair, ServiceLoop y
## NWStair). Godot z = -y del máster.
const ALT_ROUTES_BOUNDS := AABB(
	Vector3(-96.25, -4.8, -70.8),
	Vector3(202.0, 10.8, 103.55)
)

const SECTOR_BOUNDS := {
	"Z10": Z10_BOUNDS,
	"Reception": RECEPTION_BOUNDS,
	"Security": SECURITY_BOUNDS,
	"Corridor": CORRIDOR_BOUNDS,
	"SecurityAccess": SECURITY_ACCESS_BOUNDS,
	"LockersCorridor": LOCKERS_CORRIDOR_BOUNDS,
	"Control": CONTROL_BOUNDS,
	"Lockers": LOCKERS_BOUNDS,
	"Warehouse": WAREHOUSE_BOUNDS,
	"Maintenance": MAINTENANCE_BOUNDS,
	"Offices": OFFICES_BOUNDS,
	"Restroom": RESTROOM_BOUNDS,
	"StairsMain": STAIRS_MAIN_BOUNDS,
	"StairsE1": STAIRS_E1_BOUNDS,
	"StairsE2": STAIRS_E2_BOUNDS,
}

const SECTOR_IDS: Array[String] = [
	"Z10", "Reception", "Security", "Corridor", "SecurityAccess",
	"LockersCorridor", "Control", "Lockers", "Warehouse", "Maintenance",
	"Offices", "Restroom", "StairsMain", "StairsE1", "StairsE2",
]
const BLOCKOUT_IDS: Array[String] = [
	"Control", "Lockers", "Warehouse", "Maintenance", "Offices",
	"Restroom", "StairsMain", "StairsE1", "StairsE2",
]
const SECTOR_ROOTS := {
	"Z10": "Sectors/Z10Art/Z10Sector",
	"Reception": "Sectors/ReceptionArt/ReceptionSector",
	"Security": "Sectors/SecurityArt/SecuritySector",
	"Corridor": "Sectors/CorridorArt/CorridorSector",
	"SecurityAccess": "Sectors/SecurityAccessArt/SecurityAccessSector",
	"LockersCorridor": "Sectors/LockersCorridorArt/LockersCorridorSector",
	"Control": "Sectors/ControlArt/ControlSector",
	"Lockers": "Sectors/LockersArt/LockersSector",
	"Warehouse": "Sectors/WarehouseArt/WarehouseSector",
	"Maintenance": "Sectors/MaintenanceArt/MaintenanceSector",
	"Offices": "Sectors/OfficesArt/OfficesSector",
	"Restroom": "Sectors/RestroomArt/RestroomSector",
	"StairsMain": "Sectors/StairsMainArt/StairsMainSector",
	"StairsE1": "Sectors/StairsE1Art/StairsE1Sector",
	"StairsE2": "Sectors/StairsE2Art/StairsE2Sector",
}

## Identidad funcional y estado propio de cada sala blockout. `state` es
## distinto por sala y lo consumen el HUD y la prueba de humo; `hud` es la
## línea de contexto que se muestra al entrar en su volumen.
const BLOCKOUT_CONTEXT := {
	"Control": {
		"title": "CONTROL DE ACCESO",
		"function": "Filtro de acceso entre Seguridad, el corredor norte y la escalera de emergencia 12C.",
		"state": "BLOCKOUT · FILTRO DE ACCESO",
		"hud": "CONTROL DE ACCESO · FILTRO NORTE",
	},
	"Lockers": {
		"title": "VESTUARIOS",
		"function": "Taquillas, cambio de equipo y acceso de servicio del personal de recuperación.",
		"state": "BLOCKOUT · TAQUILLAS Y CAMBIO",
		"hud": "VESTUARIOS · CAMBIO DE EQUIPO",
	},
	"Warehouse": {
		"title": "ALMACÉN / SUMINISTROS",
		"function": "Almacén de suministros y zona de carga con tres vanos y doce columnas.",
		"state": "BLOCKOUT · SUMINISTROS Y CARGA",
		"hud": "ALMACÉN · SUMINISTROS Y CARGA",
	},
	"Maintenance": {
		"title": "MANTENIMIENTO",
		"function": "Sala técnica de infraestructura: quince columnas y vanos al corredor y a la escalera E2.",
		"state": "BLOCKOUT · INFRAESTRUCTURA",
		"hud": "MANTENIMIENTO · INFRAESTRUCTURA",
	},
	"Offices": {
		"title": "OFICINAS / ADMINISTRACIÓN",
		"function": "Área administrativa con acceso norte-sur desde el corredor y puerta este al enlace de Aseo.",
		"state": "BLOCKOUT · ADMINISTRACIÓN",
		"hud": "OFICINAS · ADMINISTRACIÓN",
	},
	"Restroom": {
		"title": "ASEO DE PLANTA",
		"function": "Aseo pequeño y claustrofóbico accesible desde el enlace con Oficinas.",
		"state": "BLOCKOUT · ASEO DE PLANTA",
		"hud": "ASEO · PLANTA",
	},
	"StairsMain": {
		"title": "ESCALERAS PRINCIPALES",
		"function": "Núcleo vertical principal con 24 peldaños hacia la meseta del Nivel 2.",
		"state": "BLOCKOUT · NÚCLEO VERTICAL",
		"hud": "ESCALERAS PRINCIPALES · NIVEL 1→2",
	},
	"StairsE1": {
		"title": "ESCALERA DE EMERGENCIA E1",
		"function": "Salida de emergencia este con 24 peldaños hacia el Nivel 2, accesible desde el Almacén.",
		"state": "BLOCKOUT · SALIDA E1",
		"hud": "SALIDA DE EMERGENCIA E1",
	},
	"StairsE2": {
		"title": "ESCALERA DE EMERGENCIA E2",
		"function": "Salida de emergencia este con 24 peldaños hacia el Nivel 2, accesible desde Mantenimiento.",
		"state": "BLOCKOUT · SALIDA E2",
		"hud": "SALIDA DE EMERGENCIA E2",
	},
}

## Orden de resolución del contexto por volumen. Las salas blockout se
## comprueban antes que los sectores existentes porque sus AABB se solapan en
## las juntas (p. ej. Almacén con Z10, Control con Seguridad).
const BLOCKOUT_CONTEXT_ORDER: Array[String] = [
	"Control", "Restroom", "Lockers", "StairsE1", "Warehouse",
	"StairsE2", "Maintenance", "StairsMain", "Offices",
]

## Duplicados exactos detectados entre blockout_warehouse.glb y el arte Z10
## ya montado (mismas AABB al milímetro). Se ocultan solo en el Almacén para
## evitar z-fighting; Z10 conserva la copia visible y la colisión del Almacén
## se construye antes de ocultarlas, así que el volumen físico no cambia.
const BLOCKOUT_DUPLICATES := {
	"Warehouse": [
		"SM_L1_Conn_ServiceLink_Ceiling",
		"SM_L1_Conn_ServiceLink_Floor",
		"SM_L1_Conn_ServiceLink_Wall_N_0",
		"SM_L1_Conn_ServiceLink_Wall_S_0",
		"SM_L1_Zone06_Warehouse_Wall_W_1",
	],
}

## Bloqueos del blockout que ya están resueltos. Se conserva el registro para
## que la prueba de humo compruebe la solución real y no una suposición; no se
## inventó ninguna habitación: el pasillo usa la geometría del máster y las
## puertas usan enlaces de navegación sobre los vanos existentes.
const BLOCKOUT_BLOCKERS := []
const BLOCKOUT_RESOLUTIONS := [
	{
		"id": "LockersCorridor",
		"rooms": "Lockers ↔ Z10/Corredor",
		"resolution": "Pasillo cerrado y transitable. Se exportó solo el tramo que faltaba desde el máster (suelo, muro central x=46 y cierre oeste/techo) a lockers_corridor_kit.glb; no se duplicó el kit ya montado de Z10. La prueba recorre el pasillo a pie desde el corredor de Z10 hasta Vestuarios y comprueba suelo, muro y techo con rayos.",
		"geometry_invented": false,
		"verified_by": "smoke: lockers_corridor_floor/wall/ceiling + lockers_corridor_walk",
	},
	{
		"id": "StairsLowerLanding",
		"rooms": "StairsMain / StairsE1 / StairsE2",
		"resolution": "Las tres mesetas inferiores (y=-4,5) son zonas seguras: se añadió un suelo de seguridad bajo cada una y el respawn solo se dispara fuera de los tres huecos de escalera, o si el jugador cae por debajo de -5,6. No se implementa el Nivel 2; los tres núcleos terminan en mesetas cerradas por la geometría existente.",
		"geometry_invented": false,
		"verified_by": "smoke: stairs_main_landing_walk + is_in_stair_safe_zone",
	},
	{
		"id": "BlockoutDoorNavHeight",
		"rooms": "Restroom / StairsE1 / StairsE2 / Lockers / Control",
		"resolution": "Se añadieron seis NavigationLink3D de capa 1 en los vanos de 2,44 m: enlace Oficinas↔Aseo (x=15), Aseo (x=18), E1 (x=110), E2 (x=112), Vestuarios (z=-40) y Control (z=-40). No se cambia el perfil de navegación ni la geometría. Las puertas de servicio de Control (x=-77) y Vestuarios (x=56..60) no tienen malla al otro lado y quedan como salidas selladas, no como rutas.",
		"geometry_invented": false,
		"verified_by": "smoke: nav_door_* rutas reales con NavigationAgent3D",
	},
]

## Navegación. La malla principal cubre Z10, Recepción, Seguridad y Corredor
## con el perfil del Vigilante. El pasillo de acceso a Seguridad mide 1.4 m de
## ancho libre y 2.2 m de alto: Recast no puede rasterizar su suelo con
## radio 0.45/altura 2.2, así que se hornea aparte con un perfil reducido y en
## la capa 2. El Vigilante usa solo la capa 1 (su cápsula de 2.35 m tampoco
## cabe físicamente en ese pasillo de servicio).
const NAV_AGENT_RADIUS := 0.45
const NAV_AGENT_HEIGHT := 2.20
const NAV_AGENT_MAX_CLIMB := 0.30
const NAV_MAX_SLOPE := 45.0
const NAV_CELL_SIZE := 0.25
const NAV_CELL_HEIGHT := 0.25
const NAV_SERVICE_RADIUS := 0.20
const NAV_SERVICE_HEIGHT := 1.70
const NAV_LAYER_DEFAULT := 1
const NAV_LAYER_SERVICE := 2
const NAV_LAYER_ALL := NAV_LAYER_DEFAULT | NAV_LAYER_SERVICE
const NAV_SOURCE_MAIN := &"fm_l1v06_nav_main"
const NAV_SOURCE_SERVICE := &"fm_l1v06_nav_service"
## Enlaces de la capa 2: entrada del pasillo de servicio y compuerta R21C.
const NAV_SERVICE_ENTRY_A := Vector3(-37.5, 0.30, -3.6)
const NAV_SERVICE_ENTRY_B := Vector3(-37.5, 0.30, -4.9)
const NAV_HATCH_EAST := Vector3(-70.5, 0.30, -10.9)
const NAV_HATCH_WEST := Vector3(-73.4, 0.30, -10.9)

## Enlaces de las puertas blockout de 2,44 m de luz. El perfil del agente
## principal (radio 0,45 · altura 2,20 + voxel 0,25) no encadena ruta por el
## vano, aunque la cápsula del jugador sí pasa. Cada enlace une dos superficies
## de navegación ya horneadas en la capa 1; no se cambia el perfil ni se toca
## la geometría. Aseo necesita dos enlaces porque su acceso tiene dos puertas
## consecutivas (Oficinas x=15 y Aseo x=18).
## Enlace de la mezzanine: el último tramo de la rampa queda por debajo del
## perfil del agente (techo de la plataforma) y el navmesh no encadena los dos
## polígonos. El enlace une el final navegable de la rampa con la plataforma.
const NAV_MEZZ_LINK_A := Vector3(88.35, 2.24, -25.90)
const NAV_MEZZ_LINK_B := Vector3(88.35, 2.99, -28.00)
const NAV_DOOR_LINKS := [
	{
		"name": "NavLink_OfficesAseo_W",
		"door": "Aseo · Oficinas x=15",
		"a": Vector3(13.6, 0.30, -49.0),
		"b": Vector3(16.4, 0.30, -49.0),
	},
	{
		"name": "NavLink_Aseo_W",
		"door": "Aseo x=18",
		"a": Vector3(16.6, 0.30, -49.0),
		"b": Vector3(19.4, 0.30, -49.0),
	},
	{
		"name": "NavLink_StairsE1_E",
		"door": "StairsE1 x=110",
		"a": Vector3(108.6, 0.30, -12.0),
		"b": Vector3(111.4, 0.30, -12.0),
	},
	{
		"name": "NavLink_StairsE2_E",
		"door": "StairsE2 x=112",
		"a": Vector3(110.6, 0.30, 38.0),
		"b": Vector3(113.4, 0.30, 38.0),
	},
	{
		"name": "NavLink_Lockers_S",
		"door": "Vestuarios z=-40",
		"a": Vector3(43.0, 0.30, -38.6),
		"b": Vector3(43.0, 0.30, -41.4),
	},
	{
		"name": "NavLink_Control_N",
		"door": "Control z=-40",
		"a": Vector3(-94.0, 0.30, -38.6),
		"b": Vector3(-94.0, 0.30, -41.4),
	},
	{
		"name": "NavLink_SecurityConnector",
		"door": "Seguridad · corredor z=-4",
		"a": Vector3(-89.0, 0.30, -3.40),
		"b": Vector3(-89.0, 0.30, -4.60),
	},
	{
		"name": "NavLink_Security_N",
		"door": "Seguridad z=-36",
		"a": Vector3(-94.0, 0.30, -34.6),
		"b": Vector3(-94.0, 0.30, -37.4),
	},
]

## Respawn: el V06 no tiene Nivel 2, pero las escaleras sí descienden a la
## meseta de y=-4,5. Para no teletransportar al jugador mientras la recorre,
## las tres cajas de escalera son zonas seguras hasta -5,6 m. Fuera de ellas
## se mantiene el umbral original y<-2,5. Las cajas incluyen peldaños y meseta,
## siempre dentro del hueco cerrado por la geometría existente.
const RESPAWN_Y := -2.5
const STAIR_SAFE_MIN_Y := -5.6
const STAIR_SAFE_ZONES := {
	"StairsMain": AABB(Vector3(-4.15, -5.6, 31.9), Vector3(4.30, 4.10, 12.3)),
	"StairsE1": AABB(Vector3(113.70, -5.6, -26.2), Vector3(2.60, 4.10, 12.3)),
	"StairsE2": AABB(Vector3(115.70, -5.6, 25.9), Vector3(2.60, 4.10, 10.4)),
}

enum State { PLAYING, LOST, WON }

var state: State = State.PLAYING
var player: FMPlayer
var radio: FMRadio
var watcher: FMWatcher
var security_watcher: FMWatcher
var hud: FMHUD
var security_hatch: FMSecurityHatch
var extraction: FMReceptionExtraction
var dismantlable: FMDismantlable
var carry_items: Array[FMCarryItem] = []
var batteries: Array[FMBattery] = []
var radio_supplies: Array[FMRadioSupply] = []
var hiding_spots: Array[FMHidingSpot] = []
var level_gates: Array[FMLevel1Gate] = []
var extraction_marker: Node3D
var extraction_ring: MeshInstance3D
var extraction_sign: Label3D
var extraction_floor_label: Label3D
var extraction_beacons: Array[MeshInstance3D] = []
var horror_audio: FMHorrorAudio
var world_env: WorldEnvironment
var level_environment: Environment

var sector_roots: Dictionary = {}
var collider_counts: Dictionary = {}
var merge_stats: Dictionary = {}
var hidden_duplicate_meshes: Array[String] = []
var respawn_count := 0
var door_noise_count := 0
var level_ready := false

var nav_main_region: NavigationRegion3D
var nav_service_region: NavigationRegion3D
var nav_hatch_link: NavigationLink3D
var nav_door_links: Array[NavigationLink3D] = []
var nav_main_polygons := 0
var nav_service_polygons := 0
var nav_bake_ms := 0
var nav_service_bake_ms := 0

var alt_routes_root: Node3D
var alt_routes_collider_count := 0

var _status_timer := 0.0
var _extraction_busy := false


func _ready() -> void:
	if DisplayServer.get_name() != "headless":
		DisplayServer.window_set_size(Vector2i(1280, 720))
	_setup_art()
	if get_node_or_null("Sectors") == null:
		push_error("FM_LEVEL1_V06: falta el contenedor Sectors")
		return
	await get_tree().process_frame
	_setup_collisions()
	_setup_alternate_routes()
	_setup_blockout_duplicates()
	_setup_security_hatch()
	if ENABLE_SHELL_MATERIALS:
		SHELL_MATERIALS.apply(self)
	if ENABLE_SECURITY_MATERIALS:
		var security_root := get_node_or_null("Sectors/SecurityArt") as Node3D
		if security_root != null:
			SECURITY_MATERIALS.apply(security_root)
	if ENABLE_OCCLUDERS:
		OCCLUDERS.apply(self)
	_setup_static_merge()
	_setup_safety_floors()
	_setup_navigation()
	# Compuertas después del horneado: no alteran la malla de navegación
	# aprobada y su colisión se mueve con la persiana al abrir.
	_setup_gates()
	# Gameplay después del horneado: el puesto de análisis tiene colisión
	# estática propia y no debe alterar la malla de navegación aprobada.
	_setup_loot()
	_setup_hiding_spots()
	_setup_batteries()
	_setup_radio_supplies()
	_setup_extraction()
	_setup_player()
	_setup_audio()
	_setup_watcher()
	_setup_security_watcher()
	_setup_hud()
	level_ready = true
	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	print("FM_LEVEL1_V06_READY sectors=%d z10=%d reception=%d security=%d corridor=%d access=%d blockout=%d dedup=%d resolutions=%d gates=%d door_links=%d spawn=%s" % [
		sector_roots.size(),
		int(collider_counts.get("Z10", 0)),
		int(collider_counts.get("Reception", 0)),
		int(collider_counts.get("Security", 0)),
		int(collider_counts.get("Corridor", 0)),
		int(collider_counts.get("SecurityAccess", 0)),
		get_blockout_ready_count(),
		hidden_duplicate_meshes.size(),
		BLOCKOUT_RESOLUTIONS.size(),
		level_gates.size(),
		nav_door_links.size(),
		str(Z10_SPAWN),
	])


func _setup_art() -> void:
	# Las escenas de arte traen su propia WorldEnvironment para lookdev. En el
	# nivel completo solo puede haber un entorno activo: se anula el de los
	# sectores y se conserva el WorldEnvironment único de level1_v06.tscn.
	for path in [
		"Sectors/Z10Art/WorldEnvironment",
		"Sectors/ReceptionArt/WorldEnvironment",
	]:
		var sector_world := get_node_or_null(path) as WorldEnvironment
		if sector_world != null:
			sector_world.environment = null

	for path in [
		"Sectors/Z10Art/ArtCamera",
		"Sectors/ReceptionArt/ArtCamera",
	]:
		var art_camera := get_node_or_null(path) as Camera3D
		if art_camera != null:
			art_camera.current = false

	world_env = get_node_or_null("WorldEnvironment") as WorldEnvironment
	if world_env == null:
		push_error("FM_LEVEL1_V06: falta WorldEnvironment")
	elif world_env.environment != null:
		level_environment = world_env.environment


func _setup_collisions() -> void:
	for id in SECTOR_IDS:
		var root := get_node_or_null(String(SECTOR_ROOTS[id])) as Node3D
		if root == null:
			push_error("FM_LEVEL1_V06: no se encontró la raíz del sector %s" % id)
			continue
		sector_roots[id] = root
		var sector_bounds: AABB = SECTOR_BOUNDS[id]
		var result: Dictionary = COLLISION_HELPER.build(self, root, sector_bounds)
		var body := result.get("body") as StaticBody3D
		if body != null:
			body.name = "Collision_%s" % id
		collider_counts[id] = int(result.get("count", 0))
		print("FM_LEVEL1_V06_COLLISION sector=%s count=%d trimesh=%d" % [
			id, int(collider_counts[id]), int(result.get("trimesh", 0)),
		])


## Colisiones de la red de rutas alternativas. Se construyen antes de la
## fusión estática y del horneado de navegación para que sus suelos formen
## parte del mapa físico. El perfil del Vigilante (2,20 m) no generará
## polígonos dentro de los túneles de 1,25 m; el jugador agachado sí pasa.
func _setup_alternate_routes() -> void:
	alt_routes_root = get_node_or_null("AlternateRoutes") as Node3D
	if alt_routes_root == null:
		push_error("FM_LEVEL1_V06: falta AlternateRoutes")
		return
	var result: Dictionary = COLLISION_HELPER.build(self, alt_routes_root, ALT_ROUTES_BOUNDS)
	var body := result.get("body") as StaticBody3D
	if body != null:
		body.name = "Collision_AlternateRoutes"
	alt_routes_collider_count = int(result.get("count", 0))
	print("FM_LEVEL1_V06_ALT_ROUTES colliders=%d trimesh=%d bounds=%s" % [
		alt_routes_collider_count, int(result.get("trimesh", 0)), str(ALT_ROUTES_BOUNDS),
	])


## Deduplica las mallas que blockout_warehouse.glb comparte literalmente con
## Z10. Se ejecuta después de construir colisiones (el volumen físico no
## cambia) y antes de la fusión estática (FMStaticMerge no fusiona invisibles).
## No se borra ningún nodo: las mallas quedan ocultas y auditables por nombre.
func _setup_blockout_duplicates() -> void:
	hidden_duplicate_meshes.clear()
	for id in BLOCKOUT_DUPLICATES:
		var root := sector_roots.get(id) as Node3D
		if root == null:
			push_error("FM_LEVEL1_V06: falta el sector %s para deduplicar" % id)
			continue
		for mesh_name in BLOCKOUT_DUPLICATES[id]:
			var mesh := root.find_child(String(mesh_name), true, false) as MeshInstance3D
			if mesh == null:
				push_error("FM_LEVEL1_V06: duplicado esperado no encontrado %s/%s" % [id, mesh_name])
				continue
			mesh.visible = false
			hidden_duplicate_meshes.append(String(mesh_name))
	print("FM_LEVEL1_V06_BLOCKOUT_DEDUP sector=Warehouse hidden=%d source=Z10 meshes=%s" % [
		hidden_duplicate_meshes.size(), str(hidden_duplicate_meshes),
	])
	for id in BLOCKOUT_IDS:
		var context: Dictionary = BLOCKOUT_CONTEXT.get(id, {})
		print("FM_LEVEL1_V06_BLOCKOUT room=%s colliders=%d bounds=%s state=%s" % [
			id, int(collider_counts.get(id, 0)), str(SECTOR_BOUNDS[id]),
			String(context.get("state", "")),
		])


## Primer pase de optimización de draw calls: fusiona el arte estático por
## celda espacial + material + formato de superficie. Se ejecuta después de
## construir colisiones y de configurar la compuerta de Seguridad, y antes del
## horneado de navegación (que solo lee colisiones). Las mallas originales se
## conservan ocultas: nombres, AABB de sector y colliders no cambian.
func _setup_static_merge() -> void:
	if not ENABLE_STATIC_MERGE:
		print("FM_LEVEL1_V06_MERGE disabled")
		return
	var total_ms := 0
	var total_hidden := 0
	var total_nodes := 0
	var total_source_surfaces := 0
	var total_output_surfaces := 0
	for id in SECTOR_IDS:
		var root := sector_roots.get(id) as Node3D
		if root == null:
			continue
		var stats: Dictionary = STATIC_MERGE.merge_sector(self, root, id, {
			"cell_size": STATIC_MERGE_CELL_SIZE,
			"max_diagonal": STATIC_MERGE_MAX_DIAGONAL,
			"skip_transparent": STATIC_MERGE_SKIP_TRANSPARENT,
		})
		merge_stats[id] = stats
		total_ms += int(stats.get("merge_ms", 0))
		total_hidden += int(stats.get("hidden_meshes", 0))
		total_nodes += int(stats.get("merged_nodes", 0))
		total_source_surfaces += int(stats.get("source_surfaces", 0))
		total_output_surfaces += int(stats.get("output_surfaces", 0))
		print("FM_LEVEL1_V06_MERGE sector=%s nodes=%d hidden=%d skipped=%d skipped_big=%d skipped_dynamic=%d skipped_nonuniform=%d skipped_transparent=%d src_surfaces=%d out_surfaces=%d failed=%d ms=%d" % [
			id, int(stats.get("merged_nodes", 0)), int(stats.get("hidden_meshes", 0)),
			int(stats.get("skipped_meshes", 0)),
			int(stats.get("skipped_big", 0)), int(stats.get("skipped_dynamic", 0)),
			int(stats.get("skipped_nonuniform", 0)), int(stats.get("skipped_transparent", 0)),
			int(stats.get("source_surfaces", 0)), int(stats.get("output_surfaces", 0)),
			int(stats.get("failed_buckets", 0)), int(stats.get("merge_ms", 0)),
		])
	print("FM_LEVEL1_V06_MERGE_TOTAL merged_nodes=%d hidden_meshes=%d src_surfaces=%d out_surfaces=%d ms=%d" % [
		total_nodes, total_hidden, total_source_surfaces, total_output_surfaces, total_ms,
	])


func _setup_security_hatch() -> void:
	var security_root := sector_roots.get("Security") as Node3D
	var collision_body := get_node_or_null("Collision_Security") as StaticBody3D
	if security_root == null or collision_body == null:
		push_error("FM_LEVEL1_V06: no se puede configurar la compuerta de Seguridad")
		return
	security_hatch = FMSecurityHatch.new()
	security_hatch.name = "SecurityHatch"
	add_child(security_hatch)
	if not security_hatch.setup(security_root, collision_body, self):
		push_error("FM_LEVEL1_V06: la compuerta R21C de Seguridad no se pudo abrir con seguridad")
		security_hatch.queue_free()
		security_hatch = null


func _setup_safety_floors() -> void:
	# Suelo de seguridad invisible bajo cada sector. El corredor lo necesita
	# porque su losa es una única malla de 174 m y FMGLBCollision descarta las
	# mallas con diagonal > 70 m. El resto evita caídas en los huecos de unión.
	# Z10 termina en su muro sur (z=-30,15): el tramo que antes invadía el
	# pasillo ya está cubierto por la losa real y por su propio respaldo.
	_add_safety_floor("SafetyFloor_Z10", Vector3(55.0, -0.26, -14.325), Vector3(30.6, 0.5, 31.65))
	_add_safety_floor("SafetyFloor_Reception", Vector3(-90.0, -0.26, 22.0), Vector3(40.5, 0.5, 36.6))
	_add_safety_floor("SafetyFloor_Security", Vector3(-88.0, -0.26, -23.0), Vector3(36.0, 0.5, 28.2))
	_add_safety_floor("SafetyFloor_Corridor", Vector3(-13.0, -0.26, 0.0), Vector3(175.0, 0.5, 8.6))
	# Une la losa del pasillo de acceso con Seguridad y con el corredor. Sus
	# mallas ya se tocan, pero el suelo del corredor es una única malla de
	# 174 m que FMGLBCollision descarta, así que este respaldo evita caídas en
	# las juntas.
	_add_safety_floor("SafetyFloor_SecurityAccess", Vector3(-53.8, -0.26, -7.9), Vector3(34.4, 0.5, 7.8))
	# Pasillo corredor–Vestuarios: respaldo continuo bajo las tres losas del
	# kit hero, sin invadir Vestuarios.
	_add_safety_floor(
		"SafetyFloor_LockersCorridor", Vector3(43.0, -0.26, -35.05), Vector3(6.4, 0.5, 10.3)
	)
	# Mesetas inferiores de las tres escaleras. La geometría del blockout ya
	# tiene la losa, pero el respaldo garantiza que el jugador que baja los 24
	# peldaños no caiga por una junta y que el respawn no lo trate como caída.
	_add_safety_floor(
		"SafetyFloor_StairsMainLanding", Vector3(-2.0, -4.76, 41.36), Vector3(4.0, 0.5, 5.28)
	)
	_add_safety_floor(
		"SafetyFloor_StairsE1Landing", Vector3(115.0, -4.76, -23.36), Vector3(2.0, 0.5, 5.28)
	)
	_add_safety_floor(
		"SafetyFloor_StairsE2Landing", Vector3(117.0, -4.76, -27.64), Vector3(2.0, 0.5, 3.28)
	)


func _add_safety_floor(body_name: String, center: Vector3, size: Vector3) -> void:
	var body := StaticBody3D.new()
	body.name = body_name
	body.collision_layer = 1
	body.collision_mask = 0
	body.position = center
	var shape := BoxShape3D.new()
	shape.size = size
	var collider := CollisionShape3D.new()
	collider.shape = shape
	body.add_child(collider)
	add_child(body)


func _setup_navigation() -> void:
	# Horneado desde las colisiones estáticas ya construidas (sectores +
	# suelos de seguridad + compuerta). No se parsean los GLB ni sus 2,2 M de
	# triángulos visuales.
	var map := get_world_3d().navigation_map
	NavigationServer3D.map_set_cell_size(map, NAV_CELL_SIZE)
	NavigationServer3D.map_set_cell_height(map, NAV_CELL_HEIGHT)

	add_to_group(NAV_SOURCE_MAIN)
	var main_result := _bake_navigation_region(
		"NavigationMain", NAV_SOURCE_MAIN, NAV_AGENT_RADIUS, NAV_AGENT_HEIGHT, NAV_LAYER_ALL
	)
	nav_main_region = main_result.get("region") as NavigationRegion3D
	nav_main_polygons = int(main_result.get("polygons", 0))
	nav_bake_ms = int(main_result.get("bake_ms", 0))
	remove_from_group(NAV_SOURCE_MAIN)

	# Pasillo de servicio: solo su cuerpo de colisión, perfil reducido y capa 2.
	var access_body := get_node_or_null("Collision_SecurityAccess") as StaticBody3D
	if access_body != null:
		access_body.add_to_group(NAV_SOURCE_SERVICE)
		var service_result := _bake_navigation_region(
			"NavigationService", NAV_SOURCE_SERVICE, NAV_SERVICE_RADIUS, NAV_SERVICE_HEIGHT, NAV_LAYER_SERVICE
		)
		nav_service_region = service_result.get("region") as NavigationRegion3D
		nav_service_polygons = int(service_result.get("polygons", 0))
		nav_service_bake_ms = int(service_result.get("bake_ms", 0))
		access_body.remove_from_group(NAV_SOURCE_SERVICE)
	else:
		push_error("FM_LEVEL1_V06: falta Collision_SecurityAccess para la navegación de servicio")

	var entry_link := NavigationLink3D.new()
	entry_link.name = "ServiceEntryNavLink"
	entry_link.navigation_layers = NAV_LAYER_SERVICE
	entry_link.start_position = NAV_SERVICE_ENTRY_A
	entry_link.end_position = NAV_SERVICE_ENTRY_B
	entry_link.bidirectional = true
	entry_link.enabled = true
	add_child(entry_link)

	nav_hatch_link = NavigationLink3D.new()
	nav_hatch_link.name = "HatchNavLink"
	nav_hatch_link.navigation_layers = NAV_LAYER_SERVICE
	nav_hatch_link.start_position = NAV_HATCH_EAST
	nav_hatch_link.end_position = NAV_HATCH_WEST
	nav_hatch_link.bidirectional = true
	nav_hatch_link.enabled = security_hatch != null and security_hatch.is_open
	add_child(nav_hatch_link)
	if security_hatch != null:
		security_hatch.state_changed.connect(_on_security_hatch_state_changed)

	# Enlaces de capa 1 en los vanos de 2,44 m. Se crean después del horneado
	# y no alteran la malla: solo conectan dos polígonos existentes a cada lado
	# del umbral. El agente principal puede así entrar en Aseo, E1, E2,
	# Vestuarios y Control sin bajar su altura ni la resolución del voxel.
	nav_door_links.clear()
	for entry in NAV_DOOR_LINKS:
		var link := NavigationLink3D.new()
		link.name = String(entry["name"])
		link.navigation_layers = NAV_LAYER_DEFAULT
		link.start_position = entry["a"]
		link.end_position = entry["b"]
		link.bidirectional = true
		link.enabled = true
		add_child(link)
		nav_door_links.append(link)

	# Enlace de la rampa de la mezzanine (capa 1).
	var mezz_link := NavigationLink3D.new()
	mezz_link.name = "NavLink_Mezzanine"
	mezz_link.navigation_layers = NAV_LAYER_DEFAULT
	mezz_link.start_position = NAV_MEZZ_LINK_A
	mezz_link.end_position = NAV_MEZZ_LINK_B
	mezz_link.bidirectional = true
	mezz_link.enabled = true
	add_child(mezz_link)

	print("FM_LEVEL1_V06_NAVIGATION main_polys=%d service_polys=%d main_bake_ms=%d service_bake_ms=%d layers_main=%d layers_service=%d door_links=%d" % [
		nav_main_polygons, nav_service_polygons, nav_bake_ms, nav_service_bake_ms,
		NAV_LAYER_ALL, NAV_LAYER_SERVICE, nav_door_links.size(),
	])


func _bake_navigation_region(
	region_name: String, source_group: StringName, radius: float, height: float, layers: int
) -> Dictionary:
	var region := NavigationRegion3D.new()
	region.name = region_name
	region.navigation_layers = layers
	var nav_mesh := NavigationMesh.new()
	nav_mesh.agent_radius = radius
	nav_mesh.agent_height = height
	nav_mesh.agent_max_climb = NAV_AGENT_MAX_CLIMB
	nav_mesh.agent_max_slope = NAV_MAX_SLOPE
	nav_mesh.cell_size = NAV_CELL_SIZE
	nav_mesh.cell_height = NAV_CELL_HEIGHT
	nav_mesh.region_min_size = 1.0
	nav_mesh.geometry_parsed_geometry_type = NavigationMesh.PARSED_GEOMETRY_STATIC_COLLIDERS
	nav_mesh.geometry_collision_mask = 1
	nav_mesh.geometry_source_geometry_mode = NavigationMesh.SOURCE_GEOMETRY_GROUPS_WITH_CHILDREN
	nav_mesh.geometry_source_group_name = source_group
	region.navigation_mesh = nav_mesh
	add_child(region)
	var started := Time.get_ticks_msec()
	region.bake_navigation_mesh(false)
	var bake_ms := Time.get_ticks_msec() - started
	# Reasignar fuerza la sincronización de la malla recién horneada en el mapa.
	region.navigation_mesh = null
	region.navigation_mesh = nav_mesh
	return {
		"region": region,
		"polygons": nav_mesh.get_polygon_count(),
		"bake_ms": bake_ms,
	}


func _on_security_hatch_state_changed(open: bool) -> void:
	if nav_hatch_link != null and is_instance_valid(nav_hatch_link):
		nav_hatch_link.enabled = open


# ---------------------------------------------------------------------------
# Compuertas runtime de los vanos anchos
# ---------------------------------------------------------------------------

func _setup_gates() -> void:
	_add_gate("Z10", "Z10", 5.50, 2.98, GATE_Z10_POSITION, -1.0, 12.0)
	_add_gate(
		"Reception_North", "VESTÍBULO", 7.50, 2.98,
		GATE_RECEPTION_NORTH_POSITION, -1.0, 14.0
	)
	_add_gate(
		"Reception_Hall", "RECEPCIÓN", 7.50, 2.98,
		GATE_RECEPTION_HALL_POSITION, -1.0, 14.0
	)
	_add_gate("Access", "ACCESO", 1.18, 2.10, GATE_ACCESS_POSITION, 1.0, 8.0)
	if level_gates.size() != 4:
		push_error("FM_LEVEL1_V06: se esperaban 4 compuertas y hay %d" % level_gates.size())


func _add_gate(
	id: String, label: String, gate_width: float, gate_height: float,
	pos: Vector3, facing: float, noise: float
) -> FMLevel1Gate:
	var gate := GATE_SCRIPT.new() as FMLevel1Gate
	gate.position = pos
	add_child(gate)
	gate.noise_radius = noise
	gate.setup(id, gate_width, gate_height, label, facing, self)
	level_gates.append(gate)
	return gate


# ---------------------------------------------------------------------------
# Gameplay: loot, desmontaje, recursos, escondites y extracción
# ---------------------------------------------------------------------------

func _setup_loot() -> void:
	# Núcleo de misión: objeto mediano que se transporta en las manos.
	var core := CARRY_ITEM_SCENE.instantiate() as FMCarryItem
	core.name = "Loot_Core_Z10"
	core.item_name = "NÚCLEO DE CONTENCIÓN"
	core.item_mass = 7.0
	core.size_class = "MEDIUM"
	core.item_kind = "core"
	core.is_mission_item = true
	core.visual_style = "CORE"
	core.position = CORE_POSITION
	core.rotation.y = 0.35
	core.game = self
	add_child(core)
	register_carry_item(core)

	# Puesto de análisis: libera 4 componentes pequeños al completarse y los
	# registra en carry_items a través de register_carry_item.
	dismantlable = DISMANTLE_SCRIPT.new()
	dismantlable.name = "AnalysisStation_Z10"
	dismantlable.display_name = "PUESTO DE ANÁLISIS"
	dismantlable.position = DISMANTLE_POSITION
	dismantlable.rotation.y = PI * 0.5
	dismantlable.game = self
	add_child(dismantlable)

	# Componentes/documentos adicionales fuera del eje directo de paso.
	_add_component_loot(
		"Loot_Reception_Doc", "DOCUMENTO DE RECEPCIÓN",
		LOOT_RECEPTION_DOC_POSITION, 0.4, "document",
		Color(0.78, 0.74, 0.62)
	)
	_add_component_loot(
		"Loot_Reception_Component", "COMPONENTE DE CONTROL",
		LOOT_RECEPTION_COMPONENT_POSITION, 0.9, "component",
		Color(0.30, 0.58, 0.76)
	)
	_add_component_loot(
		"Loot_Security_Doc", "DOCUMENTO DE SEGURIDAD",
		LOOT_SECURITY_DOC_POSITION, 0.5, "document",
		Color(0.72, 0.70, 0.58)
	)


func _add_component_loot(
	node_name: String, item_label: String, pos: Vector3, item_mass: float,
	kind: String, color: Color
) -> FMCarryItem:
	var item := CARRY_ITEM_SCENE.instantiate() as FMCarryItem
	item.name = node_name
	item.item_name = item_label
	item.item_mass = item_mass
	item.size_class = "SMALL"
	item.item_kind = kind
	item.is_mission_item = false
	item.visual_style = "COMPONENT"
	item.display_color = color
	item.position = pos
	item.game = self
	add_child(item)
	register_carry_item(item)
	return item


func _setup_hiding_spots() -> void:
	var shelves := HIDING_SPOT_SCENE.instantiate() as FMHidingSpot
	shelves.name = "HideShelvesZ10"
	shelves.display_name = "ESTANTERÍA"
	shelves.position = Z10_HIDE_POSITION
	shelves.rotation.y = PI
	shelves.game = self
	add_child(shelves)
	_tune_hiding_spot(shelves)
	hiding_spots.append(shelves)

	var lockers := HIDING_SPOT_SCENE.instantiate() as FMHidingSpot
	lockers.name = "HideReceptionLockers"
	lockers.display_name = "TAQUILLAS DE PERSONAL"
	lockers.position = RECEPTION_HIDE_POSITION
	lockers.rotation.y = 0.0
	lockers.game = self
	add_child(lockers)
	_tune_hiding_spot(lockers)
	hiding_spots.append(lockers)

	var security_lockers := HIDING_SPOT_SCENE.instantiate() as FMHidingSpot
	security_lockers.name = "HideSecurityLockers"
	security_lockers.display_name = "TAQUILLAS DE SEGURIDAD"
	security_lockers.position = SECURITY_HIDE_POSITION
	security_lockers.rotation.y = PI
	security_lockers.game = self
	add_child(security_lockers)
	_tune_hiding_spot(security_lockers)
	hiding_spots.append(security_lockers)


func _tune_hiding_spot(spot: FMHidingSpot) -> void:
	var shape := spot.get_node_or_null("CollisionShape3D") as CollisionShape3D
	if shape != null:
		shape.position.y = 1.05
	var exit_point := spot.get_node_or_null("ExitPoint") as Marker3D
	if exit_point != null:
		exit_point.position = Vector3(0.0, 0.0, 1.25)
	var hide_point := spot.get_node_or_null("HidePoint") as Marker3D
	if hide_point != null:
		hide_point.position = Vector3.ZERO


func _setup_batteries() -> void:
	_add_battery("Battery_Z10_Storage", BATTERY_Z10_POSITION, 70.0)
	_add_battery("Battery_Reception_West", BATTERY_RECEPTION_POSITION, 85.0)


func _add_battery(battery_name: String, pos: Vector3, charge: float) -> void:
	var battery: FMBattery = BATTERY_SCRIPT.new()
	battery.name = battery_name
	battery.charge_amount = charge
	battery.position = pos
	battery.game = self
	add_child(battery)
	batteries.append(battery)


func _setup_radio_supplies() -> void:
	# Cargadores fijos: rellenan la radio y quedan en espera unos segundos.
	_add_radio_supply("RadioStation_Z10", RADIO_STATION_Z10,
		FMRadioSupply.Kind.STATION, 40.0, 22.0)
	_add_radio_supply("RadioStation_Control", RADIO_STATION_CONTROL,
		FMRadioSupply.Kind.STATION, 40.0, 22.0)
	_add_radio_supply("RadioStation_Warehouse", RADIO_STATION_WAREHOUSE,
		FMRadioSupply.Kind.STATION, 40.0, 22.0)
	_add_radio_supply("RadioStation_Maintenance", RADIO_STATION_MAINTENANCE,
		FMRadioSupply.Kind.STATION, 40.0, 22.0)
	_add_radio_supply("RadioStation_Offices", RADIO_STATION_OFFICES,
		FMRadioSupply.Kind.STATION, 40.0, 22.0)
	_add_radio_supply("RadioStation_Stairs", RADIO_STATION_STAIRS,
		FMRadioSupply.Kind.STATION, 40.0, 22.0)
	_add_radio_supply("RadioStation_NWStair", RADIO_STATION_NWSTAIR,
		FMRadioSupply.Kind.STATION, 40.0, 22.0)

	# Pilas comunes: +30%. Repartidas por salas y rutas alternativas.
	_add_radio_supply("RadioBattery_Z10", Vector3(43.2, 0.02, -25.4),
		FMRadioSupply.Kind.BATTERY, 30.0)
	_add_radio_supply("RadioBattery_Security", Vector3(-89.0, 0.02, -23.0),
		FMRadioSupply.Kind.BATTERY, 30.0)
	_add_radio_supply("RadioBattery_Lockers", Vector3(44.0, 0.02, -52.0),
		FMRadioSupply.Kind.BATTERY, 30.0)
	_add_radio_supply("RadioBattery_Warehouse", Vector3(91.0, 0.02, -30.0),
		FMRadioSupply.Kind.BATTERY, 30.0)
	_add_radio_supply("RadioBattery_Maintenance", Vector3(84.0, 0.02, 30.0),
		FMRadioSupply.Kind.BATTERY, 30.0)
	_add_radio_supply("RadioBattery_Offices", Vector3(-12.0, 0.02, -46.0),
		FMRadioSupply.Kind.BATTERY, 30.0)
	_add_radio_supply("RadioBattery_Restroom", Vector3(24.0, 0.02, -50.0),
		FMRadioSupply.Kind.BATTERY, 30.0)
	_add_radio_supply("RadioBattery_NWStair", Vector3(-70.0, -4.48, -68.0),
		FMRadioSupply.Kind.BATTERY, 30.0)

	# Pilas de alta capacidad: +70%.
	_add_radio_supply("RadioBattery_Warehouse_High",
		Vector3(88.0, 0.02, -34.0), FMRadioSupply.Kind.HIGH_CAPACITY, 70.0)
	_add_radio_supply("RadioBattery_NWStair_High",
		Vector3(-74.0, -4.48, -69.0), FMRadioSupply.Kind.HIGH_CAPACITY, 70.0)


func _add_radio_supply(supply_name: String, pos: Vector3, kind: int,
		charge: float, cooldown := 20.0) -> void:
	var supply: FMRadioSupply = RADIO_SUPPLY_SCRIPT.new()
	supply.name = supply_name
	supply.kind = kind
	supply.charge_amount = charge
	supply.cooldown_seconds = cooldown
	supply.position = pos
	supply.game = self
	add_child(supply)
	radio_supplies.append(supply)


func _setup_extraction() -> void:
	extraction = EXTRACTION_SCRIPT.new()
	extraction.name = "ReceptionExtraction"
	extraction.position = EXTRACTION_POSITION
	extraction.game = self
	extraction.delivery_center = EXTRACTION_CENTER
	extraction.zone_size = EXTRACTION_ZONE_SIZE
	extraction.extraction_started.connect(on_extraction_started)
	extraction.extraction_progress.connect(on_extraction_progress)
	extraction.extraction_completed.connect(on_extraction_completed)
	add_child(extraction)
	_add_extraction_marker()


## Marcador visual de la zona de extracción. Reutiliza el patrón del slice
## (aro, cartel, balizas emisivas) pero sin añadir luces dinámicas: la
## compuerta y el cartel SALIDA ya existen en el GLB de Recepción. La lógica
## de FMReceptionExtraction no se modifica.
func _add_extraction_marker() -> void:
	extraction_marker = Node3D.new()
	extraction_marker.name = "ExtractionMarker"
	extraction_marker.position = EXTRACTION_MARKER_POSITION
	add_child(extraction_marker)

	var ring_mat := StandardMaterial3D.new()
	ring_mat.albedo_color = Color(0.06, 0.45, 0.22, 1.0)
	ring_mat.emission_enabled = true
	ring_mat.emission = Color(0.10, 1.0, 0.46)
	ring_mat.emission_energy_multiplier = 1.35
	ring_mat.roughness = 0.32
	extraction_ring = MeshInstance3D.new()
	extraction_ring.name = "ExtractionRing"
	var torus := TorusMesh.new()
	torus.inner_radius = 1.38
	torus.outer_radius = 1.50
	torus.rings = 40
	torus.ring_segments = 8
	extraction_ring.mesh = torus
	extraction_ring.material_override = ring_mat
	extraction_ring.position = Vector3(0.0, 0.055, 0.0)
	extraction_marker.add_child(extraction_ring)

	extraction_sign = Label3D.new()
	extraction_sign.name = "ExtractionSign"
	extraction_sign.text = "EXTRACCIÓN // RECEPCIÓN"
	extraction_sign.font_size = 32
	extraction_sign.pixel_size = 0.005
	extraction_sign.modulate = Color(0.55, 1.0, 0.66, 1.0)
	extraction_sign.outline_size = 8
	extraction_sign.outline_modulate = Color(0.004, 0.02, 0.008, 0.95)
	extraction_sign.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	extraction_sign.position = Vector3(0.0, 3.15, -0.75)
	extraction_marker.add_child(extraction_sign)

	extraction_floor_label = Label3D.new()
	extraction_floor_label.name = "ExtractionFloorLabel"
	extraction_floor_label.text = "SALIDA"
	extraction_floor_label.font_size = 96
	extraction_floor_label.pixel_size = 0.005
	extraction_floor_label.modulate = Color(0.52, 1.0, 0.64, 1.0)
	extraction_floor_label.outline_size = 10
	extraction_floor_label.outline_modulate = Color(0.004, 0.02, 0.008, 0.95)
	extraction_floor_label.billboard = BaseMaterial3D.BILLBOARD_DISABLED
	extraction_floor_label.rotation = Vector3(-PI * 0.5, PI, 0.0)
	extraction_floor_label.position = Vector3(0.0, 0.065, 0.0)
	extraction_marker.add_child(extraction_floor_label)

	var beacon_mat := StandardMaterial3D.new()
	beacon_mat.albedo_color = Color(0.05, 0.30, 0.14, 1.0)
	beacon_mat.emission_enabled = true
	beacon_mat.emission = Color(0.12, 1.0, 0.46)
	beacon_mat.emission_energy_multiplier = 2.40
	beacon_mat.roughness = 0.28
	for side in [-1.0, 1.0]:
		var beacon := _add_marker_box(
			"ExtractionBeacon_%s" % ("L" if side < 0.0 else "R"),
			Vector3(side * 3.93, 1.45, 2.00),
			Vector3(0.10, 0.48, 0.035),
			beacon_mat
		)
		extraction_beacons.append(beacon)
	print("FM_LEVEL1_V06_EXTRACTION_MARKER pos=%s ring=%.2f sign=%s beacons=%d" % [
		str(extraction_marker.global_position), torus.outer_radius,
		extraction_sign.text, extraction_beacons.size(),
	])


func _add_marker_box(
	node_name: String, pos: Vector3, size: Vector3, material: Material
) -> MeshInstance3D:
	var instance := MeshInstance3D.new()
	instance.name = node_name
	var mesh := BoxMesh.new()
	mesh.size = size
	instance.mesh = mesh
	instance.material_override = material
	instance.position = pos
	extraction_marker.add_child(instance)
	return instance


func _setup_player() -> void:
	player = PLAYER_SCENE.instantiate() as FMPlayer
	player.name = "Player"
	player.position = Z10_SPAWN
	player.rotation.y = Z10_SPAWN_YAW
	add_child(player)
	player.set_game(self)
	player.network_client = false
	player.set_flashlight_model(true)
	player.max_battery = 100.0
	player.battery = 100.0
	player.battery_drain = 0.65
	player.flashlight_on = true
	_tune_flashlight()
	player.add_to_group("fm_player")
	radio = FMRadio.new()
	radio.name = "Radio"
	player.add_child(radio)


func _tune_flashlight() -> void:
	# Linterna de trabajo, no un foco de estadio: cono estrecho y alcance corto
	# para que la sala siga siendo oscura. La batería y el encendido/apagado
	# siguen en FMPlayer; aquí solo se ajustan los parámetros de luz.
	if player == null or player.flashlight == null:
		return
	player.flashlight.light_color = Color(1.0, 0.90, 0.72)
	player.flashlight.light_energy = 9.0
	player.flashlight.spot_range = 20.0
	player.flashlight.spot_angle = 26.0
	player.flashlight.spot_attenuation = 1.20
	player.flashlight.spot_angle_attenuation = 1.05
	player.flashlight.shadow_enabled = true
	player.flashlight.light_volumetric_fog_energy = 3.0
	# Inclina el haz unos grados hacia el suelo: ilumina el camino sin ensanchar
	# el cono ni convertir la linterna en una luz de sala.
	player.flashlight.rotation.x = deg_to_rad(-2.0)
	var gradient := Gradient.new()
	gradient.set_color(0, Color(1.0, 1.0, 1.0, 1.0))
	gradient.set_color(1, Color(0.05, 0.05, 0.05, 1.0))
	var projector := GradientTexture2D.new()
	projector.gradient = gradient
	projector.width = 128
	projector.height = 128
	projector.fill = GradientTexture2D.FILL_RADIAL
	projector.fill_from = Vector2(0.5, 0.5)
	projector.fill_to = Vector2(1.0, 0.5)
	player.flashlight.light_projector = projector
	# Relleno mínimo bajo la vista para no perder los pies; no abre la sala.
	var spill := SpotLight3D.new()
	spill.name = "FlashlightSpill"
	spill.light_color = Color(1.0, 0.86, 0.66)
	spill.light_energy = 1.0
	spill.spot_range = 6.0
	spill.spot_angle = 38.0
	spill.spot_attenuation = 1.6
	spill.spot_angle_attenuation = 1.20
	spill.shadow_enabled = false
	player.camera.add_child(spill)


## Capa ambiental/eventos de terror. Vive en un nodo propio para no mezclar
## audio con la lógica de misión; reutiliza el zumbido industrial existente y
## añade solo texturas nuevas de síntesis propia.
func _setup_audio() -> void:
	if player == null or not is_instance_valid(player):
		return
	horror_audio = HORROR_AUDIO_SCRIPT.new() as FMHorrorAudio
	horror_audio.name = "HorrorAudio"
	add_child(horror_audio)
	horror_audio.setup(player)


func _setup_watcher() -> void:
	watcher = WATCHER_SCENE.instantiate() as FMWatcher
	watcher.name = "Watcher"
	watcher.position = Vector3(59.0, 0.12, -14.5)
	watcher.rotation.y = 0.0
	# Malla principal (capa 1): Z10, corredor y recepción. Seguridad tiene
	# navmesh propio, pero el único acceso es el pasillo de servicio de 1.4 m,
	# demasiado estrecho para la cápsula de 2.35 m del Vigilante.
	watcher.use_navigation = true
	add_child(watcher)
	watcher.set_game(self)
	watcher.set_player(player)
	var patrol: Array[Vector3] = [
		Vector3(59.0, 0.12, -25.0),
		Vector3(45.0, 0.12, -25.0),
		Vector3(45.0, 0.12, -14.5),
		Vector3(59.0, 0.12, -14.5),
	]
	watcher.set_patrol_points(patrol)


## Segundo Vigilante, confinado dentro de Seguridad. Reutiliza la misma
## escena, el mismo agente de navegación (capa 1) y el mismo
## `on_player_caught` del nivel; no crea HUD ni estado de partida propios.
func _setup_security_watcher() -> void:
	security_watcher = WATCHER_SCENE.instantiate() as FMWatcher
	security_watcher.name = "SecurityWatcher"
	security_watcher.position = SECURITY_WATCHER_SPAWN
	security_watcher.rotation.y = 0.0
	security_watcher.use_navigation = true
	add_child(security_watcher)
	security_watcher.set_game(self)
	security_watcher.set_player(player)
	# El acceso principal sur ya está abierto y la malla de capa 1 conecta la
	# sala con el corredor. La patrulla rodea el mostrador por el este, sale al
	# corredor y vuelve; así el Vigilante puede investigar ruidos y perseguir
	# fuera de Seguridad sin quedar confinado tras la apertura del acceso.
	var patrol: Array[Vector3] = [
		Vector3(-84.0, 0.12, -23.0),
		Vector3(-84.0, 0.12, -13.5),
		Vector3(-85.5, 0.12, -11.0),
		Vector3(-89.0, 0.12, -8.0),
		Vector3(-89.0, 0.12, -2.5),
		Vector3(-85.0, 0.12, -2.5),
		Vector3(-85.5, 0.12, -11.0),
		Vector3(-84.0, 0.12, -23.0),
		Vector3(-88.0, 0.12, -23.0),
	]
	security_watcher.set_patrol_points(patrol)
	print("FM_LEVEL1_V06_SECURITY_WATCHER spawn=%s patrol=%d" % [
		str(SECURITY_WATCHER_SPAWN), patrol.size(),
	])


func _setup_hud() -> void:
	hud = HUD_SCRIPT.new() as FMHUD
	hud.name = "HUD"
	add_child(hud)
	hud.set_objective("NIVEL 1 · V06", "Recuperá el núcleo en Z10 y volvé a Recepción")
	hud.set_status("SECTOR Z10 · RECUPERÁ EL NÚCLEO")
	hud.set_battery(player.battery, player.flashlight_on)
	hud.set_stamina(player.stamina)
	hud.set_stress(0.0)
	hud.set_carry(0.0, player.max_carry_weight, 0, player.inventory_capacity)
	hud.set_hint("WASD MOVER   ·   SHIFT CORRER   ·   CTRL AGACHARSE   ·   E INTERACTUAR   ·   Q SOLTAR   ·   F LINTERNA   ·   V RADIO   ·   C CANAL   ·   R REINICIAR   ·   ESC MOUSE")


func _process(delta: float) -> void:
	if not level_ready or player == null or not is_instance_valid(player):
		return

	if hud != null:
		hud.set_battery(player.battery, player.flashlight_on)
		hud.set_stamina(player.stamina)
		hud.set_carry(player.get_carry_weight(), player.max_carry_weight, player.get_inventory_count(), player.inventory_capacity)
		hud.set_prompt(player.get_interaction_prompt())
		hud.set_hidden(player.hidden)
		if radio != null:
			hud.set_radio(radio.get_channel_name(), radio.get_battery_ratio(),
				radio.get_signal_quality(), radio.is_transmitting(),
				radio.get_status_text())
		var observed := (watcher != null and is_instance_valid(watcher) and watcher.observed) \
			or (security_watcher != null and is_instance_valid(security_watcher) and security_watcher.observed)
		hud.set_watcher_observed(observed)

	_status_timer = maxf(0.0, _status_timer - delta)
	if _status_timer <= 0.0 and not _extraction_busy and hud != null:
		_status_timer = 0.5
		hud.set_status(_context_status())

	if _should_respawn(player.global_position):
		_respawn_player()


func _context_status() -> String:
	if state != State.PLAYING:
		return ""
	var p := player.global_position
	# Pasillo de servicio entre Z10 y Vestuarios: tiene identidad propia y no
	# forma parte del lote blockout, así que se resuelve antes.
	if LOCKERS_CORRIDOR_BOUNDS.has_point(p):
		return "PASILLO DE SERVICIO · VESTUARIOS"
	# Las nueve salas blockout tienen contexto y estado propios. Se resuelven
	# antes que los sectores existentes porque sus AABB se tocan en las juntas.
	for id in BLOCKOUT_CONTEXT_ORDER:
		if SECTOR_BOUNDS[id].has_point(p):
			return String(BLOCKOUT_CONTEXT[id]["hud"])
	if p.x < -69.0 and p.z > 3.0:
		if extraction != null and has_delivered_mission_item(EXTRACTION_CENTER, extraction.delivery_radius_m):
			return "NÚCLEO EN ZONA DE EXTRACCIÓN · PERMANECÉ DENTRO"
		if _player_has_mission_item():
			return "LLEVÁ EL NÚCLEO AL PUNTO DE EXTRACCIÓN · ALA SUR"
		if player.get_inventory_count() > 0:
			return "BOTÍN ASEGURADO · LA EXTRACCIÓN REQUIERE EL NÚCLEO"
		return "RECEPCIÓN · LA EXTRACCIÓN REQUIERE EL NÚCLEO"
	if _player_has_mission_item():
		return "NÚCLEO ASEGURADO · VOLVÉ A RECEPCIÓN"
	if p.x > 35.0 and p.z < -5.0:
		return "Z10 · CONECTOR DE SERVICIO"
	if p.x < -69.0:
		return "SEGURIDAD · MONITOREO"
	if p.x >= -71.0 and p.x <= -36.6 and p.z < -4.5:
		return "PASILLO DE ACCESO · SEGURIDAD"
	if absf(p.z) <= 5.5:
		return "CORREDOR PRINCIPAL · NIVEL 1"
	return "NIVEL 1 · SECTOR DESCONOCIDO"


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("restart"):
		get_tree().reload_current_scene()
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("pause"):
		if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
			Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
		else:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		get_viewport().set_input_as_handled()


func notify(text: String) -> void:
	_status_timer = 2.6
	if hud != null:
		hud.set_status(text)


func _respawn_player() -> void:
	if player == null or not is_instance_valid(player):
		return
	respawn_count += 1
	player.global_position = Z10_SPAWN
	player.velocity = Vector3.ZERO
	notify("POSICIÓN RECUPERADA · Z10")


## El V06 no tiene Nivel 2. Las escaleras descienden a y=-4,5 y antes
## disparaban el respawn global (y<-2,5) en la propia meseta, teletransportando
## al jugador sin motivo. La decisión es tratar los tres huecos de escalera
## como zonas válidas: mientras el jugador esté dentro de su caja (peldaños o
## meseta) y por encima de -5,6 m, no se respawnea. Fuera de ellos se conserva
## el umbral original, y por debajo de -5,6 se recupera siempre para no dejar
## al jugador cayendo fuera del nivel.
func is_in_stair_safe_zone(pos: Vector3) -> bool:
	for id in STAIR_SAFE_ZONES:
		if (STAIR_SAFE_ZONES[id] as AABB).has_point(pos):
			return true
	return false


func _should_respawn(pos: Vector3) -> bool:
	if pos.y >= RESPAWN_Y:
		return false
	if pos.y < STAIR_SAFE_MIN_Y:
		return true
	return not is_in_stair_safe_zone(pos)


# ---------------------------------------------------------------------------
# API consumida por FMPlayer / FMWatcher
# ---------------------------------------------------------------------------

func emit_noise(position: Vector3, radius: float, kind: String) -> void:
	if kind == "door":
		door_noise_count += 1
	# Ambos Vigilantes comparten el sistema de percepción sonora del nivel;
	# cada uno filtra el ruido por su propia distancia y estado.
	if watcher != null and is_instance_valid(watcher):
		watcher.hear_noise(position, radius)
	if security_watcher != null and is_instance_valid(security_watcher):
		security_watcher.hear_noise(position, radius)


func clamp_player(who: FMPlayer) -> void:
	if who == null or not is_instance_valid(who):
		return
	# No se limita el recorrido: el nivel V06 es continuo. Solo se recupera al
	# jugador si cae fuera de la geometría o si baja de la meseta segura de una
	# escalera. Las mesetas inferiores son válidas y no disparan respawn.
	if _should_respawn(who.global_position):
		_respawn_player()


func on_player_caught(_who: Node = null) -> void:
	if state != State.PLAYING:
		return
	state = State.LOST
	_extraction_busy = false
	_stop_horror_audio()
	if player != null:
		player.velocity = Vector3.ZERO
	if hud != null:
		hud.show_end("DETECTADO", "El Vigilante te encontró en el Nivel 1. R para reiniciar.")
	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func on_item_collected(_who: Node, item: FMCarryItem) -> void:
	if item == null:
		return
	if item.is_mission_item:
		notify("NÚCLEO RECUPERADO · LLEGALO A RECEPCIÓN")
		if hud != null:
			hud.set_objective("LLEVAR EL NÚCLEO A RECEPCIÓN", "Extracción en el ala sur · nivel 1")
		return
	notify("%s GUARDADO · %s" % [item.item_name, player.get_carry_summary()])


func on_artifact_picked(_who: Node) -> void:
	if player == null or player.carried_item == null:
		return
	var item := player.carried_item as FMCarryItem
	if item == null:
		return
	if item.is_mission_item:
		notify("NÚCLEO RECUPERADO · LLEGALO A RECEPCIÓN")
		if hud != null:
			hud.set_objective("LLEVAR EL NÚCLEO A RECEPCIÓN", "Extracción en el ala sur · nivel 1")
	else:
		notify("%s EN MANOS · LLEGALO A RECEPCIÓN" % item.item_name)


func on_artifact_dropped() -> void:
	notify("OBJETO SOLTADO")


func on_dismantle_completed(_station: Node, components: Array) -> void:
	notify("DESMONTAJE COMPLETADO · %d COMPONENTES" % components.size())
	if hud != null:
		hud.set_status("RECOGÉ LOS COMPONENTES DEL PUESTO DE ANÁLISIS")


func on_battery_taken(_index: int, _who: Node) -> void:
	notify("BATERÍA RECUPERADA")


func on_player_hidden(is_hidden: bool) -> void:
	notify("ESCONDIDO" if is_hidden else "SALISTE DEL ESCONDITE")


func get_active_player_count() -> int:
	return 1 if player != null and is_instance_valid(player) and state == State.PLAYING else 0


# ---------------------------------------------------------------------------
# API consumida por FMReceptionExtraction / FMDismantlable / FMCarryItem
# ---------------------------------------------------------------------------

func register_carry_item(item: FMCarryItem) -> void:
	if item == null or not is_instance_valid(item):
		return
	if not carry_items.has(item):
		carry_items.append(item)


func all_alive_players_inside(area: Area3D) -> bool:
	return area != null and player != null and is_instance_valid(player) \
		and state == State.PLAYING and area.players_inside.has(player)


func any_alive_player_inside(area: Area3D) -> bool:
	return all_alive_players_inside(area)


func get_delivered_loot_count(center: Vector3, radius: float) -> int:
	var delivered := {}
	for item in carry_items:
		if item != null and is_instance_valid(item) and item.global_position.distance_to(center) <= radius:
			delivered[item.get_instance_id()] = true
	if player != null and is_instance_valid(player) and extraction != null \
		and extraction.players_inside.has(player):
		for item in player.inventory:
			if item != null and is_instance_valid(item):
				delivered[item.get_instance_id()] = true
		var carried := player.carried_item as FMCarryItem
		if carried != null and is_instance_valid(carried) and carry_items.has(carried):
			delivered[carried.get_instance_id()] = true
	return delivered.size()


func has_delivered_mission_item(center: Vector3, radius: float) -> bool:
	for item in carry_items:
		if item != null and is_instance_valid(item) and item.is_mission_item \
			and item.global_position.distance_to(center) <= radius:
			return true
	if player != null and is_instance_valid(player) and extraction != null \
		and extraction.players_inside.has(player):
		var carried := player.carried_item as FMCarryItem
		if carried != null and carried.is_mission_item:
			return true
		for item in player.inventory:
			if item != null and is_instance_valid(item) and item.is_mission_item:
				return true
	return false


func _player_has_mission_item() -> bool:
	if player == null or not is_instance_valid(player):
		return false
	var carried := player.carried_item as FMCarryItem
	if carried != null and carried.is_mission_item:
		return true
	for item in player.inventory:
		if item != null and is_instance_valid(item) and item.is_mission_item:
			return true
	return false


func on_extraction_started() -> void:
	_extraction_busy = true
	if hud != null:
		hud.set_status("EXTRACCIÓN INICIADA · PERMANECÉ EN LA ZONA")
	notify("EXTRACCIÓN INICIADA")


func on_extraction_progress(stage: String, seconds_left: float) -> void:
	if state != State.PLAYING:
		return
	_extraction_busy = true
	var labels := {
		"activando": "VALIDANDO",
		"apertura": "ABRIENDO SALIDA",
		"espera": "ESPERANDO",
		"cierre": "CERRANDO",
		"viaje": "VIAJE",
		"llegada": "CONFIRMANDO",
	}
	if hud != null:
		hud.set_status("EXTRACCIÓN · %s · %.1f s" % [
			labels.get(stage, stage.to_upper()), maxf(0.0, seconds_left),
		])


func on_extraction_cancelled() -> void:
	_extraction_busy = false
	notify("EXTRACCIÓN CANCELADA · VOLVÉ A LA ZONA")


func on_extraction_completed(delivered_loot: int) -> void:
	if state != State.PLAYING:
		return
	state = State.WON
	_extraction_busy = false
	_stop_horror_audio()
	if hud != null:
		hud.show_end("EXTRACCIÓN COMPLETADA", "Núcleo asegurado · %d objeto(s) válido(s)" % delivered_loot)
	if DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func _stop_horror_audio() -> void:
	if horror_audio != null and is_instance_valid(horror_audio):
		horror_audio.stop_all()


# ---------------------------------------------------------------------------
# Consultas usadas por la prueba de humo
# ---------------------------------------------------------------------------

func get_sector_mesh_count(id: String) -> int:
	var root := sector_roots.get(id) as Node3D
	if root == null:
		return 0
	return root.find_children("*", "MeshInstance3D", true, false).size()


func get_alternate_routes_mesh_count() -> int:
	if alt_routes_root == null or not is_instance_valid(alt_routes_root):
		return 0
	var count := 0
	for node in alt_routes_root.find_children("*", "MeshInstance3D", true, false):
		if String(node.name).begins_with("SM_L1_Alt_"):
			count += 1
	return count


func get_alternate_routes_collider_count() -> int:
	return alt_routes_collider_count


func get_light_count() -> int:
	return find_children("*", "Light3D", true, false).size()


## Identidad/estado de una sala blockout. Devuelve {} para los sectores que
## no forman parte del lote blockout.
func get_sector_context(id: String) -> Dictionary:
	return BLOCKOUT_CONTEXT.get(id, {})


func get_blockout_ready_count() -> int:
	var count := 0
	for id in BLOCKOUT_IDS:
		if sector_roots.get(id) != null and int(collider_counts.get(id, 0)) > 0:
			count += 1
	return count


func get_hidden_duplicate_meshes() -> Array[String]:
	return hidden_duplicate_meshes.duplicate()


func get_blockout_blockers() -> Array:
	return BLOCKOUT_BLOCKERS.duplicate(true)


func get_blockout_blocker(id: String) -> Dictionary:
	for blocker in BLOCKOUT_BLOCKERS:
		if String(blocker.get("id", "")) == id:
			return blocker
	return {}


func get_blockout_resolutions() -> Array:
	return BLOCKOUT_RESOLUTIONS.duplicate(true)


func get_blockout_resolution(id: String) -> Dictionary:
	for resolution in BLOCKOUT_RESOLUTIONS:
		if String(resolution.get("id", "")) == id:
			return resolution
	return {}


func get_nav_door_link_count() -> int:
	return nav_door_links.size()


func get_nav_door_link_names() -> Array[String]:
	var names: Array[String] = []
	for link in nav_door_links:
		if link != null and is_instance_valid(link):
			names.append(String(link.name))
	return names


func get_stair_safe_zone_ids() -> Array[String]:
	var ids: Array[String] = []
	for id in STAIR_SAFE_ZONES:
		ids.append(String(id))
	return ids


func get_nav_main_polygon_count() -> int:
	return nav_main_polygons


func get_nav_service_polygon_count() -> int:
	return nav_service_polygons


func get_nav_bake_ms() -> int:
	return nav_bake_ms


func get_nav_service_bake_ms() -> int:
	return nav_service_bake_ms


func is_nav_hatch_link_enabled() -> bool:
	return nav_hatch_link != null and is_instance_valid(nav_hatch_link) and nav_hatch_link.enabled


func get_gate(id: String) -> FMLevel1Gate:
	for gate in level_gates:
		if gate != null and is_instance_valid(gate) and gate.gate_id == id:
			return gate
	return null


func get_gate_ids() -> Array[String]:
	var ids: Array[String] = []
	for gate in level_gates:
		if gate != null and is_instance_valid(gate):
			ids.append(gate.gate_id)
	return ids


func get_door_noise_count() -> int:
	return door_noise_count


func get_extraction_marker_position() -> Vector3:
	return extraction_marker.global_position if extraction_marker != null else Vector3.ZERO


func get_extraction_marker_light_count() -> int:
	if extraction_marker == null:
		return 0
	return extraction_marker.find_children("*", "Light3D", true, false).size()
