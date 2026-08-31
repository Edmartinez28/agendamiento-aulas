"""
Catálogo de parametrizaciones de la interfaz.

Cada entrada se materializa como un registro `Parametro(etiqueta, valor)` en la
base de datos (ver migración `0008_parametros_diseno`). El context processor
`core.context_processors.parametros` los expone a TODAS las plantillas dentro
del diccionario `parametros`, y `base.html` los vuelca como variables CSS
`--p-<etiqueta>` sobre `:root`.

Para cambiar la piel del sistema completo basta con editar el registro
correspondiente desde el admin de Django: no hay que tocar ni una línea de CSS.
Para añadir un color nuevo: añádelo aquí, crea una migración de datos y úsalo en
`core/static/css/ite.css` como `var(--p-mi_color)`.

Los valores de aquí son SOLO el respaldo que se usa cuando el registro todavía
no existe en la base (por ejemplo antes de correr las migraciones).
"""

# Paleta viva anclada en azul. Todos los tonos están saturados por encima del
# 65 % y se reparten el círculo cromático para que dos estados nunca se
# confundan de un vistazo: azul 215°, cian 188°, verde 153°, ámbar 33°, rojo 0°,
# índigo 239°, púrpura 281°.
#
# Los valores están verificados en contraste: blanco sobre `fondo` da 5,19:1, y
# el peor chip de estado da 4,66:1 en claro y 5,83:1 en oscuro (AA para texto
# pequeño). Si cambias un color, mantén una luminosidad parecida o revisa que
# el texto de su chip siga siendo legible.

PARAMETROS_DEFECTO = {
    # ── Identidad ────────────────────────────────────────────────────────────
    # Azul institucional vivo: el color de acción de todo el sistema.
    "fondo": "#1668DC",
    "colortitulos": "#FFFFFF",
    # Pisado/hover del azul: mismo tono, más profundo.
    "marca_fuerte": "#0E4FAF",
    # Cian del anillo de tracking del visor: la "señal" del aula VR.
    # Se reserva para foco, selección y realce. Nunca para decorar.
    "senal": "#00BCD9",
    "marca_nombre": "Aula ITE-VR",
    "marca_institucion": "Universidad Católica de Cuenca",
    "pie_texto": "Jefatura de Innovación y Emprendimiento",

    # ── Periodo académico vigente ────────────────────────────────────────────
    # Recorta lo que ve el usuario final: perfil, listado de reservas y "mi
    # horario" sólo muestran reservas dentro de este rango. El horario del aula
    # (gestion) NO se filtra: ahí se navega por semanas y debe verse todo.
    #
    # Formato obligatorio AAAA-MM-DD. Si una fecha está vacía o mal escrita, ese
    # extremo simplemente no se aplica — se prefiere mostrar de más a esconder
    # reservas por una errata en el admin.
    "periodo_nombre": "Periodo académico 2026-2",
    "periodo_inicio": "2026-09-01",
    "periodo_fin": "2027-01-31",

    # ── Estados de reserva ───────────────────────────────────────────────────
    "estado_aprobada": "#0BA05C",
    "estado_revision": "#E8850A",
    "estado_cancelada": "#E03131",
    "estado_finalizada": "#6366F1",
    "estado_bloqueada": "#A435D6",
    "estado_estudiantil": "#0D9BB8",

    # ── Estados de inventario ────────────────────────────────────────────────
    "inv_nuevo": "#00A5C4",
    "inv_correcto": "#0BA05C",
    "inv_pendiente": "#E8850A",
    "inv_mantenimiento": "#A435D6",
    "inv_fallando": "#E03131",
    # "Baja" es el único apagado a propósito: un equipo retirado no debe gritar.
    "inv_baja": "#64748B",

    # ── Superficies · tema claro (panel de aula) ─────────────────────────────
    # Neutros llevados al tono del azul de marca (215°) para que el sistema se
    # sienta de una pieza en vez de color sobre gris.
    "claro_sala": "#E7EDF6",
    "claro_panel": "#F7FAFE",
    "claro_panel_alto": "#FFFFFF",
    "claro_ranura": "#DCE5F2",
    "claro_tinta": "#0F1B2D",

    # ── Superficies · tema oscuro (sala VR) ──────────────────────────────────
    "oscuro_sala": "#0A101C",
    "oscuro_panel": "#121A28",
    "oscuro_panel_alto": "#192334",
    "oscuro_ranura": "#070C15",
    "oscuro_tinta": "#E6EDF8",

    # ── Detalles ─────────────────────────────────────────────────────────────
    "radio_panel": "12px",
    "radio_control": "8px",
    "tipo_titulo": "'Space Grotesk'",
    "tipo_texto": "'Inter'",
    "tipo_dato": "'JetBrains Mono'",
    # "claro" | "oscuro" | "sistema"
    "tema_defecto": "claro",
}
