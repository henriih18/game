\\\\# FRECUENCIA MUERTA

\\\\## Videojuego multijugador cooperativo de terror, exploración y

supervivencia.

Este documento establece las instrucciones permanentes, la identidad,

las reglas técnicas, la dirección artística y los objetivos de

desarrollo de FRECUENCIA MUERTA.

Debes consultar estas instrucciones antes de realizar cambios

importantes en el proyecto.

El proyecto ya tiene una parte desarrollada.

**\*\*\\\*\\\*\\\\\\\*\\\\\\\*NO quiero reconstruirlo desde cero.\\\\\\\*\\\\\\\*\\\*\\\*\*\***

Quiero aprovechar al máximo el trabajo existente, conservar sus

funcionalidades y transformarlo progresivamente en FRECUENCIA MUERTA.

Las instrucciones de este documento deben mantenerse vigentes durante

todo el desarrollo, pero el estado de las fases debe actualizarse

conforme avance el proyecto.

\\---

\\\\# 1. IDENTIDAD DEL VIDEOJUEGO

Nombre: FRECUENCIA MUERTA.

Lema:

"No todas las voces que escuchas pertenecen a tus compañeros".

Género:

\\\\- Terror psicológico.

\\\\- Supervivencia cooperativa.

\\\\- Exploración.

\\\\- Extracción.

\\\\- Sigilo.

\\\\- Cooperación multijugador.

\\\\- Terror ambiental.

\\\\- Suspense.

La experiencia debe generar miedo, tensión, situaciones inesperadas,

momentos divertidos entre amigos y una gran rejugabilidad.

\\\\## FILOSOFÍA PRINCIPAL

Los jugadores NO son soldados.

NO son mercenarios.

NO son cazadores de monstruos.

Son trabajadores de recuperación contratados para explorar instalaciones

abandonadas y recuperar objetos de valor.

No tienen armas.

No pueden matar a las criaturas.

No pueden enfrentarse directamente a las amenazas.

Su supervivencia depende de:

\\\\- Inteligencia.

\\\\- Observación.

\\\\- Sigilo.

\\\\- Cooperación.

\\\\- Estrategia.

\\\\- Utilización del entorno.

\\\\- Herramientas de supervivencia.

\\\\- Capacidad para tomar decisiones bajo presión.

Quiero que los jugadores sientan que realmente están en peligro.

\\---

\\\\# 2. HISTORIA Y UNIVERSO

La historia transcurre en un futuro cercano.

Una corporación tecnológica llamada NEXUS realiza experimentos

científicos secretos en instalaciones distribuidas por diferentes

lugares del mundo.

Después de un incidente desconocido, varias instalaciones quedan

abandonadas y se pierde toda comunicación con sus trabajadores.

NEXUS contrata equipos independientes de recuperación para explorar esas

instalaciones y recuperar:

\\\\- Tecnología experimental.

\\\\- Documentos clasificados.

\\\\- Muestras biológicas.

\\\\- Artefactos.

\\\\- Equipamiento científico.

\\\\- Objetos de gran valor.

Los jugadores forman parte de estos equipos.

Su trabajo consiste en entrar en las instalaciones, recuperar los

objetos solicitados y regresar al punto de extracción.

Pero existe un problema.

Algo permanece dentro de las instalaciones.

Algunas entidades parecen conocer el comportamiento humano.

Pueden imitar voces, reproducir sonidos e incluso simular situaciones de

peligro.

La comunicación entre compañeros ya no es completamente confiable.

\\---

\\\\# 3. BUCLE PRINCIPAL DE JUGABILIDAD

La estructura de una partida debe funcionar de la siguiente manera:

1\\\\. Los jugadores llegan a la base de operaciones.

2\\\\. Seleccionan una misión.

3\\\\. Revisan los objetivos y el equipamiento disponible.

4\\\\. Entran en una instalación.

5\\\\. Exploran el escenario.

6\\\\. Localizan objetos y objetivos.

7\\\\. Evitan criaturas y amenazas.

8\\\\. Utilizan herramientas y estrategias para sobrevivir.

9\\\\. Recuperan objetos de valor.

10\\\\. Se dirigen al punto de extracción.

11\\\\. Regresan a la base.

12\\\\. Reciben recompensas según los objetivos cumplidos y los objetos

recuperados.

Cada partida debe presentar situaciones diferentes.

El peligro debe aumentar a medida que los jugadores permanecen dentro de

las instalaciones.

Cuanto más tiempo permanezcan, mayor será el riesgo.

Los jugadores deberán decidir cuándo continuar explorando y cuándo

escapar.

\\---

\\# 4. SISTEMA DE OBJETOS Y EXTRACCIÓN

Los objetos recuperables deben tener características que influyan en las decisiones de los jugadores:

- Valor económico y rareza.
- Peso y volumen.
- Fragilidad y estado de conservación.
- Física e interacción.
- Sonidos al recogerlos, soltarlos, manipularlos o transportarlos.
- Requisitos de manipulación.
- Posibilidad de desmontaje y componentes recuperables, cuando corresponda.
- Posibles efectos secundarios.

Los objetos pequeños suelen poder guardarse en el inventario. Los medianos pueden requerir transporte manual y ocupar las manos. El peso y el volumen deben influir en la movilidad y la capacidad de transporte.

Algunos objetos grandes podrán desmontarse para recuperar componentes valiosos o útiles. El desmontaje debe ser una alternativa de saqueo con coste de tiempo y riesgo acústico, no una acción instantánea ni universal.

No todos los objetos grandes serán desmontables. Los objetos que no puedan desmontarse podrán requerir transporte especial o cooperación entre jugadores cuando su tamaño, peso y valor lo justifiquen.

Los objetos y sus componentes pueden:

- Hacer ruido.
- Activar mecanismos.
- Emitir señales.
- Atraer criaturas.
- Provocar eventos inesperados.
- Tener efectos ambientales.

Los objetos deben utilizar físicas coherentes dentro de las posibilidades del motor. Los jugadores deben poder recogerlos, soltarlos, transportarlos y entregarlos. El transporte debe influir en la movilidad del jugador.

La extracción debe ser una de las partes más tensas de cada partida. La ubicación establecida para la zona de extracción es recepción, en el nivel 1 de la instalación. El procedimiento exacto de activación, entrega y finalización debe respetar las reglas detalladas en la sección 45 y no debe inventarse durante una implementación sin revisar el diseño vigente.

\\\\# 5. CRIATURAS Y ENTIDADES

Las criaturas deben ser los principales elementos de terror.

No quiero enemigos genéricos que simplemente persigan al jugador.

Cada criatura debe tener:

\\\\- Diseño visual propio.

\\\\- Modelo 3D.

\\\\- Animaciones.

\\\\- Sonidos.

\\\\- Inteligencia artificial.

\\\\- Sistema de detección.

\\\\- Comportamientos particulares.

\\\\- Debilidades ambientales.

\\\\- Diferentes estados de comportamiento.

\\\\## EL IMITADOR

Una entidad capaz de reproducir voces y sonidos de los jugadores.

Comportamientos:

\\\\- Imita voces.

\\\\- Reproduce llamadas de auxilio.

\\\\- Genera sonidos falsos.

\\\\- Intenta separar al equipo.

\\\\- Puede reproducir grabaciones escuchadas anteriormente.

\\\\- Utiliza la comunicación como herramienta de engaño.

Su objetivo es confundir y atraer a los jugadores.

La imitación debe resultar convincente y no parecer una reproducción

aleatoria de sonidos.

La arquitectura debe permitir ampliar este sistema progresivamente,

incluyendo voces grabadas por los propios jugadores cuando exista una

implementación técnica viable.

El registro de voces debe realizarse antes de jugar, con consentimiento

explícito del jugador y controles para volver a grabar o eliminar sus

grabaciones.

No se debe transmitir ni almacenar audio personal sin informar al

jugador y obtener su consentimiento.

\\\\## EL VIGILANTE

Una criatura que se desplaza cuando no está siendo observada.

Comportamientos:

\\\\- Permanece inmóvil cuando está siendo observada.

\\\\- Se mueve cuando pierde contacto visual.

\\\\- Puede acercarse progresivamente.

\\\\- Obliga a los jugadores a coordinarse.

\\\\- Puede aprovechar momentos de oscuridad.

Su comportamiento debe generar incertidumbre.

No debe limitarse a avanzar directamente hacia el jugador cuando deja de

ser observado.

Puede:

\\\\- Cambiar de posición cuando pierde contacto visual.

\\\\- Acercarse aprovechando obstáculos y zonas oscuras.

\\\\- Permanecer inmóvil a una distancia inquietante.

\\\\- Investigar sonidos.

\\\\- Esperar cerca de escondites.

\\\\- Aprovechar distracciones.

\\\\- Cambiar su comportamiento según la cantidad de jugadores que lo

observan.

Su inteligencia artificial debe evitar movimientos artificiales o

demasiado predecibles.

\\\\## EL COLECCIONISTA

Una criatura obsesionada con los objetos de valor.

Comportamientos:

\\\\- Busca objetos recuperados.

\\\\- Puede robar objetos.

\\\\- Reacciona al ruido.

\\\\- Investiga objetos abandonados.

\\\\- Persigue especialmente a quienes transportan objetos valiosos.

\\\\## LA SOMBRA

Una entidad que prefiere las zonas oscuras.

Comportamientos:

\\\\- Persigue jugadores aislados.

\\\\- Se desplaza entre zonas oscuras.

\\\\- Puede desaparecer y reaparecer.

\\\\- Utiliza sonidos para generar miedo.

\\\\- Obliga a los jugadores a permanecer coordinados.

\\\\## EXPANSIÓN FUTURA

El sistema debe permitir incorporar nuevas criaturas sin modificar

completamente la arquitectura de inteligencia artificial.

Cada entidad debe tener comportamientos diferenciados y reconocibles.

\\---

\\\\# 6. SISTEMA DE SUPERVIVENCIA SIN ARMAS

ESTA ES UNA DE LAS REGLAS MÁS IMPORTANTES DEL VIDEOJUEGO.

Los jugadores NO pueden utilizar armas.

No implementar:

\\\\- Pistolas.

\\\\- Rifles.

\\\\- Escopetas.

\\\\- Armas cuerpo a cuerpo.

\\\\- Sistemas de combate.

\\\\- Habilidades para matar criaturas.

\\\\- Sistemas de daño ofensivo contra enemigos.

Las criaturas no deben poder eliminarse mediante combate.

Los jugadores deben sobrevivir utilizando herramientas, sigilo,

inteligencia y cooperación.

\\\\## HERRAMIENTAS

Implementar herramientas que ayuden a explorar y sobrevivir.

LINTERNAS:

Permiten explorar zonas oscuras. Deben tener batería limitada.

BENGALAS:

Proporcionan iluminación temporal y pueden ayudar a orientarse.

DETECTORES DE MOVIMIENTO:

Permiten identificar movimientos cercanos.

SENSORES ELECTROMAGNÉTICOS:

Detectan anomalías y determinadas presencias.

DISTRACTORES SONOROS:

Generan sonidos en ubicaciones específicas para desviar la atención de

algunas criaturas.

CÁMARAS PORTÁTILES:

Permiten observar habitaciones a distancia.

BATERÍAS:

Permiten recargar determinados dispositivos.

ESPEJOS DE INSPECCIÓN:

Permiten observar detrás de esquinas sin exponerse completamente.

DISPOSITIVOS DE COMUNICACIÓN:

Permiten comunicarse con compañeros y recibir información.

INHIBIDORES DE SONIDO:

Reducen temporalmente determinados sonidos producidos por los jugadores.

HERRAMIENTAS DE MANTENIMIENTO:

Permiten interactuar con mecanismos, paneles y sistemas de seguridad.

Ninguna herramienta debe convertirse en un arma.

Cada herramienta debe tener ventajas, limitaciones y utilidad real.

\\---

\\\\# 7. SISTEMA DE SIGILO Y DETECCIÓN

Implementar un sistema de detección de jugadores.

Las criaturas deben poder detectar:

\\\\- Sonidos.

\\\\- Movimiento.

\\\\- Distancia.

\\\\- Visibilidad.

\\\\- Iluminación.

\\\\- Interacciones con objetos.

\\\\- Puertas abiertas.

\\\\- Objetos que caen.

\\\\- Equipamiento utilizado.

Correr debe generar más ruido que caminar.

Transportar determinados objetos puede generar sonidos.

Abrir puertas, activar mecanismos y utilizar herramientas puede atraer

la atención de algunas criaturas.

La inteligencia artificial debe reaccionar de forma diferente según el

tipo de criatura.

No todas deben utilizar los mismos sistemas de detección.

\\---

\\\\# 8. SISTEMA DE ESCONDITES

Los escenarios deben permitir que los jugadores se escondan.

Implementar escondites interactivos:

\\\\- Taquillas.

\\\\- Armarios.

\\\\- Conductos.

\\\\- Debajo de escritorios.

\\\\- Detrás de maquinaria.

\\\\- Habitaciones de mantenimiento.

\\\\- Espacios entre estructuras.

Los escondites deben integrarse físicamente en los escenarios.

No deben garantizar seguridad absoluta.

Algunas criaturas pueden inspeccionar determinados escondites.

Otras pueden detectar la respiración, los movimientos o los sonidos del

jugador.

El jugador debe poder entrar y salir de los escondites mediante

interacciones naturales.

\\---

\\\\# 9. SISTEMA DE INTERACCIÓN CON EL ENTORNO

El entorno debe ser una herramienta de supervivencia.

Permitir:

\\\\- Cerrar puertas.

\\\\- Activar alarmas.

\\\\- Apagar luces.

\\\\- Activar maquinaria.

\\\\- Crear distracciones.

\\\\- Bloquear temporalmente accesos.

\\\\- Utilizar rutas alternativas.

\\\\- Activar sistemas de emergencia.

\\\\- Manipular determinados mecanismos.

Las interacciones deben tener consecuencias.

Por ejemplo:

Un jugador puede activar una alarma para atraer una criatura hacia otra

zona mientras sus compañeros escapan.

Otro puede cerrar una puerta industrial para ganar tiempo.

Otro puede apagar las luces para esconderse de una criatura que detecta

movimiento.

El entorno debe permitir diferentes estrategias.

\\---

\\\\# 10. SISTEMA DE RESISTENCIA Y ESTADO FÍSICO

Implementar un sistema de resistencia.

Características:

\\\\- Correr consume energía.

\\\\- Caminar permite recuperar resistencia.

\\\\- La fatiga afecta a la respiración.

\\\\- Transportar objetos pesados dificulta el movimiento.

\\\\- Los jugadores pueden quedarse sin energía durante una persecución.

La resistencia debe equilibrarse para evitar frustraciones.

\\\\## ESTADOS FÍSICOS

Los jugadores pueden sufrir:

\\\\- Cojera temporal.

\\\\- Visión borrosa.

\\\\- Dificultad para correr.

\\\\- Aturdimiento.

\\\\- Incapacitación.

\\\\- Pérdida temporal de orientación.

Estos efectos deben ser comprensibles y tener una duración equilibrada.

\\---

\\\\# 11. SISTEMA DE ESTRÉS Y TERROR PSICOLÓGICO

Implementar un sistema de estrés.

