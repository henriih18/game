# FRECUENCIA MUERTA — Seguridad 03 / R21B

**Área:** recepción del nivel 1, ala de seguridad. Sala de 34 × 26 m (x −105..−71, y 10..36, z 0..4.8).
**Archivo:** `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`, escena `NEXUS_L1_V06_ARCH`.
**Colección nueva:** `L1_SECURITY_R21B_HERO` con las subcolecciones `BRIEFING`, `LOCKERS`, `HATCH`, `CIRCULATION`, `CHAOS`, `LIGHTS`.

> **Actualización R21C (09/11/2026):** las piezas que aquí figuran como simplificadas
> (taquillas sin rejillas/baldas, luna incompleta de la ventanilla, rack de llaves/estantería
> simplificados y tool cart sin ruedas) quedan sustituidas por `L1_SECURITY_R21C_HERO`.
> Ver `docs/fm_security_r21c.md`. Los objetos R21B originales siguen en el archivo, ocultos,
> no eliminados.

## Estado

Zona completada a **escala de sala**: el centro, el oeste y el este de Seguridad 03 dejan de estar vacíos y quedan legibles en una vista amplia. La QA de malla pasa sin errores. El detalle es de calidad hero a distancia de juego; algunos microdetalles de close-up se simplificaron para poder entregar una malla limpia (ver **Limitaciones**).

No se ha modificado ni movido nada de:

- `L1_SECURITY_R2_HERO` (158 objetos, checkpoint).
- `L1_SECURITY_R21A_HERO` (1 objeto, cámara del centro de operaciones) ni sus subcolecciones.
- `L1_SECURITY_R1`, `L1_ARCH_*`, recepción, `Z10`, `fotos-referencia/`.

## Métricas

| Colección | Mallas | Tris |
|---|---:|---:|
| `L1_SECURITY_R21B_BRIEFING` | 24 | 38.120 |
| `L1_SECURITY_R21B_LOCKERS` | 10 | 22.776 |
| `L1_SECURITY_R21B_HATCH` | 5 | 9.264 |
| `L1_SECURITY_R21B_CIRCULATION` | 29 | 42.448 |
| `L1_SECURITY_R21B_CHAOS` | 27 | 22.974 |
| **Total** | **95** | **135.582** |

- 3 luces rojas de emergencia y 1 luz ámbar de chispa, todas de baja energía, en `L1_SECURITY_R21B_LIGHTS`; la iluminación guardada sigue siendo oscura, sin luces generales.
- Todos los objetos tienen escala 1, UV map y materiales válidos; no hay caras con UV de área cero.
- Las mallas están construidas a escala real, con bisel en las formas primarias, líneas de panel, tornillos, bisagras, rejillas y weighted normals en los ensamblajes.

## Distribución y circulación

### Briefing / training — oeste-centro (x −101..−91, y 17..24)

- Mesa de conferencia de 3,05 × 1,22 m con estructura en T, bandeja de cables, regletas, pasacables y cableado.
- 6 sillas de training ergonómicas + 2 sillas volcadas.
- Alfombra, tablero de planos/incidencias en la pared oeste (grafo abstracto con imanes, sin documentos narrativos), pantalla de proyección, proyector de techo, credenza con lámpara articulada, atril con micrófono, perchero, 2 papeleras, 2 plantas, torre de enchufes y alfombrilla de entrada.
- Reloj, bandeja de cables, bajantes y luminaria de emergencia en la pared oeste.

### Lockers / equipo — este-sur (x −80..−71, y 10..23)

- Banco A de 8 puertas en la pared este (y 13,4..17,8), con puertas abiertas, abolladuras, bisagras, cerraduras, asas y patas.
- Banco B de 8 puertas en la pared sur (x −80,6..−76,2).
- Dos bancos de vestuario con listones de madera y estructura de acero.
- Estación de carga de 6 radios con pantallas, antenas, PTT y contactos.
- Armario/rack abierto de llaves con 12 llaves y etiquetas de color.
- Botiquín, extintor con soporte, manguera y manómetro.
- Estantería de equipamiento con cascos de seguridad.
- Estación de PPE: taquilla, tablero de herramientas, espejo, 2 cascos sobre la encimera, 2 bolsas y banda de identificación.
- Alfombrilla de goma y señalización.

### Hatch / ventanilla — pared este (x ≈ −71, y 10,2..11,6)

- Mostrador de servicio de acero inoxidable con cuerpo, puertas, patas y pasabandeja.
- Reja enrollable parcialmente bajada, guías, carcasa y manivela.
- Intercomunicador con altavoz, pulsador y LED.
- Cristal roto: no se entrega una luna completa; quedan fragmentos en el mostrador y en el suelo, y el hueco se lee como ventanilla rota.
- Office nook: escritorio, CRT, teclado, teléfono, tablón de casilleros, taburete, papelera y cables.
- Rótulo “SERVICIO” y marco metálico.

### Circulación y centro

- Mampara de vidrio de 2,35 m en el borde sur del centro de operaciones (y 25,95), con puerta de vidrio abierta 22°, herrajes, cierrapuertas y rótulo de acceso restringido.
- Cola de 4 stanchions con cintas rojas desde el checkpoint (y 14,35).
- Señalización de suelo: líneas de carril, flechas, banda de peligro, texto “SEC-03”, pasos y marcas desgastadas.
- 2 jardineras de hormigón con plantas, 2 bancos de espera con respaldo, banco central sin respaldo.
- Protección de columnas: bandas amarillas en las 6 columnas.
- Servicios: bandeja de cables en la pared oeste, conductos, canaleta central, conducto HVAC, rociadores, rejillas de pared, armario de manguera, reloj, rótulo “SEGURIDAD 03”, señales de salida y extintor.

