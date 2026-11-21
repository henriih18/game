# FRECUENCIA MUERTA — Auditoría e inventario del Nivel 1 (Fase 3A.2)

**Fecha:** 2026-11-04 (COT)  
**Ámbito:** `scenes/fm/level1.tscn` y todos sus espacios interiores.  
**Objetivo:** completar el nivel 1 con un estándar visual y técnico consistente, oscuro y funcional, reutilizando la base existente.

## 1. Método

1. Lectura de `AGENTS.md`, `docs/WORKLOG.md`, `docs/NEXUS_L1_PHASE3A1_ART.md`, `docs/NEXUS_ARCHITECTURAL_AUDIT.md` y `docs/NEXUS_L1_CIRCULATION_AUDIT.md`.
2. Extracción de bounds reales del GLB jugable en Blender y raycasts de techo/suelo/paredes en Godot.
3. Recorrido fotográfico por todas las zonas con linterna encendida y apagada.
4. Intervención en Blender para geometría de arquitectura, luminarias y mobiliario; integración en Godot.
5. Pruebas funcionales: smoke, recorrido completo, colisiones nuevas y rendimiento.
6. Revisión visual iterativa y corrección de defectos detectados.

## 2. Zonas identificadas

El Nivel 1 está compuesto por las siguientes zonas. Las medidas son interiores aproximadas, obtenidas de bounds del GLB y raycasts; no sustituyen un levantamiento métrico definitivo.

| Zona | Superficie aprox. | Techo | Estado | Cierre |
|---|---:|---:|---|---|
| Recepción NEXUS | 16 × 10 m (160 m²) | 5,7 m | APROBADA | Estándar visual de referencia |
| Corredor principal | 44 × 3,4 m (149,6 m²) | 3,93 m | APROBADA | Estándar de circulación |
| Seguridad | 10 × 8 m (80 m²) | 3,93 m | APROBADA | Monitor wall + rack + desk |
| Control de acceso | 8 × 8 m (64 m²) | 3,93 m | APROBADA | Consola + rack + tornos |
| Vestuarios | 10 × 8 m (80 m²) | 3,73 m | APROBADA | Taquillas + bancos + espejos |
| Almacén | 12 × 8 m (96 m²) | 3,93 m | APROBADA | Estanterías + carga + polipasto |
| Mantenimiento | 14 × 8 m (112 m²) | 4,73 m | APROBADA | Generador + caldera + banco |
| Oficina | 3,9 × 5,8 m (22,6 m²) | 2,85 m | APROBADA | Escritorio + estantería + equipo |
| Aseo | ~4 × 3 m (12 m²) | 2,85 m | APROBADA | Lavabo + espejo + inodoro |
| Conector de servicio | Transición | Variable | APROBADA | Puerta de servicio + señalización |
| Ascensor / extracción | Cabina + recepción | Variable | APROBADA | Salida visual y trigger de recepción |
| Oficina/aseo (volumen administrativo) | Incluido en recepción | 2,85 m | APROBADA | Particiones interiores |

**Total:** 10 zonas funcionales + 2 transiciones. Ninguna zona quedó sin analizar.

## 3. Inventario por zona

### 3.1. Recepción NEXUS

- **Geometría:** mostrador de Blender con fascia verde, paneles hundidos, tapa de madera, zócalo, tira LED y mampara de cristal con marco de acero (`ART3A1_kit`). Directorio mural, panel corporativo NEXUS, ascensor SALIDA, zona de extracción, sillas, mesas, archivador, plantas.
- **Materiales:** 40 overrides PBR; madera, acero galvanizado, pintura verde, hormigón, cristal, suelo húmedo, tela de sillas, papel y sangre.
- **Iluminación:** clave fría cenital, contraluz, relleno frío, acento ámbar de mostrador, luces de emergencia atenuadas y dos reflection probes. La recepción conserva iluminación moderada.
- **Colisiones:** base del GLB + colisiones nuevas para archivador, estantería de oficina y mobiliario grande.
- **Físicas:** props físicos existentes (latas, portapapeles, cartones) sin cambios.
- **Problemas corregidos:** panel NEXUS claro, mostrador plástico, cristal sin marco, ausencia de directorio, planta low-poly, falta de detalle en pared oeste.
- **Pendiente:** algunas sillas y mesas conservan geometría de biblioteca; aceptables a distancia, simples en primer plano.

### 3.2. Corredor principal

- **Geometría:** vigas de techo, bandeja de cables, tuberías, conductos, columnas, marcos de puerta, rejillas de pared, módulos de pared, dinteles metálicos y señalización.
- **Materiales:** acero, pintura verde, hormigón, rejillas, goma, suelo húmedo, señales emisivas.
- **Iluminación:** 4 focos fríos atenuados, relleno local, tiras cian/ámbar, luces de emergencia atenuadas y niebla volumétrica. La linterna sigue siendo necesaria para leer detalles.
- **Colisiones:** paredes, puertas, columnas, extintores, carros y escombros del GLB; las rejillas y costillas nuevas son decorativas y no bloquean.
- **Problemas corregidos:** paneles blancos flotantes sobre puertas, volumen claro del techo, módulos de pared demasiado grandes, falta de ritmo vertical, dinteles claros.
- **Pendiente:** algunos tramos largos de pared siguen siendo repetitivos; no hay LOD/occlusion.

