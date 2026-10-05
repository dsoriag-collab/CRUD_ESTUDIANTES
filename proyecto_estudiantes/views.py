from models import (
    Estudiante,
    CAMPOS_ESTUDIANTE
)

from shared.json_manager import (
    GestorJSON
)

from shared.herramientas import (
    es_email_valido
)


# ============================
# ARCHIVO DE DATOS
# ============================

gestor = GestorJSON(
    "data/estudiantes.json"
)


# ============================
# CONFIGURACIÓN
# ============================

CAMPOS_OBLIGATORIOS = (
    "nombre",
    "apellido",
    "email",
    "carnet"
)


CAMPOS_BUSCABLES = (
    "nombre",
    "apellido",
    "email",
    "carnet"
)


# ============================
# AYUDAS INTERNAS
# ============================

def emails_registrados(
    excepto_id=None
):

    return {
        registro["email"].lower()

        for registro
        in gestor.leer()

        if (
            registro["id"]
            != excepto_id
        )
    }


def carnets_registrados(
    excepto_id=None
):

    return {
        registro["carnet"].lower()

        for registro
        in gestor.leer()

        if (
            registro["id"]
            != excepto_id
        )
    }


def siguiente_id():

    ids = [
        registro["id"]

        for registro
        in gestor.leer()
    ]

    if ids:

        return max(ids) + 1

    return 1


# ============================
# C · CREATE
# ============================

def crear_estudiante(datos):

    try:

        # Crear diccionario limpio
        # con los campos del estudiante

        valores = {

            campo:
            str(
                datos.get(
                    campo,
                    ""
                )
            ).strip()

            for campo
            in CAMPOS_ESTUDIANTE
        }

        # ------------------------
        # CAMPOS OBLIGATORIOS
        # ------------------------

        faltantes = [

            campo

            for campo
            in CAMPOS_OBLIGATORIOS

            if not valores[campo]
        ]

        if faltantes:

            return (
                False,
                "Faltan campos obligatorios: "
                + ", ".join(faltantes)
            )

        # ------------------------
        # VALIDAR EMAIL
        # ------------------------

        if not es_email_valido(
            valores["email"]
        ):

            return (
                False,
                f"El email "
                f"'{valores['email']}' "
                f"no tiene un formato válido"
            )

        # ------------------------
        # EMAIL DUPLICADO
        # ------------------------

        if (
            valores["email"].lower()
            in emails_registrados()
        ):

            return (
                False,
                "Ese email ya está registrado"
            )

        # ------------------------
        # CARNET DUPLICADO
        # ------------------------

        if (
            valores["carnet"].lower()
            in carnets_registrados()
        ):

            return (
                False,
                "Ese carnet ya está registrado"
            )

        # ------------------------
        # CREAR OBJETO
        # ------------------------

        estudiante = Estudiante(
            siguiente_id(),
            **valores
        )

        # ------------------------
        # GUARDAR
        # ------------------------

        registros = gestor.leer()

        registros.append(
            estudiante.a_diccionario()
        )

        if not gestor.guardar(
            registros
        ):

            return (
                False,
                "No se pudo escribir el archivo"
            )

        return (
            True,
            f"Estudiante "
            f"{estudiante.obtener_nombre_completo()} "
            f"creado con id "
            f"{estudiante.id}"
        )

    except Exception as error:

        return (
            False,
            f"Error inesperado: {error}"
        )


# ============================
# R · READ TODOS
# ============================

def obtener_todos():

    return [

        Estudiante.desde_diccionario(
            registro
        )

        for registro
        in gestor.leer()
    ]


# ============================
# R · READ POR ID
# ============================

def obtener_por_id(
    id_estudiante
):

    for estudiante in obtener_todos():

        if (
            estudiante.id
            == id_estudiante
        ):

            return estudiante

    return None


# ============================
# S · SEARCH
# ============================

def buscar_estudiantes(
    termino
):

    termino = (
        termino
        .strip()
        .lower()
    )

    if not termino:

        return []

    encontrados = []

    for registro in gestor.leer():

        for campo in CAMPOS_BUSCABLES:

            contenido = str(
                registro.get(
                    campo,
                    ""
                )
            ).lower()

            if termino in contenido:

                encontrados.append(

                    Estudiante
                    .desde_diccionario(
                        registro
                    )
                )

                # Ya encontramos coincidencia
                # en este estudiante.
                break

    return encontrados


# ============================
# U · UPDATE
# ============================

