# FRECUENCIA MUERTA — Seguridad 03, fase R1

**Fecha:** 2026-11-08
**Archivo:** `nexus/nivel_01/FM_LEVEL1_V06_ARCH.blend`
**Escena:** `NEXUS_L1_V06_ARCH`
**Sala:** Seguridad 03
**Estado:** R1 — estructura, techo e iluminación. Sin mobiliario ni señalización.

## 1. Sala

- Superficie: x −105..−71, y 10..36; **34 × 26 m**.
- Altura libre: **4,8 m**.
- Suelo existente en z −0,2..0.
- 6 columnas de 0,45 × 0,45 m: x −98 / −88 / −78, y 16 / 26.
- Puerta sur x −92..−86, z 0..3,2; conecta con el SecurityConnector y recepción.
- Puerta norte x −96..−92, z 0..2,6; conecta con AccessConnector.
- Hueco/ventana de servicio en el muro este, y 10,2..11,6, z 0..2,2.

## 2. Corrección del techo

El objeto `SM_L1_Zone03_Security_Ceiling` existía como malla de **8 vértices y 0 caras**, en el origen, dentro de la colección oculta `L1_ARCH_CEILINGS`.

- Se reconstruyó como caja real **34,0 × 26,0 × 0,2 m**.
- Posición: **(−88, 23, 4,8)**.
- Material: `M_FM_Concrete_Wall`.
- Se enlazó a `L1_SECURITY_R1`, visible.
- Ya no depende de `L1_ARCH_CEILINGS`.

## 3. Iluminación

- 7 luminarias de techo en `L1_SECURITY_R1`:
  - `KIT_SEC01_CeilingLightHousing_*` (carcasa).
  - `DET_SEC01_CeilingLightPanel_*` (panel emisivo).
  - `LIGHT_SEC01_Ceiling_*` (luz puntual fría, 2,6 W, rango 14).
- Distribución: tres crujías y eje central.

## 4. QA y render

- **SEC_R1_QA: PASS, 0 errores / 23 warnings aceptados.**
- Escena: **1.673 objetos**; `dirty=False`.
- Render Workbench 1280×720: `docs/fm_security_r1_wide_wb.png`.
- Cámara: (−101, 12, 2,6) → (−88, 24, 2,0), lente 20 mm.
- La imagen muestra el hall vacío, techo con paneles, 6 columnas, suelo marrón/rojo y el hueco sur con el conector iluminado.
- No hay mobiliario, props ni señalización: es R1 estructural.

## 5. Identidad pendiente (R2)

- Checkpoint sur: mostrador de guardia, barrera/torniquete, lector, cámara, monitor.
- Centro de operaciones: monitor wall, 2–3 puestos, sillas, consola de radio, rack/UPS.
- Briefing: mesa, sillas, tablero de planos/incidencias, reloj.
- Lockers/equipo: taquillas, extintor, botiquín, panel eléctrico, alarma.
- Ventana/hatch este: mostrador de registro/entrega y señalización.
- Iluminación de trabajo y emergencias; señalización SEGURIDAD / CONTROL DE ACCESO / SOLO PERSONAL AUTORIZADO.

Después: R3 señalización/emergencias/desgaste, QA+GLB WebP+Godot. Texturas y objetos narrativos al final.

Sin commit.