### 3.3. Seguridad

- **Geometría:** mesa de monitores, sillas, monitor wall, rack técnico, cámara, caja de servicio, taburete, extintor, reloj.
- **Materiales:** PBR de acero, pintura, pantallas y cuero sintético.
- **Iluminación:** lámpara colgante de jaula, vigas, conducto, luces de emergencia atenuadas.
- **Colisiones:** mobiliario original + rack nuevo con collider.
- **Problemas corregidos:** sala vacía, techo plano, falta de equipo técnico.
- **Pendiente:** la pared trasera conserva grandes superficies oscuras; el monitor wall podría tener contenido más variado.

### 3.4. Control de acceso

- **Geometría:** consola de control con dos monitores, teclado, bandeja de cables, rack técnico, taburete, cámara, marco de acceso y señalización RAYOS X.
- **Materiales:** PBR, pantallas cian con barras de interfaz, acero y pintura.
- **Iluminación:** lámpara colgante, vigas, conducto, luces de emergencia y luz de pantallas.
- **Colisiones:** consola y rack con colliders nuevos.
- **Problemas corregidos:** sala casi vacía, ausencia de puesto de control, monitores planos.
- **Pendiente:** la consola es una aproximación de bloqueo; no tiene animaciones ni pantallas interactivas.

### 3.5. Vestuarios

- **Geometría:** taquillas, bancos con listones de madera, espejos con marco, taburete, caja, extintor, botiquín, señal DUCHA.
- **Materiales:** pintura verde, madera, acero, espejo oscuro reflectante, tela.
- **Iluminación:** lámpara colgante, vigas, luces de emergencia; se corrigió la lámpara sobreexpuesta.
- **Colisiones:** taquillas y bancos originales; caja y taburete nuevos.
- **Problemas corregidos:** espejos blancos planos, lámpara quemada, techo plano, falta de listones.
- **Pendiente:** taquillas de biblioteca con puertas simples; los listones son un añadido fino.

### 3.6. Almacén

- **Geometría:** estanterías, cajas, palés, barriles, polipasto, carro, conducto, lámpara colgante, rejillas.
- **Materiales:** madera, cartón, plástico, acero oxidado, pintura.
- **Iluminación:** lámpara colgante de jaula, conducto, luces de emergencia atenuadas; se retiraron las tiras emisivas que parecían cajas flotantes.
- **Colisiones:** estanterías y cajas originales + barriles/cajas nuevas.
- **Problemas corregidos:** luces flotantes, techo plano, falta de carga y polipasto visible.
- **Pendiente:** cajas de cartón de biblioteca con geometría simple.

### 3.7. Mantenimiento

- **Geometría:** generador de alta tensión, caldera, tuberías, banco de trabajo, pegboard con herramientas, caja de herramientas, carro, cajas, barriles, caja eléctrica, botiquín.
- **Materiales:** acero, pintura roja, cobre, madera, goma, óxido.
- **Iluminación:** dos lámparas colgantes, vigas, conducto, luces de emergencia, vapor volumétrico.
- **Colisiones:** banco, caldera y generador originales; cajas/barriles y caja eléctrica nuevos.
- **Problemas corregidos:** panel negro plano, falta de maquinaria legible, techo plano, cajas flotantes.
- **Pendiente:** la cara del generador sigue siendo un bloque grande; se mejoró con materiales, no con geometría interna.

### 3.8. Oficina

- **Geometría:** escritorio, silla, monitor, microscopio, estantería, archivador, reloj, papeles, sangre.
- **Materiales:** PBR de metal, madera, pantalla, papel.
- **Iluminación:** luz de oficina existente, lámpara de techo, luces de emergencia.
- **Colisiones:** escritorio y estantería; estantería nueva con collider.
- **Problemas corregidos:** estantería vacía, falta de equipo, monitor plano.
- **Pendiente:** estantería de planks simple; el reloj es un asset de biblioteca.

### 3.9. Aseo

- **Geometría:** lavabo, espejo con marco, estante, jabón, toalla, inodoro, secador, botiquín, partición.
- **Materiales:** PBR de cerámica, metal, espejo oscuro, papel.
- **Iluminación:** panel de luz existente + luces de emergencia.
- **Colisiones:** particiones y sanitarios originales.
- **Problemas corregidos:** espejo sin marco, estante inexistente, pared vacía.
- **Pendiente:** no hay azulejo procedural; la pared es lisa.

### 3.10. Conector de servicio, ascensor y extracción

- **Geometría:** puerta de servicio, rejillas naranjas, señalización PASO ESTRECHO / SERVICIO // MUELLE, ascensor SALIDA, cabina, puertas, trigger de extracción en recepción.
- **Materiales:** pintura naranja/verde, acero, cristal, señalización emisiva.
- **Iluminación:** luces de emergencia, tiras, luz de cabina.
- **Colisiones:** puertas, muros, cabina y trigger de recepción.
- **Problemas corregidos:** legibilidad de la puerta de servicio y señalización.
- **Pendiente:** la extracción sigue siendo una secuencia visual/trigger; no se tocó su lógica.

