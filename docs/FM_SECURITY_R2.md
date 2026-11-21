# FRECUENCIA MUERTA — Seguridad 03, R2.0: checkpoint de acceso

**Fecha:** 2026-11-08
**Escena:** `NEXUS_L1_V06_ARCH`
**Sala:** Seguridad 03 — 34 × 26 m, altura 4,8 m
**Colección:** `L1_SECURITY_R2`

---

## 1. Alcance

R2.0 construye el **checkpoint de acceso sur**, el primer bloque de identidad de
Seguridad 03. No incluye todavía el centro de operaciones, la sala de briefing,
los lockers ni el hatch este. No hay objetos narrativos ni lógica de juego.

La sala se construye ya en estado de abandono: el caos es parte de la identidad,
no una capa posterior.

## 2. Elementos construidos

- Panel trasero de 2,8 × 0,10 × 2,2 m con cartel **SEGURIDAD** texturizado
  (`rec_seguridad.png`, 1024 × 256, texto blanco sobre verde).
- Mostrador de pie dañado:
  - Tapa de 2,6 × 0,8 × 0,08 m.
  - Frontal verde y lateral izquierdo.
  - Monitor muerto con pantalla negra y teclado.
- Lector de tarjetas sobre pedestal.
- Barrera de acceso con dos postes, bases y cinta roja.
- Panel de techo caído, charco de agua, seis escombros y cable/restos.
- Aplique y luz de emergencia roja en el checkpoint.

## 3. Iluminación

La iluminación sigue el estándar del piloto Z10:

- Las 7 luces generales de techo están **apagadas**.
- Los 7 paneles de techo usan `M_FM_Steel_Dark`: están **muertos**.
- Emergencias rojas escasas:
  - Checkpoint sur: `LIGHT_SEC02_Emergency`, 2,5 W.
  - Puerta norte: `LIGHT_SEC03_Emergency_N`, 2,5 W.
  - Lado este: `LIGHT_SEC03_Emergency_E`, 2,0 W.
- La recepción sigue siendo la única zona con iluminación general abundante.
- La linterna es la fuente principal de exploración.

## 4. QA

- **SEC_R2_SIGN_QA: PASS, 0 errores / 12 warnings**.
- `L1_SECURITY_R2`: **26 objetos**.
- Escena: **1.701 objetos**.
- Warnings aceptados: UV solapadas y caras internas de piezas con materiales
  sólidos; no hay flotantes ni normales invertidas.
- Archivo guardado.

## 5. Renders

- `docs/fm_security_r2_checkpoint_text.png` — EEVEE 64 samples, 1280 × 720,
  cámara (-89, 9,0, 1,7) → (-89, 13,3, 1,4), lente 24 mm, luces temporales de
  revisión.
- `docs/fm_security_r2_wide_wb.png` — Workbench, vista amplia.
- `docs/fm_security_r2_checkpoint_wb.png` — Workbench, checkpoint.

El render EEVEE muestra el cartel **SEGURIDAD** legible, el panel trasero con
remaches y manchas, el mostrador, el monitor negro, el teclado, la cinta roja y
los escombros. El checkpoint se lee con claridad y el caos es visible.

## 6. Limitaciones

- La sala sigue vacía más allá del checkpoint.
- La cinta de barrera se ve intacta; el poste izquierdo queda fuera del encuadre.
- Los objetos narrativos (cuerpos, sangre, documentos, objetos personales) y las
  texturas finales quedan para la última capa.
- El shell tiene UVs pendientes para el pase de texturas; no bloquea la
  identidad geométrica de R2.

## 7. Próximo paso: R2.1

1. Centro de operaciones: puestos, monitores muertos, sillas volcadas, rack,
   radio y cables.
2. Briefing: mesa y sillas volcadas, tablero roto.
3. Lockers abollados/abiertos.
4. Hatch este dañado.
5. QA, render y después R3 (señalización, emergencias, desgaste).