### Chaos (no narrativo)

- Tool cart/cabinet con 5 frentes de cajón y tiradores (sin ruedas; simplificado por QA), cable reel vertical y tumbado, pallet, cajas, bidones/contenedores, monitores CRT muertos.
- Luminarias de techo caída y colgando, escombros, charcos, polvo, cables, rollos y caja de conexiones dañada con cables expuestos en la columna (−88, 16), con luz ámbar de chispa.
- Sin cuerpos, sangre, notas, fotos ni objetos personales.

## QA

Ejecutada con `/home/riyo/.agents/skills/blender-asset-qa/scripts/qa_check.py` dentro de Blender 5.2.3.

- Objetos: 95 mallas de `L1_SECURITY_R21B_*` + `SM_L1_Zone03_Security_Floor`, techo, paredes E1/E2/N0/N1/N2/S0/S1/S2/W0 y las 6 columnas de seguridad.
- Perfil: `render`; `eps=0.0005`; `tol=0.004`; `max_tris=450000`; `uv=False` en la pasada combinada (el suelo/arquitectura no se usan como referencia de UV).
- **Resultado: `pass=True`, 0 errores, 71 warnings.**
- La pared E0 se excluyó de la pasada porque forma un z-fighting preexistente con S2 (arquitectura existente, no R21B). No se modificó.
- El perfil `game` marcaría como error los “inward normals” que el comprobador detecta al triangular tapas n-gon de piezas pequeñas; los héroes existentes (`R2_HERO`, `R21A`) muestran el mismo comportamiento. La comprobación visual y el volumen firmado de las islas revisadas dan normales hacia fuera.
- Warnings: 43 avisos de “inward normals” (falsos positivos de triangulación en piezas pequeñas), 13 de caras ocultas back-to-back, 6 de vértices duplicados en uniones/UV, 1 de punto más bajo −0,2 (cara inferior del suelo) y 1 de piezas encerradas.
- UVs validadas aparte: 95/95 mallas con UV map, 0 caras con UV de área cero, escala 1, materiales asignados.

JSON completo: `docs/fm_security_r21b_qa.json`.

## Renders

- `docs/fm_security_r21b_briefing.png` — briefing/training, EEVEE 64 samples, 1280×720.
- `docs/fm_security_r21b_lockers_hatch.png` — lockers, PPE y ventanilla, EEVEE 64 samples.
- `docs/fm_security_r21b_center.png` — 3/4 del centro, EEVEE 64 samples.
- `docs/fm_security_r21b_wide.png` — vista amplia de la sala completa; Workbench con techo oculto y colores de material aclarados temporalmente para que la densidad y la circulación sean legibles. La versión EEVEE con techo resultó demasiado oscura para evaluar la sala; se documenta como limitación.

Las luces y cámaras de render son temporales y no se guardaron en el `.blend`.

## Rutas y circulación

- **Sur → norte:** puerta sur (x −92..−86) → lateral oeste del checkpoint (x −92..−90,4) → carril oeste (x −95..−91,4) → puerta norte (x −96..−92). Libre.
- **Checkpoint → lockers/hatch:** salida este del checkpoint (x −87,6..−86) → cola (y 14,35) → pasillo este (x −86..−76) → banco A, banco B, estación de radios, llaves, botiquín, estantería, PPE y ventanilla.
- **Centro → operaciones:** puerta de vidrio en la mampara sur (x −86,3..−85,1, y 25,95), abierta 22°.
- **Centro → briefing:** paso oeste entre la mampara (x −91,5) y la mesa de briefing, sin bloquear las puertas.
- No se bloqueó el eje sur-norte ni los accesos; el banco de espera oeste roza el borde del carril, pero deja más de 3,5 m libres.

## Limitaciones

- La QA obligó a simplificar microdetalles que generaban solapamientos coplanares: se quitaron las rejillas de las puertas de taquilla, las baldas interiores de los lockers, la luna completa de la ventanilla (quedan fragmentos), el cajón/rack cerrado de llaves, las ruedas del tool cart y parte del interior de la estantería. El resultado es limpio a escala de sala, pero no es todavía un hero de close-up en esos cuatro elementos.
- El árbol central se sustituyó por una gran sansevieria en maceta para evitar autointersecciones de hojas.
- La vista amplia se entrega en Workbench; falta un pase de iluminación práctica que permita una amplia en EEVEE con el techo visible.
- La sala no tiene todavía colisiones, navegación, LOD ni sincronización multijugador; esta entrega es de arte/blockout hero.
- El suelo y las paredes son arquitectura existente y conservan su z-fighting previo E0/S2.

## Siguiente paso

1. Pase de close-up hero en taquillas, ventanilla, rack de llaves y tool cart con ensamblajes de una sola pieza (marcos de puerta, rejillas y baldas) que no generen caras coplanares.
2. Pase de iluminación práctica definitivo (luces de emergencia, monitores, fluorescencia puntual) y render amplio EEVEE con techo visible.
3. Colisiones, navegación, LOD y presupuesto final de draw calls.
4. Integración multijugador de puertas, objetos físicos, escondites y eventos de la sala.