## 4. Inventario global

- **Mallas del nivel:** GLB jugable original de 42,5 MB; 1.940 objetos, 530.249 triángulos de origen.
- **Kit 3A.1:** mostrador/cristal de recepción, 2 conductos de 10 m, módulos de pared; 8 mallas fusionadas.
- **Kit 3A.2:** 1.327 objetos de origen fusionados en 10 mallas; vigas, costillas, zócalos, cajas de servicio, conductos, lámparas de jaula, directorio, consola, racks, listones, rejillas y dinteles.
- **Props 3A.2:** 15 GLB con texturas a 1K, 34 instancias colocadas.
- **Materiales:** 40 overrides PBR en runtime; el GLB conserva 111 materiales base.
- **Luces:** 23 `ART_` (17 originales + 6 rellenos fríos de sala), 30 de emergencia y 3 de linterna; solo algunas luces clave proyectan sombra.
- **Colisiones:** 515 del GLB + 17 nuevas (14 props + 3 estructuras) = 532.
- **Físicas:** 21 props físicos originales; los nuevos muebles son estáticos con collider.
- **Partículas/atmósfera:** polvo, vapor, niebla volumétrica, decals de sangre/suciedad/humedad.

## 5. Defectos y estado

### Resueltos

| Defecto | Prioridad | Solución |
|---|---|---|
| Volumen claro sobre el acceso del corredor | Alta | Parapetos ocultos + dinteles/bulkheads + conducto elevado y oscurecido |
| Paneles blancos flotantes sobre puertas | Alta | Override de linteles/`_ABOVE_` a acero oscuro |
| Módulos de pared demasiado grandes/planos | Alta | Kit 3A.2 con costillas, paneles y escala reducida |
| Mostrador y cristal plásticos | Alta | Kit Blender 3A.1 con marco, paneles y materiales PBR |
| Panel NEXUS claro | Alta | Override `NEXUS_V05_MAT_Sign_Battery` |
| Lámpara de vestuarios sobreexpuesta | Alta | Clamp de emisión de `industrial_wall_lamp` |
| Tiras de techo que parecían cajas flotantes | Media | Ocultas y sustituidas por lámparas de jaula |
| Plantas low-poly (esferas verdes) | Media | Ocultas y sustituidas por `potted_plant` |
| Control/seguridad vacíos | Media | Consola, racks, monitores, cámara y radio |
| Espejos blancos planos | Media | Material oscuro reflectante |
| Caída de FPS por texturas de props | Alta | Reducción a 1K; 36 → 108 FPS (medición previa a los rellenos fríos; 103–107 final) |
| Falta de colisiones en mobiliario nuevo | Alta | 14 colliders de props + 3 estructuras |

### Pendientes conocidos

| Defecto | Prioridad | Estado |
|---|---|---|
| Props de biblioteca con geometría simple (sillas, cajas, taquillas) | Media | Aceptado para vertical slice; sustitución futura |
| Sin LOD ni occlusion culling reales | Media | Documentado; el kit está fusionado por material |
| Pantallas sin contenido/interacción | Baja | Placeholder visual |
| Tramos de pared repetitivos | Baja | Costillas y cajas mitigan; falta variación única |
| Sin prueba en GTX 1650 Ti ni build final | Media | Pendiente de la fase de optimización |
| Sin menús/perfiles gráficos | Baja | Fuera de alcance por instrucción |
| Viewmodel de linterna y HUD de fases previas | Baja | Conservados |
| Sin red de 8 jugadores | Alta (futuro) | Fuera de alcance de esta fase |

## 6. Pruebas

| Prueba | Resultado |
|---|---|
| Carga de escena | `ART3A1_KIT loaded`, `ART3A2_DRESSING loaded`, `ART3A2_PROPS 34`, `ART_PASS ready materials=40 details=10`, `LEVEL1_READY loot=5 colliders=515` |
| Smoke | **PASS** — `TEST_LIGHTS general=0 art=23 emergency=30 flashlight=3`, `FM_LEVEL1_TEST: PASS` |
| Recorrido | **PASS** — `WALK_RESULT reached=33/33` |
| Colisiones nuevas | **PASS 5/5**, 14 `PropCollider` |
| Capturas | 34/34, con y sin linterna |
| Rendimiento | **103–107 FPS / 1.255 draws / 886.246 primitivas / 9.089 objetos** a 1280×720 en el equipo de desarrollo |

## 7. Limitaciones de la auditoría

- Las medidas son aproximadas y provienen de bounds/raycasts, no de un levantamiento topográfico.
- La evaluación visual se realizó en el equipo de desarrollo; no sustituye una prueba en GTX 1650 Ti.
- El rendimiento incluye la escena completa del Nivel 1, pero no una partida de 8 jugadores ni criaturas adicionales.
- No se modificaron físicas, puertas, cajones, taquillas, alarmas, loot, IA, red, inventario ni menús.
- No se modificó el `.blend` original ni el GLB jugable; el trabajo nuevo vive en kits y overrides.