def actualizar_estudiante(
    id_estudiante,
    cambios
):

    try:

        # ------------------------
        # CAMPOS DESCONOCIDOS
        # ------------------------

        desconocidos = (
            set(cambios)
            -
            set(CAMPOS_ESTUDIANTE)
        )

        if desconocidos:

            return (
                False,
                "Campos no válidos: "
                + ", ".join(
                    sorted(desconocidos)
                )
            )

        if not cambios:

            return (
                False,
                "No se indicó ningún cambio"
            )

        # ------------------------
        # EMAIL
        # ------------------------

        if "email" in cambios:

            cambios["email"] = (
                cambios["email"]
                .strip()
            )

            if not es_email_valido(
                cambios["email"]
            ):

                return (
                    False,
                    "El email no tiene "
                    "un formato válido"
                )

            if (
                cambios["email"].lower()
                in emails_registrados(
                    excepto_id=id_estudiante
                )
            ):

                return (
                    False,
                    "Ese email ya lo usa "
                    "otro estudiante"
                )

        # ------------------------
        # CARNET
        # ------------------------

        if "carnet" in cambios:

            cambios["carnet"] = (
                cambios["carnet"]
                .strip()
            )

            if (
                cambios["carnet"].lower()
                in carnets_registrados(
                    excepto_id=id_estudiante
                )
            ):

                return (
                    False,
                    "Ese carnet ya lo usa "
                    "otro estudiante"
                )

        # ------------------------
        # BUSCAR POSICIÓN
        # ------------------------

        registros = gestor.leer()

        posicion = None

        for indice, registro in enumerate(
            registros
        ):

            if (
                registro["id"]
                == id_estudiante
            ):

                posicion = indice

                break

        if posicion is None:

            return (
                False,
                f"No existe un estudiante "
                f"con id {id_estudiante}"
            )

        # ------------------------
        # ACTUALIZAR
        # ------------------------

        registros[posicion].update(
            cambios
        )

        if not gestor.guardar(
            registros
        ):

            return (
                False,
                "No se pudo escribir el archivo"
            )

        return (
            True,
            f"Estudiante "
            f"{id_estudiante} actualizado "
            f"({len(cambios)} campo/s)"
        )

    except Exception as error:

        return (
            False,
            f"Error inesperado: {error}"
        )


# ============================
# D · DELETE
# ============================

def eliminar_estudiante(
    id_estudiante
):

    registros = gestor.leer()

    quedan = [

        registro

        for registro
        in registros

        if (
            registro["id"]
            != id_estudiante
        )
    ]

    # Si ambas listas tienen
    # el mismo tamaño,
    # no encontramos el ID.

    if (
        len(quedan)
        == len(registros)
    ):

        return (
            False,
            f"No existe un estudiante "
            f"con id {id_estudiante}"
        )

    if not gestor.guardar(
        quedan
    ):

        return (
            False,
            "No se pudo escribir el archivo"
        )

    return (
        True,
        f"Estudiante "
        f"{id_estudiante} eliminado"
    )


# ============================
# EXTRA · AGREGAR NOTA
# ============================

def agregar_nota(
    id_estudiante,
    materia,
    nota
):

    estudiante = obtener_por_id(
        id_estudiante
    )

    if estudiante is None:

        return (
            False,
            f"No existe un estudiante "
            f"con id {id_estudiante}"
        )

    materia = str(
        materia
    ).strip()

    if not materia:

        return (
            False,
            "La materia es obligatoria"
        )

    # ------------------------
    # CONVERTIR NOTA
    # ------------------------

    try:

        nota = float(
            nota
        )

    except (
        TypeError,
        ValueError
    ):

        return (
            False,
            "La nota debe ser un número"
        )

    # ------------------------
    # VALIDAR RANGO
    # ------------------------

    if (
        nota < 0
        or nota > 20
    ):

        return (
            False,
            "La nota debe estar "
            "entre 0 y 20"
        )

    # ------------------------
    # AGREGAR NOTA AL OBJETO
    # ------------------------

    estudiante.agregar_nota(
        materia,
        nota
    )

    # ------------------------
    # ACTUALIZAR JSON
    # ------------------------

    registros = gestor.leer()

    for indice, registro in enumerate(
        registros
    ):

        if (
            registro["id"]
            == id_estudiante
        ):

            registros[indice] = (
                estudiante
                .a_diccionario()
            )

            break

    if not gestor.guardar(
        registros
    ):

        return (
            False,
            "No se pudo escribir el archivo"
        )

    return (
        True,
        f"Nota {nota:g} agregada "
        f"en {materia}"
    )


# ============================
# EXTRA · MATERIAS OFERTADAS
# ============================

def materias_ofertadas():

    materias = set()

    for estudiante in obtener_todos():

        materias.update(
            estudiante.materias
        )

    return materias


# ============================
# EXTRA · MATERIAS EN COMÚN
# ============================

def estudiantes_en_comun(
    id_a,
    id_b
):

    estudiante_a = obtener_por_id(
        id_a
    )

    estudiante_b = obtener_por_id(
        id_b
    )

    if (
        estudiante_a is None
        or estudiante_b is None
    ):

        return None

    return estudiante_a.materias_en_comun(
        estudiante_b
    )