El estrés puede aumentar por:

\\\\- Proximidad de criaturas.

\\\\- Oscuridad.

\\\\- Aislamiento.

\\\\- Sonidos desconocidos.

\\\\- Persecuciones.

\\\\- Eventos paranormales.

\\\\- Situaciones peligrosas.

Sus efectos pueden incluir:

\\\\- Interferencias auditivas.

\\\\- Distorsiones visuales sutiles.

\\\\- Alteraciones de sonido.

\\\\- Respiración acelerada.

\\\\- Sensación de presencia.

\\\\- Falsas señales auditivas.

El sistema debe generar miedo sin quitar arbitrariamente el control al

jugador.

No quiero efectos que dificulten injustamente la jugabilidad.

\\---

\\\\# 12. COOPERACIÓN MULTIJUGADOR

La cooperación debe ser fundamental.

Implementar o adaptar:

\\\\- Creación de salas.

\\\\- Sistema de invitaciones.

\\\\- Unión a partidas.

\\\\- Sincronización de jugadores.

\\\\- Sincronización de objetos.

\\\\- Sincronización de criaturas.

\\\\- Estados de partida.

\\\\- Reconexión.

\\\\- Gestión de desconexiones.

\\\\- Comunicación.

\\\\- Sincronización de eventos.

\\\\- Gestión de misiones.

Fomentar situaciones donde los jugadores necesiten ayudarse.

Ejemplos:

\\\\- Desmontar en equipo objetos complejos cuando el procedimiento lo justifique y transportar entre varios jugadores componentes voluminosos o pesados.

\\\\- Ayudar a un compañero herido.

\\\\- Activar mecanismos simultáneamente.

\\\\- Crear distracciones.

\\\\- Vigilar pasillos.

\\\\- Compartir herramientas.

\\\\- Rescatar compañeros.

\\\\- Coordinar una extracción.

Mantener la autoridad del servidor sobre los elementos importantes de la

partida cuando la arquitectura existente lo permita.

Evitar inconsistencias entre jugadores.

No introducir sistemas de red incompatibles con el proyecto actual.

El desarrollo debe realizarse progresivamente. Primero se pueden validar

las mecánicas principales en un entorno local de un jugador y

posteriormente integrar la sincronización multijugador sin duplicar

innecesariamente los sistemas.

\\---

\\\\# 13. COMUNICACIÓN POR PROXIMIDAD

El sonido debe ser fundamental.

Implementar comunicación por proximidad cuando sea compatible con la

arquitectura existente.

Características:

\\\\- Audio posicional 3D.

\\\\- Voces que disminuyen con la distancia.

\\\\- Comunicación mediante dispositivos de radio.

\\\\- Interferencias.

\\\\- Voces distorsionadas.

\\\\- Sonidos falsos del Imitador.

\\\\- Comunicación afectada por determinadas zonas.

Los jugadores deben poder escuchar a sus compañeros según su posición.

El silencio también debe formar parte del terror.

La arquitectura de comunicación debe contemplar la futura integración de

las voces grabadas de los jugadores para el sistema del Imitador.

No sacrificar la privacidad ni la estabilidad del sistema por

implementar esta característica prematuramente.

\\## SISTEMA DE RADIO Y ALIMENTACIÓN POR PILAS

Cuando los jugadores estén fuera del alcance de la comunicación por proximidad, podrán comunicarse mediante radios portátiles.

Cada jugador dispondrá de una radio individual con una batería independiente.

Características:

\\- Comunicación mediante Push-to-Talk.

\\- Canal compartido inicial para el equipo.

\\- Posibilidad de cambiar de canal cuando el diseño de la misión lo permita.

\\- Alcance y calidad de señal condicionados por la distancia, las estructuras y las características de cada instalación.

\\- Interferencias, estática, distorsiones y pérdida temporal de señal en zonas determinadas o durante eventos de la instalación.

\\- Indicador de transmisión, canal, nivel de batería y calidad de señal.

\\- La radio consume más energía al transmitir que al recibir.

\\- La batería baja puede provocar degradación progresiva de la comunicación, sin introducir distorsiones constantes o injustas.

\\- Cuando la batería se agote, la radio dejará de funcionar hasta reemplazar sus pilas.

Las radios utilizan pilas reemplazables que los jugadores pueden encontrar durante la exploración de las instalaciones.

Tipos de pilas previstos:

\\- Pilas comunes: restauran una parte de la carga.

\\- Pilas de alta capacidad: restauran una mayor cantidad de carga o permiten recuperar la carga completa.

La disponibilidad de pilas debe equilibrarse según la duración y dificultad de cada misión. No deben aparecer en cantidades que eliminen la gestión del recurso ni ser tan escasas que obliguen a buscar pilas constantemente.

La radio es una herramienta de supervivencia y coordinación, no una obligación de gestión permanente. Quedarse sin batería no debe impedir toda comunicación: la comunicación por proximidad seguirá funcionando con normalidad cuando los jugadores estén suficientemente cerca.

La radio no debe revelar automáticamente la ubicación de los compañeros. La información sobre su posición debe obtenerse mediante la comunicación y la exploración.

\\## ENGAÑO E INTERFERENCIA DEL IMITADOR EN LAS RADIOS

El Imitador podrá aprovechar el sistema de radio para engañar a los jugadores:

\\- Transmitir mensajes falsos utilizando voces que haya imitado.

\\- Reproducir llamadas de auxilio o instrucciones falsas.

\\- Reproducir fragmentos de conversaciones escuchadas anteriormente y sacarlos de contexto.

\\- Hacer creer que un compañero está transmitiendo cuando no es así.

\\- Aprovechar momentos de interferencia para aumentar la incertidumbre.

Las interferencias normales y los engaños del Imitador deben contar con pistas auditivas y de comportamiento coherentes. No deben ser siempre fáciles de distinguir, pero tampoco deben convertirse en engaños arbitrarios imposibles de interpretar.

El sistema debe respetar los requisitos de privacidad y consentimiento establecidos para la captura, grabación y reproducción de voces. No transmitir ni almacenar audio personal sin informar al jugador y obtener su consentimiento explícito.

\\## REGLAS DE DISEÑO DE LA COMUNICACIÓN

\\- La comunicación por proximidad y la comunicación por radio deben complementarse.

\\- La proximidad utiliza audio posicional 3D y se ve afectada por distancia y entorno.

\\- La radio permite comunicarse a distancia dentro de sus límites de alcance, señal y batería.

\\- La pérdida de batería de la radio nunca debe desactivar la comunicación por proximidad.

\\- La radio no debe convertirse en un rastreador de compañeros ni proporcionar información automática que elimine la incertidumbre.

\\- Las limitaciones de señal y batería deben generar decisiones y tensión, no frustración constante.

\\- Las comunicaciones y sus eventos importantes deberán integrarse con el sistema de audio, las criaturas y la arquitectura multijugador cuando corresponda.

\\- Antes de implementar, inspeccionar y reutilizar los sistemas de audio y comunicación existentes; no duplicarlos ni asumir que ya están sincronizados en multijugador.

\\---

\\\\# 14. MAPAS E INSTALACIONES

Crear escenarios con identidades visuales propias.

\\\\## LABORATORIO SUBTERRÁNEO

\\\\- Laboratorios.

\\\\- Salas de experimentación.

\\\\- Cámaras de contención.

\\\\- Pasillos metálicos.

\\\\- Salas de control.

\\\\- Sistemas de seguridad.

\\\\## HOSPITAL EXPERIMENTAL

\\\\- Habitaciones médicas.

\\\\- Quirófanos.

\\\\- Morgue.

\\\\- Pasillos deteriorados.

\\\\- Salas de aislamiento.

\\\\## MINA DE INVESTIGACIÓN

\\\\- Túneles.

\\\\- Ascensores industriales.

\\\\- Maquinaria.

\\\\- Sistemas eléctricos.

\\\\- Zonas inundadas.

\\\\## COMPLEJO MILITAR

\\\\- Búnkeres.

\\\\- Almacenes.

\\\\- Sistemas de vigilancia.

\\\\- Laboratorios.

\\\\- Puertas de seguridad.

\\\\## CENTRO COMERCIAL CLAUSURADO

\\\\- Tiendas abandonadas.

\\\\- Pasillos comerciales.

\\\\- Almacenes.

\\\\- Escaleras mecánicas.

\\\\- Zonas de mantenimiento.

Los mapas deben tener:

\\\\- Habitaciones interconectadas.

\\\\- Zonas secretas.

\\\\- Rutas alternativas.

\\\\- Escondites.

\\\\- Objetos interactivos.

\\\\- Elementos ambientales.

\\\\- Distribuciones variables cuando sea viable.

\\---

\\\\# 15. DIRECCIÓN ARTÍSTICA Y GRÁFICOS 3D

ESTA SECCIÓN TIENE PRIORIDAD ALTA.

Quiero conseguir una estética de terror cinematográfico y ciencia

ficción.

Utilizar Godot 4.x.

Preferir el renderer Forward+ cuando sea compatible con el hardware

objetivo.

Las imágenes de referencia están almacenadas dentro de:

\\\\\\\`fotos-referencia/\\\\\\\`

Esta carpeta se encuentra en la raíz del proyecto.

\\\\## ANÁLISIS OBLIGATORIO DE LAS REFERENCIAS

Antes de desarrollar escenarios:

1\\\\. Localizar \\\\\\\`fotos-referencia/\\\\\\\`.

2\\\\. Identificar todas las imágenes.

3\\\\. Analizar visualmente cada una.

4\\\\. Identificar características de iluminación.

5\\\\. Analizar arquitectura y composición.

6\\\\. Identificar materiales y texturas.

7\\\\. Analizar ambientación y atmósfera.

8\\\\. Extraer una dirección artística coherente.

Las imágenes representan el objetivo visual del proyecto.

No quiero que simplemente reproduzcas las imágenes.

Quiero que utilices su lenguaje visual para construir escenarios 3D

reales dentro de Godot.

No utilizar las imágenes como fondos planos para simular escenarios.

No ignorarlas ni sustituir su análisis por descripciones genéricas.

Si alguna imagen no puede visualizarse, indícalo.

No modificar, eliminar, renombrar ni sobrescribir ningún archivo de

\\\\\\\`fotos-referencia/\\\\\\\`.

Esta carpeta debe permanecer intacta.

\\\\## REFERENCIA VISUAL OFICIAL DE LAS CRIATURAS

Dentro de \\\`fotos-referencia/\\\` existe una imagen llamada \\\`modelos-referencia\\\` que contiene los diseños conceptuales oficiales de las cuatro criaturas del juego.

Esta referencia es de cumplimiento obligatorio durante el diseño, modelado, texturizado y animación de las criaturas.

Antes de crear o modificar cualquier criatura:

1\\. Localizar la imagen \\\`modelos-referencia\\\` dentro de \\\`fotos-referencia/\\\`, comprobando su extensión real. No asumir que es una carpeta ni inventar su formato.

2\\. Analizar cuidadosamente los cuatro diseños representados.

3\\. Respetar sus siluetas, anatomía, proporciones, características físicas, materiales y rasgos distintivos.

4\\. Mantener la identidad visual de cada criatura para que sea reconocible incluso en condiciones de poca iluminación.

5\\. Utilizar estos diseños como referencia principal, evitando reinterpretaciones que alteren significativamente su apariencia original.

Los nombres de las criaturas son:

\\- El Imitador.

\\- El Vigilante.

\\- El Coleccionista.

\\- La Sombra.

La imagen es únicamente una referencia visual. No debe utilizarse como textura, fondo o sustituto de modelos 3D reales.

**\*\*\\\*\\\*PROHIBIDO modificar, eliminar, renombrar o sobrescribir la imagen original.\\\*\\\*\*\*** Todos los modelos, materiales, texturas y animaciones deben desarrollarse como recursos independientes dentro del proyecto.

\\\\## ILUMINACIÓN

Implementar:

\\\\- Iluminación dinámica.

\\\\- Luces de emergencia rojas.

\\\\- Iluminación industrial.

\\\\- Fuentes de luz intermitentes.

\\\\- Sombras dinámicas.

\\\\- Iluminación volumétrica.

\\\\- Linternas realistas.

\\\\- Contrastes entre zonas iluminadas y oscuras.

\\\\- Iluminación indirecta cuando sea viable.

La iluminación debe contribuir directamente a generar miedo.

\\\\## ATMÓSFERA

Implementar:

\\\\- Niebla volumétrica.

\\\\- Polvo suspendido.

\\\\- Partículas ambientales.

\\\\- Vapor de tuberías.

\\\\- Humo.

\\\\- Ambientes húmedos.

\\\\- Profundidad atmosférica.

\\\\- Efectos ambientales.

\\\\## MATERIALES Y TEXTURAS

Utilizar materiales PBR.

Incluir:

\\\\- Metales oxidados.

\\\\- Hormigón deteriorado.

\\\\- Suelos húmedos.

\\\\- Cristales rotos.

\\\\- Pintura descascarada.

\\\\- Suciedad.

\\\\- Manchas.

\\\\- Superficies reflectantes.

\\\\- Diferentes niveles de rugosidad.

\\\\## POSTPROCESAMIENTO

Implementar cuando sea apropiado:

\\\\- Ambient Occlusion.

\\\\- Tonemapping.

\\\\- Color Grading cinematográfico.

\\\\- Bloom moderado.

\\\\- Viñeta.

\\\\- Profundidad atmosférica.

\\\\- Aberración cromática muy sutil.

\\\\- Control de exposición.

Evitar efectos excesivos.

\\\\## DETALLE AMBIENTAL

Los escenarios deben contar historias mediante sus elementos.

Incluir:

\\\\- Tuberías.

\\\\- Cables.

\\\\- Paneles eléctricos.

\\\\- Monitores CRT.

\\\\- Cámaras de seguridad.

\\\\- Puertas industriales.

\\\\- Señalización.

\\\\- Equipamiento científico.

\\\\- Mobiliario abandonado.

\\\\- Maquinaria.

\\\\- Sistemas de ventilación.

\\\\- Luces de emergencia.

No quiero escenarios vacíos ni habitaciones genéricas.

\\---

\\\\# 16. DISEÑO DE PERSONAJES

Los personajes deben parecer trabajadores de recuperación.

Diseño:

\\\\- Trajes industriales.

\\\\- Cascos.

\\\\- Linternas.

\\\\- Mochilas.

\\\\- Equipamiento de protección.

\\\\- Herramientas.

\\\\- Accesorios personalizables.

Implementar:

\\\\- Modelos 3D.

\\\\- Animaciones.

\\\\- Caminar.

\\\\- Correr.

\\\\- Saltar.

\\\\- Agacharse.

\\\\- Recoger objetos.

\\\\- Transportar objetos.

\\\\- Interactuar.

\\\\- Esconderse.

\\\\- Recibir daño.

\\\\- Caer.

\\\\- Ser auxiliado.

Los personajes no deben tener armas.

\\---

\\\\# 17. BASE DE OPERACIONES Y PROGRESIÓN

Crear una base de operaciones perteneciente a NEXUS.

Debe funcionar como centro entre partidas.

Incluir:

\\\\- Selección de misiones.

\\\\- Tienda.

\\\\- Equipamiento.

\\\\- Personalización.

\\\\- Estadísticas.

\\\\- Contratos.

\\\\- Preparación del equipo.

\\\\- Información de instalaciones.

\\\\- Sistema de recompensas.

Los jugadores pueden utilizar el dinero conseguido para comprar

herramientas y mejoras.

La progresión debe ofrecer nuevas posibilidades sin convertir a los

jugadores en combatientes.

\\---

\\\\# 18. INTERFAZ

La interfaz debe parecer un sistema tecnológico de una corporación de

recuperación.

Identidad visual:

\\\\- Verde oscuro.

\\\\- Gris industrial.

\\\\- Naranja de seguridad.

\\\\- Paneles tecnológicos.

\\\\- Tipografía técnica.

\\\\- Indicadores industriales.

\\\\- Animaciones sutiles.

Implementar:

\\\\- Menú principal.

\\\\- Lobby.

\\\\- Sala de espera.

\\\\- Selección de misión.

\\\\- HUD.

\\\\- Inventario.

\\\\- Indicadores de salud.

\\\\- Estado de compañeros.

\\\\- Objetivos.

\\\\- Comunicaciones.

\\\\- Pantalla de extracción.

\\\\- Resultados.

\\\\- Tienda.

\\\\- Configuración.

Evitar interfaces genéricas.

\\---

\\\\# 19. AUDIO Y DISEÑO SONORO

Implementar:

\\\\- Audio ambiental dinámico.

\\\\- Audio posicional 3D.

\\\\- Sonidos industriales.

\\\\- Ruidos metálicos.

\\\\- Interferencias de radio.

\\\\- Voces distorsionadas.

\\\\- Sonidos de criaturas.

\\\\- Respiración.

\\\\- Pasos.

\\\\- Sonidos de objetos.

\\\\- Eventos aleatorios.

\\\\- Silencios ambientales.

Cada criatura debe tener una identidad sonora.

Los sonidos deben permitir que el jugador identifique peligros sin

necesariamente verlos.

El Imitador debe utilizar el sonido como herramienta principal de

engaño.

\\---

\\\\# # 20. RECURSOS Y MODELOS 3D

No quiero que los escenarios definitivos estén construidos únicamente con cubos, cilindros o geometrías provisionales.

Utilizar modelos 3D, materiales, texturas y animaciones apropiadas.

Se pueden investigar recursos gratuitos y de código abierto.

Priorizar recursos con licencias compatibles con distribución comercial.

Si no existe un recurso apropiado:

- Crear modelos propios.
- Crear materiales procedurales.
- Diseñar elementos modulares.
- Crear texturas propias.
- Reutilizar recursos de forma coherente.

No introducir recursos de procedencia desconocida.

Documentar las licencias de los recursos externos utilizados.

Los prototipos geométricos pueden utilizarse durante el desarrollo de mecánicas, pero deben identificarse como provisionales y no confundirse con el arte final.

### Realismo y nivel de detalle

Siempre que crees objetos, escenarios, mobiliario, maquinaria, herramientas o cualquier elemento 3D, busca el mayor nivel de realismo y detalle visual posible dentro de las capacidades del proyecto.

- Los objetos deben tener geometría trabajada, proporciones creíbles y detalles propios de sus equivalentes en el mundo real.
- Utiliza biseles, uniones, tornillos, paneles, ranuras, desgaste, imperfecciones y otros detalles cuando corresponda.
- Los materiales deben representar correctamente las superficies: metal, plástico, vidrio, goma, tela, madera, etc.
- Evita objetos genéricos, excesivamente simples o que parezcan juguetes.
- No confundas optimización con falta de detalle: busca un equilibrio entre calidad visual y rendimiento.
- Antes de crear un modelo desde cero, busca referencias visuales para reproducir correctamente su diseño.
- El resultado debe tener calidad de un videojuego comercial, no parecer un prototipo ni un objeto de prueba.
- El realismo y el nivel de detalle deben respetar la dirección artística oficial de FRECUENCIA MUERTA. Los objetos y escenarios deben ser visualmente convincentes, sin romper la coherencia estética del videojuego ni el estilo establecido para los personajes y criaturas.

\\---

\\\\# 21. OPTIMIZACIÓN Y RENDIMIENTO

Hardware objetivo de desarrollo:

\\\\- NVIDIA GTX 1650 Ti de 4 GB.

\\\\- 32 GB de RAM.

\\\\- Procesador Intel Core i5.

Quiero gráficos atractivos sin exigir hardware de última generación.

Optimizar:

\\\\- Geometría.

\\\\- Texturas.

\\\\- Luces dinámicas.

\\\\- Sombras.

\\\\- Partículas.

\\\\- Físicas.

\\\\- Materiales.

\\\\- Distancia de renderizado.

\\\\- Efectos volumétricos.

Implementar:

\\\\- LOD.

\\\\- Occlusion Culling.

\\\\- Gestión eficiente de recursos.

\\\\- Configuraciones gráficas.

\\\\- Optimización de escenarios.

\\\\- Control de calidad visual.

Crear perfiles:

\\\\- Bajo.

\\\\- Medio.

\\\\- Alto.

\\\\- Ultra.

Permitir ajustar:

\\\\- Resolución.

\\\\- Calidad de sombras.

\\\\- Texturas.

\\\\- Distancia de renderizado.

\\\\- Efectos.

\\\\- Antialiasing.

\\\\- Niebla volumétrica.

\\\\- Oclusión ambiental.

Priorizar estabilidad y FPS.

No sacrificar innecesariamente la calidad visual.

Todas las optimizaciones deben medirse en condiciones reproducibles.

No presentar mediciones de escenas de prueba como si fueran resultados

del videojuego completo.

\\---

\\\\# 22. ARQUITECTURA Y CALIDAD DEL CÓDIGO

El código debe ser:

\\\\- Modular.

\\\\- Mantenible.

\\\\- Reutilizable.

\\\\- Escalable.

\\\\- Documentado.

\\\\- Optimizado.

Evitar duplicación.

Mantener separación entre sistemas.

No crear dependencias innecesarias.

No sustituir tecnologías que ya funcionan.

No introducir cambios arquitectónicos importantes sin justificar su

necesidad.

Mantener compatibilidad con las funcionalidades existentes.

Utilizar las características propias de Godot de forma apropiada.

Antes de crear un sistema nuevo, comprobar si ya existe uno que pueda

reutilizarse o ampliarse.

\\---

\\\\# 23. ANÁLISIS Y CONSERVACIÓN DEL PROYECTO EXISTENTE

El análisis inicial del proyecto ya se realizó durante las fases

anteriores.

Sin embargo, antes de modificar una parte del proyecto debes

inspeccionar el estado actual de los archivos y sistemas relacionados

con el cambio.

Identifica, cuando corresponda:

1\\\\. Motor y versión.

2\\\\. Lenguajes y tecnologías.

3\\\\. Estructura de carpetas.

4\\\\. Escenas existentes.

5\\\\. Scripts.

6\\\\. Sistemas implementados.

7\\\\. Sistemas pendientes.

8\\\\. Arquitectura multijugador.

9\\\\. Controladores de personajes.

10\\\\. Sistemas de físicas.

11\\\\. Recursos gráficos.

12\\\\. Sistemas de audio.

13\\\\. Problemas técnicos.

14\\\\. Funcionalidades que deben conservarse.

Determina qué elementos pueden reutilizarse.

NO reconstruyas el proyecto desde cero.

NO elimines funcionalidades existentes sin autorización.

NO modifiques archivos innecesariamente.

NO inventes funcionalidades.

NO declares tareas terminadas si no han sido probadas.

Antes de realizar cambios:

\\\\- Comprueba las dependencias.

\\\\- Identifica los archivos afectados.

\\\\- Revisa las escenas relacionadas.

\\\\- Comprueba las referencias entre recursos.

\\\\- Evita romper sistemas existentes.

\\\\- Mantén los cambios limitados al objetivo de la tarea.

\\---

\\\\# 24. PLAN DE IMPLEMENTACIÓN

Organizar el desarrollo en fases.

FASE 1: Diagnóstico del proyecto y arquitectura.

FASE 2: Definición de identidad visual y análisis de referencias.

FASE 3: Escenario de prueba y vertical slice jugable.

FASE 4: Personajes, modelos y animaciones.

FASE 5: Sistema de supervivencia sin armas.

FASE 6: Criaturas e inteligencia artificial.

FASE 7: Exploración, objetos y extracción.

FASE 8: Multijugador y sincronización.

FASE 9: Audio y comunicación.

FASE 10: Base de operaciones y progresión.

FASE 11: Optimización y pruebas.

Cada fase debe incluir:

\\\\- Objetivos.

\\\\- Archivos involucrados.

\\\\- Cambios necesarios.

\\\\- Dependencias.

\\\\- Riesgos.

\\\\- Criterios de aceptación.

\\\\- Pruebas.

No implementar todas las fases simultáneamente.

No repetir fases que ya estén completadas, salvo que exista una razón

técnica justificada.

Actualizar la documentación cuando una fase o funcionalidad cambie de

estado.

\\---

\\\\# 25. OBJETIVO PRINCIPAL: VERTICAL SLICE

Antes de desarrollar todos los mapas quiero una demostración

representativa de la calidad final.

Crear un escenario de prueba con:

\\\\- Un pasillo industrial.

\\\\- Una habitación de laboratorio.

\\\\- Una puerta de seguridad.

\\\\- Iluminación de emergencia.

\\\\- Niebla volumétrica.

\\\\- Materiales PBR.

\\\\- Objetos físicos.

\\\\- Una linterna funcional.

\\\\- Un escondite interactivo.

\\\\- Sonido ambiental.

\\\\- Una criatura de prueba.

\\\\- Sistema básico de sigilo.

La criatura debe poder detectar al jugador y reaccionar ante sus

movimientos y sonidos.

El jugador debe poder esconderse y escapar sin utilizar armas.

Este escenario debe representar la calidad visual y jugable que queremos

conseguir.

No quiero una escena compuesta únicamente por primitivas ni un prototipo

visual extremadamente básico.

Debe ser una demostración representativa del resultado final.

El desarrollo de este objetivo debe realizarse por etapas.

Primero debe existir un escenario funcional y estable. Después se

integran progresivamente las mecánicas, la criatura, los objetos y los

sistemas de supervivencia.

No intentar implementar todo en una sola operación.

\\---

\\\\# 26. REGLAS OBLIGATORIAS

1\\\\. No implementar armas.

2\\\\. No implementar combate directo.

3\\\\. No permitir matar criaturas.

4\\\\. No reconstruir el proyecto desde cero.

5\\\\. No eliminar sistemas existentes sin autorización.

6\\\\. No modificar las imágenes de referencia.

7\\\\. No sustituir la arquitectura existente sin justificación.

8\\\\. No implementar todas las funcionalidades simultáneamente.

9\\\\. No generar sistemas ficticios.

10\\\\. No declarar funcionalidades terminadas sin pruebas.

11\\\\. Priorizar rendimiento y estabilidad.

12\\\\. Mantener coherencia visual y jugable.

13\\\\. No sobrescribir archivos de referencia.

14\\\\. No introducir recursos externos sin comprobar su procedencia y

licencia.

15\\\\. No asumir que una funcionalidad está sincronizada en multijugador

si solo funciona localmente.

16\\\\. No ocultar errores ni resultados negativos de las pruebas.

17\\\\. No eliminar código existente únicamente porque parezca innecesario

sin comprobar sus dependencias.

18\\\\. No realizar cambios destructivos sin autorización.

19\\\\. No modificar configuraciones importantes del proyecto sin

justificar el cambio.

20\\\\. Mantener documentación técnica actualizada.

\\---

\\\\# 27. FORMA DE TRABAJO Y AUTORIZACIÓN DE CAMBIOS

Esta sección sustituye las instrucciones de inicio que se utilizaron

durante el diagnóstico inicial del proyecto.

El diagnóstico inicial y la definición de identidad visual ya se

realizaron.

Por tanto, NO debes comenzar cada nueva tarea solicitando nuevamente un

diagnóstico completo.

Tampoco debes permanecer permanentemente en modo Plan.

\\\\## ANTES DE IMPLEMENTAR

Cuando recibas una tarea:

1\\\\. Comprende el objetivo.

2\\\\. Consulta este documento.

3\\\\. Inspecciona los archivos relacionados.

4\\\\. Comprueba qué sistemas ya existen.

5\\\\. Identifica dependencias y posibles conflictos.

6\\\\. Determina la estrategia de implementación.

7\\\\. Divide el trabajo si es necesario.

\\\\## DURANTE LA IMPLEMENTACIÓN

\\\\- Trabaja de forma ordenada.

\\\\- Implementa una funcionalidad a la vez.

\\\\- Reutiliza sistemas existentes.

\\\\- No realices refactorizaciones ajenas al objetivo.

\\\\- No elimines funcionalidades aprobadas.

\\\\- Mantén el proyecto ejecutable.

\\\\- Realiza pruebas después de cada cambio importante.

\\\\## AL FINALIZAR

Informa:

1\\\\. Qué se implementó.

2\\\\. Qué archivos se modificaron.

3\\\\. Qué archivos nuevos se crearon.

4\\\\. Qué sistemas existentes se reutilizaron.

5\\\\. Qué pruebas se ejecutaron.

6\\\\. Qué resultados se obtuvieron.

7\\\\. Qué problemas siguen pendientes.

8\\\\. Qué limitaciones tiene la implementación.

9\\\\. Qué conviene hacer a continuación.

No afirmes que algo funciona si no lo has comprobado.

Si una tarea requiere una decisión importante que puede cambiar la

arquitectura, eliminar datos o afectar sistemas ajenos al objetivo,

explica el problema y espera autorización.

Para cambios normales, necesarios y coherentes con una tarea aprobada,

puedes proceder sin solicitar confirmación por cada archivo.

\\---

\\\\# 28. USO DE SKILLS ESPECIALIZADAS

Durante el desarrollo debes aprovechar las skills especializadas

disponibles en OpenCode.

Antes de implementar una tarea, identifica si existe alguna skill que

pueda mejorar el resultado.

Priorizar las siguientes áreas:

\\\\## GODOT

Utilizar skills especializadas cuando corresponda para:

\\\\- GDScript.

\\\\- Nodos y escenas.

\\\\- Desarrollo 3D.

\\\\- Física.

\\\\- Animaciones.

\\\\- Audio.

\\\\- Shaders.

\\\\- Interfaz.

\\\\- Señales y grupos.

\\\\- Multijugador.

\\\\## INTELIGENCIA ARTIFICIAL

Utilizar skills relacionadas con:

\\\\- Game AI.

\\\\- Máquinas de estados.

\\\\- Árboles de comportamiento.

\\\\- Utility AI.

\\\\- Sistemas de percepción.

\\\\- Comportamientos de criaturas.

\\\\- Navegación.

\\\\## DISEÑO Y OPTIMIZACIÓN

Utilizar skills relacionadas con:

\\\\- Level Design.

\\\\- Procedural Generation.

\\\\- Camera Systems.

\\\\- Performance Optimization.

\\\\- Diseño de niveles.

\\\\- Optimización gráfica.

\\\\- Arquitectura de videojuegos.

\\\\## REGLAS DE USO

1\\\\. Utiliza las skills cuando sean relevantes para la tarea.

2\\\\. No invoques skills innecesarias.

3\\\\. No instales dependencias sin necesidad.

4\\\\. No confíes ciegamente en las recomendaciones de una skill.

5\\\\. Comprueba que sus indicaciones sean compatibles con la versión de

Godot y la arquitectura del proyecto.

6\\\\. Verifica las implementaciones mediante pruebas reales.

7\\\\. No permitas que una skill contradiga las reglas fundamentales de

este documento.

8\\\\. Prioriza siempre la estabilidad, el rendimiento y la coherencia del

proyecto.

Las skills son herramientas de apoyo, no sustituyen el análisis técnico.

\\---

\\\\# 29. ESTADO ACTUAL DEL DESARROLLO

Esta sección debe mantenerse actualizada conforme avance el proyecto.

\\\\## FASE 1: DIAGNÓSTICO

Estado: COMPLETADA.

El proyecto fue inspeccionado para identificar su estructura,

tecnologías y posibilidades de evolución.

\\\\## FASE 2: IDENTIDAD VISUAL Y LOOK DEVELOPMENT

Estado: COMPLETADA.

Se realizó un trabajo de identidad visual y desarrollo de apariencia

para FRECUENCIA MUERTA.

Se trabajó en:

\\\\- Escenario de corredor industrial.

\\\\- Laboratorio.

\\\\- Puerta de seguridad.

\\\\- Materiales.

\\\\- Iluminación.

\\\\- Atmósfera.

\\\\- Configuración gráfica.

\\\\- Renderer Forward+.

Se generaron capturas de referencia:

\\\\- \\\\\\\`docs/fm_lookdev_corridor.png\\\\\\\`

\\\\- \\\\\\\`docs/fm_lookdev_lab.png\\\\\\\`

\\\\- \\\\\\\`docs/fm_lookdev_door.png\\\\\\\`

Documentación:

\\\\- \\\\\\\`docs/fm_lookdev.md\\\\\\\`

Se realizaron pruebas de rendimiento en una NVIDIA GTX 1650 Ti con

Forward+ y VSync desactivado.

Resultados registrados:

\\\\- Corredor a 1280x720: aproximadamente 172--174 FPS.

\\\\- Corredor a 1920x1080: aproximadamente 95--99 FPS.

\\\\- Laboratorio a 1920x1080: aproximadamente 92--94 FPS.

IMPORTANTE:

Estas mediciones corresponden a las escenas de look development.

NO representan el rendimiento del videojuego final.

No deben utilizarse como garantía de rendimiento cuando se incorporen

personajes, físicas, criaturas, efectos, audio y multijugador.

\\\\## ESTADO VISUAL CONOCIDO

Durante las pruebas se identificaron aspectos que pueden seguir

mejorándose:

\\\\- El laboratorio tiene zonas visualmente vacías.

\\\\- El anillo cian del tanque puede resultar demasiado protagonista.

\\\\- La pantalla necesita mejorar su legibilidad.

\\\\- La puerta del corredor está demasiado distante.

\\\\- Parte de la geometría sigue siendo provisional.

No rehacer todo el trabajo visual.

Evaluar cada mejora y conservar lo que ya funciona.

\\\\## FASE 3: VERTICAL SLICE JUGABLE

Estado: SIGUIENTE OBJETIVO.

El objetivo es transformar el trabajo visual existente en una

experiencia jugable.

La primera versión debe incluir progresivamente:

1\\\\. Escenario funcional de corredor y laboratorio.

2\\\\. Cámara en primera persona.

3\\\\. Movimiento del jugador.

4\\\\. Linterna con batería.

5\\\\. Objeto físico que pueda recogerse, transportarse y soltarse.

6\\\\. Escondite funcional.

7\\\\. El Vigilante.

8\\\\. Detección mediante ruido y visión.

9\\\\. Comportamiento de la criatura al ser observada.

10\\\\. Sistema de extracción al final del recorrido.

La primera implementación debe utilizar un jugador local como entorno de

prueba.

NO desarrollar todavía todo el sistema multijugador.

La arquitectura debe evitar que las futuras funciones multijugador

obliguen a rehacer completamente los sistemas existentes.

\\\\## ESTADO DE VESTIDO DE SALAS V06

\\\\- Vestuarios (Z05): COMPLETADO. Blockout + `vestuarios_art.glb` (106

  objetos, 51.050 tris, 5,97 MB), 13 luces de sala, 131 mallas y 104

  colliders en la escena. Ver `docs/FM_VESTUARIOS_ART.md`.

\\\\- Control de Acceso (Z04): COMPLETADO Y RECONSTRUIDO CON CALIDAD.
  Blockout + `control_art.glb` (88 objetos, 69.708 tris, 7,73 MB), 18 luces
  de sala, 114 mallas y 71 colliders en la escena. QA subset 101 objetos
  PASS 0/59. Incluye tornos realistas, garita de aluminio/vidrio, racks 19",
  muro de CRT, techo registrable, cladding, clutter de abandono y suelo
  texturizado. Ver `docs/FM_CONTROL_ACCESS_ART.md`.

\\\\- Almacén / Suministros (Z06): COMPLETADO. Blockout + `warehouse_art.glb`

  (88 objetos, 137.808 tris, 20,09 MB), 15 luces de sala, 132 mallas y 79

  colliders en la escena. Ver `docs/FM_WAREHOUSE_ART.md`.

\\\\- Mantenimiento (Z07): COMPLETADO. Blockout + `maintenance_art.glb`

  (104 objetos, 95.230 tris, 21,63 MB), 20 luces de sala, 143 mallas y 102

  colliders en la escena. Ver `docs/FM_MAINTENANCE_ART.md`.

\\\\- Oficinas / Administración (Z08): COMPLETADO. Blockout + `offices_art.glb`

  (262 objetos, 178.810 tris, 9,72 MB), 25 luces de sala, 292 mallas y 167

  colliders en la escena. Ver `docs/FM_OFFICES_ART.md`.

\\\\- Aseo de planta (Z09): COMPLETADO. Blockout + `restroom_art.glb`

  (25 objetos, 16.188 tris, 1,64 MB), 14 luces de sala, 39 mallas y 20

  colliders en la escena. Ver `docs/FM_RESTROOM_ART.md`.

\\\\- Escaleras principales y salidas E1/E2 (Z11/Z12a/Z12b): COMPLETADO.

  Blockout + `stairs_main_art.glb`, `stairs_e1_art.glb` y

  `stairs_e2_art.glb` (44 objetos, 24.954 tris, 4,03 MB), 21 luces de

  sala, 162 mallas y 119 colliders en las escenas. Ver

  `docs/FM_STAIRS_ART.md`.

\\\\- Revisión global de cierre (2026-11-16): COMPLETADA. Las nueve salas

  blockout del Nivel 1 V06 están vestidas y verificadas. Escena: 5.032.386

  tris, 4.500 mallas, 743 materiales, 158 luces y 1.434 colliders. Pruebas:

  smoke 403/0, gameplay 105/0, full run 49/0, presets 194/0 y perf 1280×720

  PASS. Ver `docs/FM_LEVEL1_V06_CLOSURE.md`.

\\\\- Correcciones MEP V06 (2026-11-16): APLICADAS. Resueltos los cuatro
  conflictos críticos (Almacén/ServiceLink, Oficinas/conector, Aseo y
  Mantenimiento), añadidos HVAC local en Control y transición en StairsMain,
  y conectadas las bandejas de E1/E2 a Almacén y Mantenimiento mediante
  sleeves y ramales (`WH_E1_TrayLink_CABLE`, `MT_E2_TrayLink_CABLE`,
  `ST_E1_TrayLink_CABLE`, `ST_E2_TrayLink_CABLE`). QA PASS 0 por sala, GLB
  reexportados, smoke 403/0, gameplay 105/0, full 49/0, presets 194/0 y perf
  1280×720 PASS (556,2 fps medios). Ver `docs/FM_MEP_AUDIT_V06.md` sección 11.

\\\\- Conectividad del Nivel 1 (2026-11-16): FASES 1+2 IMPLEMENTADAS. La red
  `L1_ARCH_ALTERNATE` se exportó como `alternate_routes.glb` (86 mallas, 1.032
  tris, 104.816 bytes) y se integró fuera de `Sectors` con 27 luces y 86
  colliders. Se añadió `security_connector.glb` (3 mallas, 36 tris), se
  reexportó `security_sector.glb` sin la cinta de la barrera sur y se
  añadieron 8 `NavigationLink3D` de capa 1, incluidos los accesos de
  Seguridad. Rutas: EastGallery, MaintCorridor, NorthGallery, OfficesCrawl,
  ReceptionStair, ServiceLoop y NWStair. Las rutas de 1,25 m son solo para el
  jugador agachado; la IA principal no entra. Ver
  `docs/FM_ALTERNATE_ROUTES.md`.

\\- Arte de rutas alternativas (2026-11-16): IMPLEMENTADO.
  `alternate_routes_art.glb` (20 objetos, 38.632 tris, 1.545.912 bytes, 7
  materiales) integrado como `AlternateRoutesDressing`; incluye conducciones,
  13 carteles sobre paramentos reales, franjas de peligro, líneas, charcos y
  balizas. QA 134 objetos PASS 0; los 13 carteles se verificaron legibles y
  sin espejo. Perf 1280×720 PASS con 581,0 fps medios. Ver
  `docs/FM_ALTERNATE_ROUTES_ART.md`.

\\- IA y encuentro de Seguridad (2026-11-16): IMPLEMENTADOS. La patrulla del
  segundo Vigilante pasa a 9 puntos y sale al corredor por el acceso sur,
  rodeando el mostrador; se añadió el escondite `HideSecurityLockers` en las
  taquillas de la pared sur. Sin cambios de geometría ni GLB. Pruebas: smoke
  411/0, gameplay 108/0, full 49/0, presets 194/0 y perf 1280×720 PASS
  (447,6 fps medios). Ver `docs/FM_SECURITY_AI_ENCOUNTER.md`.

\\- Mezzanine de supervisión del Almacén (2026-11-16): IMPLEMENTADA. Se
  eligió la Opción C de la propuesta de verticalidad (mejor valor/coste) y
  se descartó el túnel inferior de ≈167 m. Plataforma de 6×6 m a cota 2,60
  con rampa de 1,5×5,2 m, barandilla, puesto de supervisión e iluminación.
  Arte: 99 objetos, 151.004 tris; GLB 20.577.408 bytes y 147.344 tris;
  escena 143 mallas, 84 colliders y 18 luces. Navegación con
  `NavLink_Mezzanine` de capa 1. QA PASS 0, smoke 412/0, gameplay 108/0,
  full 49/0, presets 194/0, alt routes 73/0 y perf 1280×720 PASS
  (482,9 fps medios). Ver `docs/FM_MEZZANINE_ART.md`.

\\- Primera pasada visual global (2026-11-16): APLICADA. Ajuste conservador
  del `WorldEnvironment` de `level1_v06.tscn`: niebla de profundidad
  (densidad 0,0025, color verde-azulado), niebla volumétrica 0,012 y
  corrección de color (contraste 1,06, saturación 1,10) manteniendo AgX,
  SSR, SSAO y glow. Sin cambios de geometría ni materiales. Smoke 412/0,
  gameplay 108/0, full 49/0, presets 194/0, alt routes 73/0 y perf
  1280×720 PASS (474,0 fps medios; coste ~1,8 %). Ver
  `docs/FM_GLOBAL_VISUAL_PASS.md`.

\\- Optimización medida (2026-11-16): APLICADA. Se corrigió la fusión
  estática de Seguridad (un `BoxMesh` con `surface_get_format` abortaba el
  merge del sector): ~2.408 → ~1.500 draw calls en `security_access`. Se
  limitaron 212 texturas 2K a 1024 px (VRAM 1.154,6 → 842,6 MB), se vistió el
  shell de pasillos, conectores y escaleras con materiales triplanar
  (`M_Shell_Wall`, `M_Shell_Floor`, `M_Shell_Ceiling`; 64 muros, 10 suelos y
  11 techos) y se añadió oclusión estática con los triángulos reales del shell
  (91 mallas, 1.092 tris), que baja `security_access` a 1.275 draws y 2,88 M
  primitivas. Después se consolidaron los materiales duplicados de Seguridad
  (`scripts/fm/fm_security_materials.gd`: 596 superficies remapeadas, 16
  materiales deduplicados, 710 materiales en escena), bajando la fusión de 393
  a 260 nodos y `security_access` a **1.127 draws** (−11,6 %) sin diferencia
  visual perceptible. Sin cambios de geometría ni GLB. Pruebas: smoke 412/0,
  gameplay 108/0, full 49/0, presets 194/0, alt routes 73/0 y perf 1280×720
  PASS (481,9–495,0 fps medios, mínimo 147,3, p99 4,44 ms; `security_access`
  313,9–322,5 fps). Ver `docs/FM_OPTIMIZATION_PASS.md`.

\\- Capturas finales de conjunto (2026-11-16): COMPLETADAS. Nuevo
  `tests/fm_level1_v06_final_shots.gd/.tscn` con cámara libre, lámpara hija y
  HUD oculto; 17 vistas a 1280×720 en `/tmp/opencode/final_godot_*.png` y
  contact sheet en `/tmp/opencode/final_godot_contact.png`. Documentación de
  cierre actualizada en `docs/FM_LEVEL1_V06_CLOSURE.md`.

\\- Sala técnica NWStair (2026-11-16): IMPLEMENTADA. Se cerró el fondo de
  saco de la meseta inferior con un espolón y una sala de 8×6 m a cota −4,5
  (Opción B; no se construyó el túnel de ≈167 m). Arte no narrativo con
  modelado realista: 17 objetos, 62.978 tris, GLB de 6.593.560 bytes, 20
  materiales y 21 imágenes; dos bombas centrífugas, cabeceras de agua/vapor,
  tres armarios eléctricos, bandeja de cables, banco con herramientas,
  extractor, desagüe y señalización funcional. QA aislada PASS 0 y con shell
  NWStair PASS 0. Integrada como `NwStairServiceArt` en
  `fm_alternate_routes.tscn`, con 5 luces y `ALT_ROUTES_BOUNDS` ampliado.
  Pruebas: smoke 412/0, alt routes 73/0, gameplay 108/0, full 49/0, presets
  194/0 y perf 1280×720 PASS (474,4 fps medios, p99 4,30 ms). Ver
  `docs/FM_NWSTAIR_SERVICE.md`.

\\- El Coleccionista — modelo esculpido (2026-11-16, APLAZADO). Se probaron
  las versiones procedurales v1–v4 sin alcanzar el realismo pedido. Hyper3D
  sigue sin fondos y no hay generador 3D por IA configurado. El usuario pidió
  dejar las criaturas para más adelante; los archivos
  `FM_COLLECTOR_V4.blend`, `collector_creature_v4.glb` y
  `scripts/fm_collector_v4.py` quedan como WIP sin integrar. Ver
  `docs/FM_COLLECTOR_SCULPT_STATUS.md`.

\\- El Imitador — modelo generado (2026-11-17, WIP). Se limpió y escaló el GLB
  generado a 2,23 m, se corrigieron pies y garras, se adelgazó el torso y se
  aplicaron UVs y materiales PBR. Pase de acercado a la referencia: piel
  marrón rojiza oscura con textura y roughness propias, torso más encorvado,
  cráneo estrechado/alargado y boca vertical. Los intentos de cuencas y de
  una cabeza nueva se revirtieron; los dientes postizos se eliminaron porque
  flotaban fuera de la cavidad. Malla final: 36.435 verts, 72.031 polys. GLB
  `assets/models/fm/imitator_generated_v5.glb` (3.491.352 bytes, 1 mesh,
  4 materiales, 3 imágenes, 72.851 tris, 0 cámaras/luces). QA
  `blender-asset-qa` PASS 0 errores / 3 warnings. No integrado en escena ni
  IA. El cráneo sigue siendo una cúpula lisa: para la referencia hace falta
  escultura/retopología manual. Ver `docs/FM_IMITATOR_GENERATED.md` y backup
  `docs/backups/FM_IMITATOR_MOUTH_CLEAN_2026-11-17/`.

\\- Modelo del jugador (2026-11-19): VERSIÓN CONSERVADORA 0,55. GLB fuente de
  `objetos-modelados/personaje-jugador/` escalado a 1,75 m, orientado a −Y y
  decimado con ratio 0,55 para conservar el aspecto original (239.186 tris,
  257.187 verts). Rig `PlayerRig` de 23 huesos, huesos `foot`/`toe`
  corregidos y binding proxy con 22 grupos, 0 sin peso y máximo 4
  influencias. Acciones `Player_Walk` (25 frames) y `Player_Idle` (48 frames).
  GLB `assets/models/fm/player_generated_v5.glb` (44.490.492 bytes, 1 mesh,
  1 skin, 23 joints, 2 animaciones, 239.186 tris, 0 cámaras/luces) y
  alternativa ligera `player_generated_v4.glb` (152.183 tris, 29 MB). Godot
  importa v5 con 1 malla, 23 huesos y las 2 animaciones. QA de malla con
  deuda de topología AI (UVs de área cero, winding, z-fighting); no es asset
  final, pero conserva el aspecto. No integrado en escena todavía. Ver
  `docs/FM_PLAYER_MODEL.md`.

\\- Jugador Nomad — rig preparado para animar (2026-11-20): COMPLETADO.
  `objetos-modelados/personaje-jugador/nomad_player/nomad_player_master.blend`
  conserva la malla, UVs, texturas y pesos originales (11.095 verts,
  14.996 tris, 70 grupos, 5 materiales), el rig de 70 huesos FK y las 10
  acciones. Se levantó el conjunto para que la rest quede en Z=0 y se
  ajustó cada acción para que su punto más bajo toque el suelo; las
  acciones quedaron autocontenidas (497 fcurvas) con fake user y NLA
  muteada. Bone collections Root/Spine/Arms/Hands/Fingers/Legs/Feet.
  Validación: firma de malla idéntica, Idle abierto con Z mín 0,000611 m,
  mínimos Z >= 0 en las 10 acciones y cambio de acción sin contaminación.
  Contact sheet: `docs/FM_NOMAD_PLAYER_RIG_CONTACT.png`. Limitaciones:
  solo FK (sin IK/controles), rest original no simétrica, sin brazos FP
  ni exportación a Godot. El antiguo `nomad_player_rig.blend` es un
  horneado defectuoso y no debe usarse. Ver `docs/FM_NOMAD_PLAYER_RIG.md`.

\\- Capa FP del jugador Nomad (2026-11-20): PROTOTIPO FUNCIONAL.
  `objetos-modelados/personaje-jugador/nomad_player/nomad_fp_player.blend`
  conserva la malla completa con la misma firma que el maestro (11.095 v,
  14.996 tris, UVs y texturas intactas). Añade 6 sockets no-deform
  (`socket_hand_r`, `socket_hand_l`, `socket_chest_radio`,
  `socket_chest_flashlight`, `socket_backpack`, `socket_camera`; armadura
  76 huesos, 70 deform), monta `linterna.glb` (escala 0,30) en
  `socket_hand_r` y `radio.glb` (escala 0,25) en `socket_chest_radio`, y
  crea `FP_Grip_Idle` 0–240 (710 fcurvas) con el puño de `Fight Excited`
  frame 104 y la linterna apuntada a (−0,1499,−0,9592,−0,2398). Capturas:
  `docs/FM_NOMAD_FP_BODY.png`, `docs/FM_NOMAD_FP_GRIP.png` y
  `docs/FM_NOMAD_FP_RADIO.png`. Limitación: la vista FP final no está
  cerrada; el brazo recortado produce tubo hueco/mano gigante/cuff
  facetado, hace falta un viewmodel de mano/guante dedicado. Ver
  `docs/FM_NOMAD_FP_LAYER.md`. Sin commit.

\\- Sistema de radio local (2026-11-17): IMPLEMENTADO. `scripts/fm/fm_radio.gd`
  añade PTT con V, cambio de canal con C (EQUIPO/SERVICIO/EMERGENCIA),
  batería propia, drenaje distinto al transmitir/escuchar, interferencia,
  calidad de señal, estática y pitidos sintetizados, y API para futuras
  transmisiones. Panel de radio en el HUD con canal, TX, batería y señal.
  Sin voz de red ni revelación de posiciones. Integrado en el jugador.
  Suministros (2026-11-17): 7 cargadores de radio (+40 %, cooldown 22 s),
  8 pilas comunes (+30 %) y 2 de alta capacidad (+70 %), 17 nodos en total,
  recogibles con E y sin colisión ni alteración de navmesh.
  Pruebas: radio 21/0, supplies 30/0, smoke 412/0, gameplay 108/0, full 49/0,
  presets 194/0, perf 1280×720 PASS (432,0 fps medios, mínimo 154,3,
  p99 4,48 ms). Ver `docs/FM_RADIO_SYSTEM.md`.

\\- Siguiente fase: sincronizar radio y suministros en multijugador, voz por
  proximidad/red con Opus y consentimiento, Imitador en radio y pruebas de
  red; o extracción dinámica y pase visual. Commit solo con autorización.

\\\\- Smoke/gameplay/full run/presets/alt routes/radio/supplies: 412/108/49/194/73/21/30 PASS tras el cambio.

\\\\- Sin commit hasta autorización del usuario.

\\\\## REGLAS PARA CONTINUAR

\\\\- Revisar el estado real del proyecto antes de modificarlo.

\\\\- Reutilizar escenas, materiales, iluminación y recursos de la Fase 2.

\\\\- No rehacer sistemas visuales que ya funcionan.

\\\\- No modificar \\\\\\\`fotos-referencia/\\\\\\\`.

\\\\- No introducir armas ni combate.

\\\\- Implementar y probar cada sistema secuencialmente.

\\\\- Documentar los cambios.

\\\\- Registrar errores y limitaciones.

\\\\- Medir el rendimiento cuando sea relevante.

\\\\- Actualizar esta sección cuando cambie el estado de desarrollo.

Si el estado real de los archivos contradice esta documentación,

inspecciona el proyecto y utiliza el estado comprobado como fuente de

verdad. Después actualiza esta sección.

\\---

\\\\# OBJETIVO FINAL

Crear FRECUENCIA MUERTA.

Un videojuego multijugador cooperativo de terror psicológico donde los

jugadores deben explorar instalaciones abandonadas, recuperar objetos

valiosos y escapar de criaturas inteligentes.

Sin armas.

Sin combate.

Sin héroes.

Solamente personas intentando sobrevivir.

Quiero escenarios 3D cinematográficos, iluminación espectacular,

criaturas memorables, físicas de objetos, cooperación, sigilo, audio

inmersivo y situaciones impredecibles.

El objetivo es crear una experiencia que los jugadores recuerden y

quieran volver a jugar con sus amigos.

\\------------------------------------------------------------------------

\\# 30. ESCALA MAESTRA, PROPORCIONES Y DIMENSIONES DE LAS INSTALACIONES

La arquitectura de FRECUENCIA MUERTA debe tener una escala creíble y coherente con los personajes, sus equipamientos, las cuatro criaturas y las funciones reales de cada espacio.

No construir instalaciones con dimensiones arbitrarias, excesivamente reducidas o elegidas únicamente por comodidad del modelado. Tampoco agrandar todo indiscriminadamente.

## 30.1. REFERENCIA OFICIAL DE ESCALA DE LAS CRIATURAS

La imagen `fotos-referencia/modelos-referencia` contiene los diseños conceptuales oficiales de las cuatro criaturas y muestra sus dimensiones de referencia. Es la fuente visual oficial para consultar las dimensiones de:

- El Imitador.
- El Vigilante.
- El Coleccionista.
- La Sombra.

Antes de diseñar, modelar, dimensionar o reorganizar la arquitectura de una instalación:

1. Localizar `modelos-referencia` dentro de `fotos-referencia/` y comprobar su extensión real. Es un archivo de imagen, no una carpeta.
2. Abrir y examinar la imagen completa, incluyendo las anotaciones y medidas escritas junto a cada criatura.
3. Transcribir literalmente las dimensiones indicadas para cada criatura, conservando sus unidades y cualquier distinción entre altura, anchura, longitud u otra medida que aparezca.
4. No estimar, redondear, sustituir ni inventar valores cuando la imagen ya proporciona una medida.
5. Si una anotación no es legible, indicarlo y solicitar una referencia legible; no completar el dato mediante suposiciones.
6. Utilizar esas medidas como referencia oficial de escala para la arquitectura, las puertas, los pasillos, las cámaras, los accesos y los espacios de maniobra.
7. Mantener intacta la imagen original. Está prohibido modificarla, eliminarla, renombrarla o sobrescribirla.

Las medidas escritas en `modelos-referencia` prevalecen sobre estimaciones visuales o valores inventados en otros documentos. Si posteriormente se aprueba un cambio de diseño de una criatura, actualizar la documentación de escala de forma explícita y conservar la trazabilidad del cambio.

## 30.2. ESCALA DE LOS PERSONAJES Y EQUIPAMIENTO

Inspeccionar los modelos reales de los trabajadores y determinar sus dimensiones, incluyendo cuando corresponda:

- Cuerpo y postura de pie.
- Casco y protección.
- Mochila y equipamiento transportado.
- Anchura ocupada durante el desplazamiento.
- Volumen de objetos que puedan cargar.
- Posturas de agacharse, arrastrarse, esconderse o auxiliar a otro jugador.

No asumir una altura o volumen humano sin comprobar los modelos y la escala del proyecto. Documentar las medidas obtenidas y utilizar una referencia humana consistente.

## 30.3. DIMENSIONAMIENTO ARQUITECTÓNICO

Las dimensiones de cada elemento deben responder a su función y a las necesidades reales de los personajes y criaturas. Evaluar, como mínimo:

- Altura, anchura y sentido de apertura de las puertas.
- Altura libre de techos y pasos.
- Anchura y altura de pasillos.
- Espacio para girar, maniobrar y cruzarse.
- Escaleras, rampas, ascensores y plataformas.
- Accesos de mantenimiento y transporte.
- Espacios de trabajo alrededor de maquinaria.
- Volumen de mobiliario, equipos y objetos interactivos.
- Espacios requeridos por animaciones, colisiones y navegación.
- Espacios para persecuciones, encuentros, escondites y cooperación.

No reducir una habitación al espacio mínimo necesario para colocar sus objetos. Debe permitir que los jugadores se desplacen, observen, se escondan, cooperen y manipulen elementos sin que la arquitectura interfiera artificialmente.

Las criaturas deben disponer del espacio que requieran sus dimensiones y sus animaciones. Una criatura puede no caber por una puerta o pasillo como decisión deliberada de diseño, pero esa limitación debe ser intencional, estar documentada y formar parte de la jugabilidad; nunca debe ser consecuencia accidental de una mala escala.

## 30.4. VARIEDAD DE ESCALAS Y VOLUMETRÍA

No todas las habitaciones deben ser grandes ni tener proporciones similares. Combinar de forma justificada:

- Espacios pequeños, estrechos y claustrofóbicos.
- Habitaciones de tamaño medio.
- Laboratorios amplios.
- Cámaras industriales y de contención de gran volumen.
- Espacios verticales y de doble altura.
- Cámaras centrales monumentales.
- Pasillos secundarios, corredores principales y galerías industriales.
- Espacios técnicos reducidos cuando su función lo justifique.
- Áreas abiertas que generen vulnerabilidad.

La variedad debe tener una justificación funcional, arquitectónica, narrativa y jugable. No agrandar todas las habitaciones ni reducirlas para aumentar artificialmente el número de espacios.

## 30.5. ESCALA GENERAL DE LAS INSTALACIONES

La superficie total, el número de habitaciones y la cantidad de niveles deben responder a:

- Duración prevista de las misiones.
- Cantidad de jugadores.
- Complejidad de objetivos.
- Distribución funcional de departamentos.
- Necesidades de exploración y navegación.
- Variedad de rutas y posibilidades de orientación.
- Presencia, dimensiones y movilidad de las criaturas.
- Rendimiento del juego.

Los rangos de superficie y cantidad de habitaciones que aparecen en esta sección son referencias iniciales, no límites obligatorios. No deben forzar una distribución artificial ni justificar espacios vacíos. La superficie debe representar áreas realmente explorables y funcionales.

## 30.6. VALIDACIÓN DE ESCALA

Antes de aprobar una instalación, comprobar visual y técnicamente:

- Proporciones entre jugadores, equipamiento, puertas, mobiliario y arquitectura.
- Proporciones entre cada criatura y los jugadores.
- Compatibilidad de puertas, pasillos y accesos con las dimensiones oficiales de cada criatura.
- Espacios de giro, navegación y ejecución de animaciones.
- Colisiones y posibles penetraciones de geometría.
- Circulación de jugadores y transporte de objetos.
- Espacios adecuados para persecuciones, escondites y encuentros.
- Coherencia de la escala general con una instalación real.

Utilizar comparativas visuales, mediciones de escena y pruebas de navegación. No considerar terminada una instalación únicamente porque sus objetos estén colocados.

\\# 31. DENSIDAD, VARIEDAD Y DIMENSIONES FUNCIONALES DE LAS HABITACIONES

Los escenarios deben sentirse como instalaciones reales que tuvieron una función antes del incidente. No crear mapas extensos compuestos por habitaciones vacías, repetidas, genéricas o excesivamente pequeñas.

Cada habitación debe tener una función reconocible, una composición visual propia y elementos coherentes con su uso.

## 31.1. TIPOS DE ESPACIOS

Incluir, según la naturaleza de cada instalación:

- Laboratorios biológicos, químicos y genéticos.
- Salas de experimentación.
- Quirófanos y salas de procedimientos.
- Morgues y cámaras frigoríficas.
- Cámaras de contención.
- Oficinas y despachos.
- Habitaciones y vestuarios del personal.
- Salas de servidores y control.
- Almacenes y depósitos.
- Salas eléctricas y de mantenimiento.
- Zonas de descontaminación.
- Archivos y salas de documentación.
- Áreas de descanso y cafeterías.
- Cuartos de limpieza y almacenamiento.
- Salas de comunicaciones.
- Áreas de recepción y transporte de suministros.
- Cámaras técnicas y espacios de infraestructura.

La selección debe responder al tipo, historia y necesidades de cada instalación. No es obligatorio incorporar todos los tipos de habitaciones en todos los mapas.

## 31.2. DIMENSIONES SEGÚN SU FUNCIÓN

No establecer dimensiones universales ni medidas fijas para cada categoría de habitación. Cada espacio debe dimensionarse después de determinar:

- Su función y capacidad prevista.
- La cantidad de personas que puede albergar.
- Los equipos y maquinaria que necesita.
- El mobiliario y las zonas de trabajo.
- Las áreas de circulación y maniobra.
- Los accesos, salidas y rutas de evacuación.
- Los requisitos de mantenimiento y seguridad.
- Las conexiones con otros departamentos.
- Las dimensiones de los personajes y criaturas cuando corresponda.

Un laboratorio debe disponer de espacio para equipos, preparación, análisis, almacenamiento y circulación. Una sala de generadores debe alojar la maquinaria, cuadros eléctricos, ventilación y accesos de mantenimiento. Una cámara de contención debe considerar el volumen del elemento contenido, observación, controles, accesos de seguridad y zonas de operación. Un quirófano debe permitir la disposición del equipamiento, camilla, personal y circulación.

No reducir una habitación a una caja vacía que apenas contiene sus objetos principales. Tampoco sobredimensionarla sin una razón funcional.

## 31.3. DENSIDAD Y COMPOSICIÓN VISUAL

La variedad debe surgir de combinar:

- Arquitectura y distribución espacial.
- Mobiliario y equipamiento.
- Maquinaria e instalaciones técnicas.
- Iluminación y materiales.
- Deterioro, suciedad y daños.
- Objetos interactivos y recuperables.
- Elementos narrativos y señales de uso anterior.

Cada habitación importante debe contar parte de la historia mediante su composición, objetos, daños, iluminación y distribución. Evitar llenar habitaciones con objetos aleatorios únicamente para aparentar mayor detalle. La decoración debe responder a su función original y a los acontecimientos del incidente.

## 31.4. RELACIÓN ENTRE ESPACIOS Y CRIATURAS

La arquitectura debe considerar la presencia de las criaturas desde la planificación. Evaluar para cada criatura:

- Si puede recorrer los pasillos y atravesar los accesos previstos.
- Si puede girar y maniobrar según su anatomía.
- Si puede entrar en determinadas habitaciones.
- Si puede utilizar los espacios verticales previstos.
- Si puede ejecutar sus animaciones sin atravesar geometría.
- Si puede interactuar con elementos del escenario.
- Si puede perseguir a los jugadores sin bloqueos accidentales.
- Si existen espacios donde su tamaño limite intencionalmente su movimiento.

Las restricciones de movilidad pueden utilizarse como mecánica de terror siempre que sean intencionales. No diseñar toda la arquitectura exclusivamente alrededor de la criatura más grande: conservar variedad espacial y permitir que cada criatura tenga comportamientos y ventajas diferentes.

## 31.5. VALIDACIÓN

Antes de aprobar una habitación, comprobar su función, escala, circulación, equipamiento, conexiones, composición visual y compatibilidad con los personajes y criaturas que puedan acceder a ella.

No considerar terminada una habitación únicamente porque tenga paredes, suelo, techo y algunos objetos.

\\# 32. OBJETOS, SAQUEO Y RECUPERACIÓN

Diferenciar claramente las categorías de objetos del mundo:

1. Objetos decorativos: enriquecen visualmente el escenario.
2. Objetos interactivos: permiten abrir, activar, mover, consultar o manipular elementos.
3. Objetos recuperables: pueden transportarse y entregarse para obtener recompensas.
4. Objetos de misión: son necesarios para cumplir objetivos específicos.
5. Objetos especiales: tienen propiedades, riesgos o valor narrativo particulares.

Los objetos recuperables pueden tener:

- Valor económico y rareza.
- Peso y volumen.
- Fragilidad y estado de conservación.
- Física e interacción.
- Sonidos al recogerlos, soltarlos, manipularlos o transportarlos.
- Requisitos de manipulación.
- Posibles efectos secundarios.
- Posibilidad de desmontaje y componentes recuperables.
- Necesidad de cooperación cuando el tamaño, peso o procedimiento lo justifique.

La selección y colocación de objetos debe respetar la función de cada habitación. Un laboratorio debe contener material científico; una morgue, equipamiento médico y elementos propios de esa zona.

No convertir todos los elementos del escenario en objetos recogibles o desmontables. La interactividad debe tener un propósito y mantenerse dentro del presupuesto de rendimiento.

## 32.1. CLASIFICACIÓN SEGÚN TAMAÑO Y TRANSPORTE

**Objetos pequeños**

- Pueden guardarse en el inventario o bolso, según su tamaño y las reglas de capacidad.
- Deben respetar los límites de espacio y peso.
- Normalmente no afectan significativamente la movilidad.

**Objetos medianos**

- Generalmente se transportan con las manos.
- Pueden ocupar las manos e impedir determinadas interacciones.
- Su peso o volumen puede afectar la movilidad.

**Objetos grandes**

- Ocupan un espacio considerable y no deben tratarse automáticamente como objetos que simplemente se cargan o arrastran.
- Algunos pueden desmontarse para recuperar componentes individuales.
- Otros pueden ser indivisibles, estar sellados o no ofrecer componentes recuperables.
- Si no pueden desmontarse, su transporte puede requerir una solución especial o cooperación entre jugadores, cuando esté justificado por su diseño.

La clasificación debe basarse en las dimensiones, el peso, la forma, la fragilidad y la función del objeto, no únicamente en una etiqueta arbitraria.

## 32.2. DESMONTAJE Y RECUPERACIÓN DE COMPONENTES

Algunos objetos grandes deben permitir desmontarse para recuperar piezas importantes, valiosas o útiles. Esta mecánica ofrece una alternativa al transporte del objeto completo.

Ejemplos de objetos que podrían ser desmontables, según su diseño:

- Equipos científicos.
- Computadores industriales.
- Generadores.
- Equipamiento médico.
- Maquinaria especializada.
- Sistemas electrónicos y de telecomunicaciones.

Cada objeto desmontable debe tener una estructura de componentes definida. Puede incluir componentes principales, secundarios, comunes, valiosos, frágiles o vinculados a objetivos de misión.

No todos los componentes tienen que ofrecer una recompensa económica. Algunos pueden servir para completar objetivos, reparar sistemas, desbloquear información o aportar contexto narrativo.

El jugador debe poder reconocer qué partes son manipulables o recuperables mediante señales visuales, etiquetas, inspección o interacción. No es necesario revelar siempre el valor exacto de cada componente.

No todos los objetos deben poder desmontarse. Algunos pueden estar sellados, dañados, protegidos, ser de una sola pieza o requerir herramientas y procedimientos que no estén disponibles en esa misión.

## 32.3. REGLAS DEL DESMONTAJE

El desmontaje debe:

- Requerir una interacción específica y comprensible.
- Poder necesitar herramientas determinadas.
- Tener una duración relacionada con la complejidad del objeto y la herramienta utilizada.
- Generar sonidos durante el procedimiento.
- Poder producir ruido adicional si una pieza cae, se rompe o se manipula incorrectamente.
- Permitir recuperar componentes de forma individual.
- Considerar el peso, volumen y fragilidad de cada componente.
- Respetar la capacidad del inventario y las limitaciones de transporte.
- Poder interrumpirse si aparece una amenaza o el jugador decide abandonar el procedimiento.

El desmontaje no debe ser instantáneo ni completamente silencioso. Tampoco debe convertirse en una secuencia larga y tediosa sin decisiones interesantes.

Los procedimientos pueden variar según el objeto. No todos deben utilizar las mismas herramientas, animaciones, duración o secuencia de interacción.

## 32.4. RIESGO, RUIDO Y DECISIONES

El desmontaje debe crear una decisión de riesgo y recompensa. El equipo debe valorar si el valor de los componentes justifica el tiempo y el ruido necesarios para obtenerlos.

Considerar, según el objeto:

- Ruido de herramientas y mecanismos.
- Golpes, vibraciones y piezas que se desprenden.
- Componentes que caen al suelo.
- Piezas frágiles que pueden romperse.
- Mecanismos que pueden activarse accidentalmente.
- Sistemas eléctricos o de presión que pueden producir efectos adicionales.
- Tiempo de exposición durante el procedimiento.
- Posibilidad de atraer criaturas cercanas.

No todos los desmontajes deben generar el mismo nivel de ruido. La intensidad y duración deben depender del material, la herramienta, la acción, el estado del objeto y el entorno.

El jugador debe poder detener o abandonar el desmontaje cuando detecte peligro. Las criaturas deben reaccionar según sus capacidades de percepción y el sistema de propagación sonora, no mediante una detección global e infalible.

## 32.5. RECUPERACIÓN Y TRANSPORTE DE COMPONENTES

Una vez separados, los componentes recuperables se comportan como objetos independientes y deben poder recogerse, soltarse, transportarse y entregarse.

Su peso y volumen determinan si pueden guardarse en el inventario, llevarse en las manos o si requieren una solución de transporte especial.

Los componentes voluminosos o pesados pueden requerir cooperación entre jugadores cuando su diseño lo justifique. La cooperación también puede intervenir durante el desmontaje de maquinaria compleja, sin convertir todos los procedimientos en tareas obligatoriamente cooperativas.

El desmontaje no debe ser siempre más rentable que recuperar un objeto intacto. El valor de sus componentes debe equilibrarse con el valor del objeto completo, el tiempo invertido, el riesgo y el espacio de transporte.

Un mismo objeto no debe generar recompensas duplicadas por entregarse completo y también por entregar sus componentes. La lógica de recompensa debe reconocer una única recuperación válida o una combinación expresamente definida.

No asumir que todo componente separado cuenta automáticamente como recuperado: debe llegar a la zona y cumplir las reglas de entrega y extracción que se definan para la misión.

\\# 33. DESTRUCCIÓN Y DETERIORO AMBIENTAL

Las instalaciones deben mostrar daños y deterioro variados, coherentes

con el incidente y con el paso del tiempo.

Distinguir entre destrucción ambiental, destrucción accidental y desmontaje recuperable. La destrucción ambiental representa el deterioro del escenario; la destrucción accidental puede ser causada por jugadores, criaturas o eventos; el desmontaje recuperable es un procedimiento intencional para separar componentes de un objeto y obtener recursos. Romper un objeto no implica que sus piezas puedan recuperarse ni que otorguen recompensas. El desmontaje recuperable se rige por la sección 32.

Incluir cuando corresponda:

\\- Muebles volcados o destruidos.

\\- Estanterías caídas.

\\- Cristales rotos.

\\- Equipos médicos y científicos dañados.

\\- Computadores y monitores destruidos.

\\- Puertas deformadas o bloqueadas.

\\- Tuberías rotas y fugas.

\\- Cables colgando.

\\- Paneles eléctricos dañados.

\\- Escombros y fragmentos de estructuras.

\\- Techos deteriorados y revestimientos desprendidos.

\\- Señales de impactos, incendios o inundaciones.

No todas las habitaciones deben presentar el mismo nivel de destrucción.

Alternar espacios relativamente intactos, zonas abandonadas, áreas

dañadas y escenas de destrucción extrema.

La destrucción debe contribuir a la historia, la navegación o la

jugabilidad siempre que sea posible.

\\------------------------------------------------------------------------

\\# 34. SANGRE, CADÁVERES Y RESTOS HUMANOS

El horror ambiental debe representar visualmente las consecuencias del

incidente.

Se pueden incluir, según la historia y el contexto de cada habitación:

\\- Cadáveres completos en distintas posiciones.

\\- Cuerpos parcialmente ocultos, atrapados o arrastrados.

\\- Extremidades amputadas y restos humanos, como manos, brazos y

&#x20; piernas.

\\- Camillas con cuerpos cubiertos o abandonados.

\\- Bolsas para cadáveres abiertas, dañadas o abandonadas.

\\- Restos en quirófanos, morgues, laboratorios y zonas de contención.

\\- Charcos, manchas y salpicaduras de sangre.

\\- Huellas de manos ensangrentadas en paredes, puertas y cristales.

\\- Rastros de sangre que indiquen desplazamientos o arrastres.

\\- Señales de experimentos fallidos, accidentes y contaminación

&#x20; biológica.

La sangre, los cuerpos y los restos deben estar integrados en escenas

con sentido narrativo. No distribuirlos aleatoriamente ni llenar todas

las habitaciones con el mismo nivel de violencia.

Utilizar el contraste: algunas zonas pueden mostrar una catástrofe

evidente, otras una evacuación interrumpida y otras una normalidad

inquietante.

Cuando sea viable, los cuerpos y determinados restos podrán tener

interacción física limitada. Esta interacción debe ser coherente y no

comprometer el rendimiento.

\\------------------------------------------------------------------------

\\# 35. TRAMPAS AMBIENTALES Y PELIGROS PARA LOS JUGADORES

Las instalaciones deben contener peligros y trampas ambientales que

puedan perjudicar a los jugadores, generar ruido, revelar su posición,

separar al equipo o atraer criaturas.

Estas trampas NO son herramientas para capturar o eliminar criaturas.

Son peligros del entorno que los jugadores deben aprender a reconocer y

evitar.

\\## TRAMPAS SONORAS

Incluir mecanismos que generen ruido cuando un jugador los active

accidentalmente:

\\- Latas, botellas y objetos metálicos colocados de forma inestable.

\\- Cristales rotos que producen ruido al pisarlos.

\\- Cables que hacen caer objetos suspendidos.

\\- Alarmas conectadas a puertas, sensores o mecanismos.

\\- Suelos con piezas metálicas sueltas.

\\- Objetos que caen al tocar muebles o estructuras.

\\- Mecanismos que producen golpes, vibraciones o sonidos fuertes.

\\## TRAMPAS FÍSICAS

Incluir peligros como:

\\- Cables y alambres a la altura de los pies.

\\- Placas de presión que activan mecanismos.

\\- Suelos debilitados que pueden romperse.

\\- Estanterías inestables que pueden caer.

\\- Puertas que se cierran automáticamente.

\\- Estructuras o elementos del techo que pueden desprenderse.

\\- Accesos que pueden bloquearse al activar un mecanismo.

\\## PELIGROS AMBIENTALES

Incluir, cuando corresponda:

\\- Fugas de gas.

\\- Zonas electrificadas.

\\- Charcos de sustancias químicas.

\\- Tuberías que liberan vapor o presión.

\\- Suelos contaminados o peligrosos.

\\- Zonas con visibilidad reducida.

\\- Sistemas eléctricos defectuosos.

\\- Áreas que requieren protección o herramientas específicas.

\\## TRAMPAS DE ENGAÑO Y TENSIÓN

Se pueden utilizar elementos aparentemente normales que provoquen

situaciones inesperadas:

\\- Luces que se encienden al entrar en una habitación.

\\- Puertas que producen sonidos repentinos.

\\- Maniquíes, cuerpos u objetos suspendidos que caen.

\\- Señuelos sonoros que se confunden con sonidos de compañeros o

&#x20; criaturas.

\\- Mecanismos que activan alarmas o maquinaria.

\\## DETECCIÓN Y CONTRAJUEGO

\\- Algunas trampas deben poder detectarse mediante observación y

&#x20; atención.

\\- Otras pueden requerir herramientas para inspeccionarse o

&#x20; desactivarse.

\\- Los jugadores deben poder evitarlas o encontrar rutas alternativas

&#x20; cuando sea razonable.

\\- Algunas trampas pueden activarse durante una persecución y aumentar

&#x20; el peligro.

\\- Los sonidos generados deben integrarse con el sistema de percepción

&#x20; de las criaturas.

\\- Las consecuencias deben ser comprensibles y evitar muertes

&#x20; inevitables o situaciones injustas.

Las trampas deben estar integradas en la arquitectura y tener sentido

dentro de la historia de la instalación.

\\------------------------------------------------------------------------

\\# 36. NARRATIVA AMBIENTAL

Los escenarios deben contar historias sin depender exclusivamente de

documentos o diálogos.

Cada habitación importante debe comunicar algo mediante su composición,

objetos, daños, iluminación, cuerpos, sangre y distribución de

elementos.

Ejemplos:

\\- Un laboratorio donde un experimento salió mal.

\\- Un quirófano donde una operación fue interrumpida.

\\- Una oficina con documentos abandonados durante una evacuación.

\\- Una cámara de contención destruida desde dentro.

\\- Una habitación aparentemente intacta en medio de una instalación

&#x20; devastada.

\\- Un pasillo con rastros que indiquen que alguien intentó escapar.

\\- Una sala de control donde se intentó contener el incidente.

Evitar colocar elementos narrativos sin relación entre sí. La escena

debe permitir que el jugador interprete lo ocurrido mediante la

observación.

\\------------------------------------------------------------------------

\\# 37. VARIABILIDAD Y REJUGABILIDAD DE LOS ESCENARIOS

Las instalaciones deben ofrecer situaciones diferentes entre partidas

sin perder coherencia arquitectónica.

Cuando sea técnicamente viable, variar:

\\- Ubicación de objetos recuperables.

\\- Contenedores y recursos disponibles.

\\- Puertas bloqueadas o desbloqueadas.

\\- Rutas accesibles.

\\- Zonas derrumbadas.

\\- Iluminación y sistemas eléctricos.

\\- Determinados eventos ambientales.

\\- Presencia y ubicación inicial de criaturas.

\\- Accesos secundarios y zonas restringidas.

La arquitectura principal debe mantener una estructura comprensible. La

variabilidad no debe generar habitaciones inaccesibles, objetos fuera

del mapa, rutas imposibles ni distribuciones incoherentes.

Priorizar escenarios diseñados manualmente con variaciones controladas

antes que generación procedural indiscriminada.

\\------------------------------------------------------------------------

\\# 38. EVENTOS DINÁMICOS DE LAS INSTALACIONES

Las instalaciones deben poder experimentar eventos durante una misión.

Ejemplos:

\\- Cortes eléctricos.

\\- Alarmas de seguridad.

\\- Fallos de ventilación.

\\- Puertas que se bloquean.

\\- Fugas de gas o vapor.

\\- Activación de maquinaria.

\\- Fallos de sistemas de contención.

\\- Interrupciones de comunicaciones.

\\- Ruidos inexplicables.

\\- Sistemas de emergencia que se activan.

\\- Cambios en la iluminación de determinadas zonas.

Los eventos deben tener consecuencias jugables y ambientales. No deben

ser simples efectos visuales sin impacto.

No todos los eventos deben ocurrir en cada partida. Su frecuencia,

duración y consecuencias deben equilibrarse para generar variedad sin

frustrar al jugador.

\\------------------------------------------------------------------------

\\# 39. INTERACCIÓN FÍSICA CON EL ENTORNO

El mundo debe sentirse tangible y reaccionar a las acciones de los

jugadores.

Determinar qué elementos pueden:

\\- Caerse.

\\- Romperse.

\\- Desplazarse.

\\- Abrirse y cerrarse.

\\- Activarse y desactivarse.

\\- Generar ruido.

\\- Bloquear caminos.

\\- Alterar la iluminación.

\\- Provocar otros eventos.

No todos los elementos decorativos necesitan física completa. Priorizar

la interacción física en objetos importantes para la jugabilidad, la

narrativa y las situaciones de peligro.

Las interacciones deben integrarse con los sistemas de sonido,

detección, físicas y multijugador.

\\------------------------------------------------------------------------

\\# 40. INTELIGENCIA DE LAS CRIATURAS FRENTE AL ENTORNO

Las criaturas deben reaccionar al entorno y a las consecuencias de las

acciones de los jugadores.

Según sus características individuales, podrán investigar o reaccionar

ante:

\\- Alarmas.

\\- Trampas sonoras.

\\- Cristales rotos.

\\- Objetos que caen.

\\- Puertas abiertas o cerradas.

\\- Obstáculos desplazados.

\\- Luces que se encienden o apagan.

\\- Maquinaria activada.

\\- Jugadores que transportan objetos ruidosos.

\\- Rastros y señales ambientales cuando tenga sentido para su

&#x20; comportamiento.

No todas las criaturas deben reaccionar igual. Cada una debe conservar

su identidad, sus sentidos, sus limitaciones y sus patrones de

comportamiento.

No implementar una inteligencia artificial universal que haga que todas

las criaturas persigan cualquier sonido de la misma manera.

\\------------------------------------------------------------------------

\\# 41. CONSTRUCCIÓN MODULAR Y RENDIMIENTO DE ESCENARIOS

Los escenarios grandes y densos deben construirse con una arquitectura

modular y optimizada.

Priorizar:

\\- Habitaciones y módulos reutilizables.

\\- Elementos arquitectónicos modulares.

\\- Instancing para objetos repetidos.

\\- LOD para geometría y recursos apropiados.

\\- Occlusion culling.

\\- Gestión eficiente de materiales y texturas.

\\- Uso controlado de luces dinámicas y sombras.

\\- Gestión de partículas y efectos volumétricos.

\\- Física selectiva para objetos interactivos.

\\- Carga y descarga de recursos cuando sea necesario.

No reducir indiscriminadamente la densidad visual para mejorar el

rendimiento. Optimizar mediante mediciones y decisiones técnicas

justificadas.

Las escenas deben probarse con condiciones representativas: geometría,

iluminación, objetos, físicas, partículas, criaturas y jugadores cuando

esos sistemas estén disponibles.

\\------------------------------------------------------------------------

\\# 42. REGLAS DE IMPLEMENTACIÓN DE ESCENARIOS POR FASES

No construir una instalación completa de decenas de habitaciones antes

de validar los sistemas principales.

La vertical slice debe demostrar una muestra representativa de:

\\- Un corredor y varias habitaciones con identidades distintas.

\\- Objetos decorativos e interactivos.

\\- Al menos un objeto recuperable.

\\- Una muestra de deterioro y destrucción ambiental.

\\- Sangre, cadáveres o restos cuando corresponda a la escena.

\\- Una trampa ambiental que pueda generar ruido.

\\- Una criatura que reaccione a los sonidos.

\\- Un escondite funcional.

\\- Un recorrido de recuperación y extracción.

Después de validar el ciclo básico, ampliar progresivamente la cantidad

de habitaciones, sectores, objetos, trampas, eventos y variantes.

No implementar todos los sistemas simultáneamente. Cada ampliación debe

tener criterios de aceptación y pruebas.

\\------------------------------------------------------------------------

\\# 43. SISTEMA DE HERIDAS Y AUXILIO ENTRE JUGADORES

El daño recibido debe tener consecuencias jugables sin convertir el

videojuego en un sistema de combate.

Definir estados y efectos como:

\\- Heridas que afectan temporalmente la movilidad.

\\- Cojera o dificultad para correr.

\\- Visión o audición alteradas por determinados efectos.

\\- Aturdimiento.

\\- Incapacitación.

\\- Necesidad de asistencia de otro jugador.

Los compañeros deben poder ayudar a un jugador herido o incapacitado

mediante interacciones y herramientas apropiadas.

El sistema debe distinguir entre daño, incapacitación y muerte. Sus

reglas deben ser claras y equilibradas.

No permitir que las heridas se conviertan en una excusa para quitar

arbitrariamente el control al jugador durante periodos excesivos.

La implementación debe integrarse con las animaciones, el estado físico,

el inventario, la extracción y la futura sincronización multijugador.

\\------------------------------------------------------------------------

\\# 44. SISTEMA DE RECURSOS, EQUIPAMIENTO Y HERRAMIENTAS

El equipamiento debe ofrecer decisiones y compromisos. Los jugadores no

deben poder llevar todas las herramientas sin limitaciones.

Definir:

\\- Espacios de inventario.

\\- Capacidad de transporte.

\\- Peso y volumen.

\\- Baterías y consumibles.

\\- Durabilidad cuando corresponda.

\\- Herramientas que requieren preparación.

\\- Herramientas que pueden compartirse.

\\- Recursos que pueden encontrarse dentro de las instalaciones.

\\- Compatibilidad entre herramientas y objetivos.

Las herramientas deben tener funciones diferenciadas y limitaciones

reales.

La gestión del equipamiento debe fomentar la cooperación y la

planificación antes de entrar en una misión.

No convertir las herramientas en armas ni permitir que sustituyan el

sigilo y la estrategia.

\\------------------------------------------------------------------------

\\# 45. EXTRACCIÓN, FRACASO Y CONSECUENCIAS DE LA MISIÓN

La extracción debe tener reglas claras y consecuencias que den importancia a las decisiones del equipo.

## 45.1. UBICACIÓN ESTABLECIDA

La zona de recepción, ubicada en el nivel 1 de la instalación, es el punto establecido para la extracción y la entrega del botín recuperado.

La arquitectura, las rutas y las conexiones entre niveles deben considerar que los jugadores necesitarán regresar a recepción transportando los objetos y componentes que hayan decidido recuperar.

La recepción debe tener una función reconocible dentro del flujo de extracción y no ser tratada como una habitación decorativa cualquiera.

La ubicación está establecida, pero los detalles operativos de la extracción —activación, dispositivo o vehículo, duración, secuencia de entrega, condiciones de éxito y tratamiento de jugadores u objetos que no lleguen— deben definirse expresamente antes de implementarse. No inventar esos detalles ni asumir que depositar un objeto equivale por sí solo a completar la extracción.

## 45.2. REGLAS QUE DEBEN DEFINIRSE

Definir:

- Condiciones para activar la extracción.
- Funcionamiento concreto del punto de extracción en recepción.
- Tiempo necesario para completar una extracción.
- Riesgos durante la espera y durante el procedimiento.
- Procedimiento para entregar objetos completos y componentes desmontados.
- Qué objetos y componentes cuentan como recuperados.
- Consecuencias de abandonar objetos o componentes.
- Qué ocurre cuando un jugador queda incapacitado o no llega al punto de extracción.
- Qué ocurre cuando un jugador muere.
- Reglas de recuperación o pérdida de objetos y recompensas.
- Resultados individuales y colectivos de la misión.

El equipo debe poder decidir si continúa explorando o si se retira con lo que ya consiguió.

El fracaso debe tener consecuencias comprensibles, pero no debe castigar de manera desproporcionada ni hacer que perder una partida resulte inútil.

La extracción debe ser una situación jugable y tensa, no simplemente una pantalla que aparece al terminar el recorrido.

Los objetos recuperables y los componentes desmontados deben seguir una lógica de recompensa coherente. Evitar duplicar el valor de un objeto por contabilizar simultáneamente el objeto completo y las piezas extraídas.

\\# 46. SISTEMA DE SONIDO AVANZADO Y PROPAGACIÓN DEL RUIDO

El sonido debe ser uno de los sistemas centrales de jugabilidad y terror.

No tratar todos los sonidos como eventos globales con el mismo alcance.

Cuando sea técnicamente viable, considerar:

- Distancia de propagación.
- Atenuación por distancia.
- Obstáculos y paredes.
- Puertas abiertas o cerradas.
- Diferentes materiales y superficies.
- Pisadas según el material.
- Ruido al correr, caminar o agacharse.
- Ruido de objetos al caer, manipularse o transportarse.
- Sonidos de herramientas y procedimientos de desmontaje.
- Golpes, vibraciones, mecanismos y piezas que se desprenden durante el desmontaje.
- Sonidos de mecanismos y trampas.
- Reverberación según el tipo de habitación.
- Interferencias y distorsiones.
- Audio posicional 3D.

El desmontaje de objetos grandes debe integrarse como una fuente de eventos sonoros. El nivel, duración y características del ruido deben depender del objeto, el material, la herramienta, la acción, el estado del objeto y el entorno.

Diferenciar, cuando corresponda, entre el sonido continuo de una herramienta, golpes puntuales, una pieza que cae, una rotura y la activación accidental de un mecanismo. Estos eventos no tienen por qué compartir intensidad, duración ni alcance.

Las criaturas deben recibir información sonora de acuerdo con sus capacidades de percepción. No todas deben detectar los mismos sonidos ni a la misma distancia.

El sistema debe distinguir entre sonidos producidos por jugadores, sonidos ambientales, eventos de la instalación y sonidos falsos del Imitador.

La voz falsa debe poder integrarse con el sistema de comunicación por proximidad y las grabaciones autorizadas de los jugadores, respetando siempre el consentimiento y la privacidad.

Evitar que el sonido revele información injusta o que permita identificar automáticamente todos los peligros.

\\# 47. PLANIFICACIÓN ARQUITECTÓNICA, DISTRIBUCIÓN FUNCIONAL Y NIVELES

La arquitectura de cada instalación debe responder a una planificación funcional, operativa, espacial y narrativa. No distribuir habitaciones arbitrariamente ni colocar departamentos donde simplemente exista espacio disponible.

Una instalación debe parecer diseñada por una organización que tenía necesidades reales de operación, investigación, seguridad, almacenamiento, mantenimiento, transporte y evacuación.

## 47.1. ZONIFICACIÓN FUNCIONAL

Identificar y clasificar los espacios según su función. Considerar, cuando corresponda:

- Acceso, recepción y control de visitantes.
- Administración.
- Seguridad, vigilancia y control de acceso.
- Investigación científica y laboratorios especializados.
- Experimentación.
- Áreas médicas, quirófanos y procedimientos.
- Morgues y almacenamiento biológico.
- Contención y aislamiento.
- Almacenamiento, logística y recepción de suministros.
- Mantenimiento y servicios técnicos.
- Energía e infraestructura.
- Servidores y telecomunicaciones.
- Descanso y servicios del personal.
- Archivos y documentación.
- Zonas restringidas, técnicas y de emergencia.

No es obligatorio incorporar todas estas áreas en todos los niveles ni en todas las instalaciones. La selección y distribución deben responder a la identidad, historia y operación del lugar.

## 47.2. DISTRIBUCIÓN ENTRE NIVELES

Los niveles deben organizarse según la función de los departamentos, sus relaciones, las necesidades de circulación y la lógica operativa de la instalación.

No asumir que todos los niveles deben tener la misma cantidad de habitaciones, superficie o distribución. No asignar departamentos automáticamente para completar cada planta.

Al planificar cada nivel, considerar:

- Relaciones funcionales entre departamentos.
- Proximidad a accesos y salidas.
- Necesidades de seguridad y restricción.
- Transporte de suministros, equipos y muestras.
- Circulación del personal.
- Requisitos de mantenimiento.
- Conexiones verticales y horizontales.
- Evacuación y respuesta ante emergencias.
- Narrativa e historia del complejo.

La organización puede utilizar niveles subterráneos, sectores desplazados horizontal o verticalmente, cámaras de gran altura, espacios que atraviesen varios niveles, pasarelas, túneles, pozos, plataformas y áreas técnicas.

No es obligatorio organizar todo en cinco plantas horizontales convencionales. Pueden existir niveles parciales, sectores a diferentes cotas, cámaras de doble altura y conexiones verticales, siempre que la arquitectura sea comprensible y funcional.

Cada nivel debe tener una identidad funcional reconocible, pero no debe convertirse en un compartimento aislado del resto de la instalación.

La recepción del nivel 1 es la zona establecida para la extracción y entrega del botín. La planificación debe considerar rutas de regreso desde los distintos sectores hasta recepción.

Las circulaciones deben contemplar el transporte de objetos completos que no puedan desmontarse y de componentes recuperados. Considerar las dimensiones de puertas, pasillos, escaleras, rampas y ascensores según los objetos que realmente puedan encontrarse en cada sector.

No es necesario que todas las rutas sean directas, amplias o seguras. Las restricciones espaciales pueden generar decisiones y tensión, pero deben ser intencionales y permitir una navegación comprensible.

## 47.3. RELACIONES FUNCIONALES ENTRE DEPARTAMENTOS

Determinar qué espacios necesitan proximidad, conexión directa, separación o controles intermedios. Ejemplos para NEXUS:

**Acceso y administración**

- Recepción próxima a los accesos principales.
- Administración relacionada con recepción y áreas de personal.
- Registro y control de visitantes próximos a recepción.

**Seguridad**

- Seguridad y control de acceso próximos a las entradas y sectores que supervisan.
- Vigilancia relacionada con cámaras, monitoreo y comunicaciones.
- Puestos de seguridad conectados con áreas restringidas mediante accesos controlados.
- Rutas de emergencia y puntos de control con lógica operativa.

**Almacenamiento y logística**

- Almacenes relacionados con recepción de suministros.
- Áreas de carga conectadas con rutas de transporte y ascensores adecuados.
- Depósitos especializados próximos a los departamentos que utilizan sus recursos.
- Circulaciones aptas para equipos y materiales.

**Investigación**

- Laboratorios relacionados con preparación, análisis y almacenamiento de muestras.
- Áreas de investigación conectadas según sus procedimientos.
- Espacios de experimentación con accesos y controles apropiados.
- Zonas restringidas separadas de áreas administrativas o públicas cuando corresponda.

**Áreas médicas**

- Quirófanos relacionados con preparación médica y recuperación cuando corresponda.
- Morgues y cámaras frigoríficas con accesos controlados.
- Áreas de aislamiento separadas de circulaciones generales.
- Suministros médicos próximos a las áreas que los necesitan.

**Contención**

- Cámaras de contención relacionadas con vigilancia y control.
- Accesos restringidos y mecanismos de seguridad.
- Áreas técnicas para monitoreo y mantenimiento.
- Circulaciones controladas para personal autorizado.

**Infraestructura**

- Generadores relacionados con distribución eléctrica, ventilación y mantenimiento.
- Servidores relacionados con telecomunicaciones, monitoreo y sistemas de control.
- Sistemas de ventilación conectados con los sectores que abastecen.
- Espacios técnicos accesibles para mantenimiento y sustitución de equipos.

No colocar departamentos incompatibles uno junto al otro sin justificación funcional o arquitectónica. Tampoco separar espacios que necesitan una conexión operativa directa.

**Recepción y extracción**

- La recepción del nivel 1 es el punto establecido para la extracción y entrega del botín.
- Debe existir una conexión arquitectónica y de circulación comprensible entre recepción y las rutas principales de la instalación.
- La distribución debe permitir que los jugadores trasladen objetos y componentes recuperados hasta recepción.

**Equipos recuperables y desmontaje**

- Los laboratorios, áreas técnicas y departamentos especializados pueden contener equipos desmontables cuando su función lo justifique.
- Debe existir espacio funcional alrededor de los equipos que requieran inspección, manipulación o desmontaje.
- Los objetos y componentes recuperables deben corresponder con la función original del departamento.
- Las rutas de transporte deben considerar el tamaño y las limitaciones de los componentes que puedan extraerse de esos equipos.

## 47.4. CIRCULACIONES Y CONECTIVIDAD

Planificar las circulaciones desde el inicio. Considerar cuando corresponda:

- Circulación del personal.
- Circulación de visitantes.
- Transporte de suministros.
- Transporte de maquinaria, equipos y muestras.
- Accesos de mantenimiento.
- Accesos restringidos.
- Rutas de emergencia y evacuación.
- Escaleras, ascensores y rampas.
- Corredores principales y secundarios.
- Túneles y conexiones técnicas.

Las rutas deben tener sentido respecto a la función de los espacios. No crear habitaciones sin conexiones funcionales, puertas que conduzcan a paredes o espacios inaccesibles, ni recorridos sin sentido.

Evitar que las circulaciones de suministros atraviesen innecesariamente zonas administrativas, médicas o restringidas. Las rutas alternativas, conexiones secretas y accesos de mantenimiento pueden aportar exploración y jugabilidad, pero deben conservar coherencia arquitectónica.

## 47.5. ARQUITECTURA MULTINIVEL Y VOLUMETRÍA

La instalación debe concebirse como un espacio tridimensional, no como plantas idénticas apiladas. Combinar cuando tenga sentido:

- Sectores a diferentes alturas.
- Espacios de doble altura.
- Cámaras que conecten varios niveles.
- Pasarelas, puentes y plataformas industriales.
- Ascensores de carga y montacargas.
- Escaleras de servicio y rampas.
- Pozos verticales y túneles técnicos.
- Cámaras de maquinaria.
- Sectores inundados, colapsados o parcialmente inaccesibles.
- Accesos ocultos y rutas de mantenimiento.

Las conexiones verticales deben conectar espacios reales y tener una función identificable. No crear escaleras, ascensores o pasarelas como decoración si no conectan correctamente los espacios.

## 47.6. DIMENSIONAMIENTO DURANTE LA PLANIFICACIÓN

Las dimensiones deben determinarse después de establecer la función y las necesidades de cada espacio. No utilizar medidas fijas para todas las habitaciones ni repetir módulos idénticos sin justificación.

Antes de dimensionar un espacio, considerar:

- Función y capacidad.
- Personajes y equipamiento.
- Medidas oficiales de las criaturas en `fotos-referencia/modelos-referencia`.
- Mobiliario y maquinaria.
- Circulación y maniobra.
- Accesibilidad y seguridad.
- Mantenimiento y transporte.
- Altura y volumen necesarios.
- Conexiones con otros espacios.

Las dimensiones deben ser coherentes con la escala maestra de la sección 30 y la función descrita en la sección 31.

## 47.7. PLANIFICACIÓN ANTES DE MODELAR O REORGANIZAR

Antes de crear una instalación nueva o reorganizar una existente:

1. Inspeccionar la arquitectura y los archivos actuales.
2. Inventariar habitaciones, sectores, niveles y espacios de circulación.
3. Identificar la función real o prevista de cada habitación.
4. Clasificar los departamentos y sus niveles de restricción.
5. Identificar relaciones de proximidad, conexión y separación.
6. Determinar necesidades de circulación y transporte.
7. Analizar la distribución vertical y las conexiones entre niveles.
8. Comprobar dimensiones y proporciones con la escala maestra.
9. Validar puertas, pasillos, escaleras, ascensores y accesos.
10. Identificar conflictos, espacios mal aprovechados y rutas incoherentes.
11. Preparar una propuesta arquitectónica con planos o vistas por nivel y conexiones verticales.
12. Presentar la propuesta para revisión antes de ejecutar cambios estructurales.

La propuesta debe mostrar qué se conserva, qué se mueve, qué se amplía, qué se reduce y por qué. No modificar a ciegas.

## 47.8. AUDITORÍA DE INSTALACIONES EXISTENTES

Cuando se trabaje sobre una instalación ya construida, realizar primero una auditoría. Comprobar:

- Si los departamentos están distribuidos de manera lógica.
- Si los niveles tienen una identidad funcional.
- Si existen mezclas de departamentos sin justificación.
- Si las habitaciones tienen dimensiones apropiadas para su función.
- Si los espacios permiten realizar sus operaciones.
- Si las conexiones entre departamentos son coherentes.
- Si las rutas de circulación y transporte son funcionales.
- Si existen habitaciones aisladas o mal conectadas.
- Si hay sectores vacíos o mal aprovechados.
- Si las conexiones verticales tienen sentido.
- Si la escala es coherente con jugadores, equipamiento y criaturas.
- Si los cambios propuestos afectan navegación, colisiones, iluminación, audio, IA o jugabilidad.

Presentar los problemas detectados y una propuesta de reorganización antes de modificar la arquitectura. No mover, eliminar, reconstruir ni redimensionar habitaciones sin comprobar previamente sus dependencias y conexiones. Conservar copias de seguridad y versiones anteriores.

## 47.9. COHERENCIA ARQUITECTÓNICA Y NARRATIVA

La instalación debe contar una historia mediante su organización. La ubicación de departamentos, rutas, accesos y restricciones debe reflejar cómo funcionaba la organización antes del incidente.

La arquitectura también debe reflejar las consecuencias del desastre, la evacuación, los fallos de contención y el abandono prolongado. No distribuir daños, destrucción y elementos narrativos aleatoriamente.

Cada sector debe conservar una identidad arquitectónica y funcional reconocible.

## 47.10. REGLA DE APROBACIÓN

No comenzar una reorganización arquitectónica importante sin presentar primero una propuesta que permita evaluar:

- Distribución funcional.
- Organización de niveles.
- Relaciones entre departamentos.
- Circulaciones y conectividad.
- Dimensiones y proporciones.
- Compatibilidad con jugadores y criaturas.
- Arquitectura tridimensional.
- Coherencia narrativa.

La propuesta debe poder revisarse antes de ejecutar cambios. La prioridad es conseguir una instalación funcional, creíble, explorable y visualmente convincente.

\\# REGLA GENERAL PARA LAS SECCIONES 30--47

Estas secciones amplían los requisitos de diseño de FRECUENCIA MUERTA.

No autorizan a implementar todos los sistemas inmediatamente ni

sustituyen el plan de fases existente.

Antes de implementar una característica:

1\\. Revisar si ya existe algo equivalente en el proyecto.

2\\. Identificar qué sistemas y recursos pueden reutilizarse.

3\\. Comprobar dependencias y riesgos.

4\\. Dividir la implementación en pasos pequeños.

5\\. Definir criterios de aceptación.

6\\. Probar el resultado.

7\\. Documentar limitaciones y estado real.

La mecánica de desmontaje y recuperación de componentes debe respetar conjuntamente las secciones 4, 32, 33, 45, 46 y 47. No implementar sistemas de desmontaje aislados del inventario, las herramientas, el peso, el volumen, las físicas, el sonido, las criaturas y la extracción. La recepción del nivel 1 es la ubicación establecida para la extracción; cualquier detalle operativo que aún no esté definido debe proponerse y aprobarse antes de implementarse.

Las dimensiones, cantidades y ejemplos de este documento son referencias

iniciales de diseño. Deben validarse mediante prototipos y pruebas de

jugabilidad, no tratarse como cifras definitivas e inamovibles.

Las decisiones arquitectónicas deben respetar conjuntamente las secciones 30, 31 y 47. La escala, las dimensiones, la distribución funcional y la organización de niveles no deben resolverse de manera independiente. Antes de modificar una instalación, comprobar la coherencia entre arquitectura, personajes, equipamiento, medidas oficiales de las criaturas, mobiliario, circulación, jugabilidad y narrativa.

La imagen `fotos-referencia/modelos-referencia` es la fuente oficial de las medidas conceptuales de las cuatro criaturas. Consultar y transcribir sus valores reales; nunca sustituirlos por dimensiones inventadas.

---

# 48. REGLA PERMANENTE: SKILLS OBLIGATORIAS Y REALISMO ADAPTATIVO

## 48.1. Uso obligatorio de skills

**USAR SIEMPRE TODAS LAS SKILLS QUE SE NECESITE. NO ES OPCIONAL.**

Antes de empezar cualquier tarea:

1. Revisar el catálogo de skills disponibles.
2. Identificar todas las skills relevantes para esa tarea concreta.
3. Cargarlas y usarlas de verdad: para planificar, modelar, texturizar, iluminar, renderizar, auditar, documentar o probar.
4. No basta con nombrarlas ni con decir que se van a usar. Hay que aplicarlas en el trabajo real.
5. Registrar en el informe final qué skills se usaron y para qué.
6. Si una skill relevante no se usó, justificarlo de forma explícita.
7. Si una skill contradice este documento, prevalece `AGENTS.md`; se documenta la contradicción y se prioriza la estabilidad, el rendimiento y la coherencia del proyecto.
8. No instalar dependencias ni cambiar herramientas sin necesidad.

La falta de uso de una skill relevante se considera una tarea incompleta.

## 48.2. Estándar de realismo adaptativo

El estándar vigente es `docs/FM_QUALITY_STANDARD.md`, sección **19. Reglas de realismo adaptativo para Blender**.

Principios obligatorios:

- **Identificar la categoría antes de modelar:** hard surface/mecánico/sci-fi, orgánico/natural, objeto cotidiano/mobiliario o arquitectura/estructura.
- **No usar un estilo único para todo.** Los detalles, el bevel, el material y la iluminación se adaptan a la categoría.
- **Hard surface:** panel lines, tornillos, rejillas, cortes booleanos y bevel pronunciado (3–4 segmentos).
- **Orgánico:** Displace/Multires con ruido, formas irregulares y asimétricas; prohibido usar paneles o pernos.
- **Objetos cotidianos/mobiliario:** uniones realistas, costuras cuando corresponda y bevel sutil (2–3 segmentos).
- **Arquitectura:** marcos, zócalos, textura de concreto/ladrillo y desgaste en esquinas inferiores.
- **Materiales contextuales:** metal/plástico con Noise 80–150 → ColorRamp → Roughness; madera con Noise/Musgrave 10–20 alargado → Color/Roughness; tela/cuero con Bump 0.01–0.02 y Noise de alta escala. Nunca el mismo Noise para todo.
- **Reglas universales:** escala real, Bevel mínimo 2 segmentos, quads limpios, `remove_doubles`, normales recalculadas, 2–3 Area Lights grandes, cámara 50/85 mm con DOF si es objeto pequeño, Cycles mínimo 128 samples con Denoise.
- **Cierre de tarea:** Validación de topología (0 caras invertidas, quads limpios, normales recalculadas) y confirmación de que los materiales, bevels e iluminación están aplicados correctamente en el script.
- **Excepciones:** documentadas y aprobadas; no se aceptan excepciones verbales.

El pase de casilleros Z10 (`docs/fm_z10_lockers_studio.png`) queda como **ejemplo de aplicación** de este estándar, no como norma única.
