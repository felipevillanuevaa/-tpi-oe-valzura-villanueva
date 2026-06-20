import csv
import os
from datetime import datetime, timedelta


ARCHIVO_EMPLEADOS = "empleados.csv"
ARCHIVO_LICENCIAS = "licencias.csv"

CAMPOS_EMPLEADOS = ["dni", "clave", "nombre", "es_jefe", "dias_anuales"]
CAMPOS_LICENCIAS = [
    "id",
    "dni_empleado",
    "tipo",
    "fecha_inicio",
    "fecha_fin",
    "dias",
    "estado",
    "dni_aprobador",
]

TIPOS_LICENCIA = ["vacaciones", "enfermedad", "estudio", "duelo"]
ESTADOS_COMPROMETIDOS = ["pendiente", "aprobada"]


class VolverAlMenu(Exception):
    """Excepción simple para volver al menú principal desde cualquier opción."""
    pass


def crear_archivos_si_no_existen():
    """Crea los archivos CSV base si todavía no existen."""
    if not os.path.exists(ARCHIVO_EMPLEADOS):
        empleados_ejemplo = [
            {
                "dni": "12345678",
                "clave": "abc123",
                "nombre": "Juan Perez",
                "es_jefe": "False",
                "dias_anuales": "15",
            },
            {
                "dni": "87654321",
                "clave": "xyz789",
                "nombre": "Maria Lopez",
                "es_jefe": "True",
                "dias_anuales": "15",
            },
            {
                "dni": "11223344",
                "clave": "qwe456",
                "nombre": "Ana Gomez",
                "es_jefe": "False",
                "dias_anuales": "20",
            },
        ]
        escribir_csv(ARCHIVO_EMPLEADOS, CAMPOS_EMPLEADOS, empleados_ejemplo)

    if not os.path.exists(ARCHIVO_LICENCIAS):
        escribir_csv(ARCHIVO_LICENCIAS, CAMPOS_LICENCIAS, [])


def leer_csv(ruta):
    """Lee un CSV y devuelve sus filas como lista de diccionarios."""
    try:
        with open(ruta, "r", newline="", encoding="utf-8-sig") as archivo:
            lector = csv.DictReader(archivo, skipinitialspace=True)
            if lector.fieldnames is None:
                return []
            return list(lector)
    except FileNotFoundError:
        return []


def escribir_csv(ruta, campos, filas):
    """Sobrescribe un CSV respetando el encabezado indicado."""
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow(fila)


def pedir_dato(mensaje):
    """Pide un dato y permite escribir menu/menú para volver al menú principal."""
    valor = input(mensaje).strip()
    if valor.lower() in ["menu", "menú"]:
        raise VolverAlMenu
    return valor


def normalizar_texto(texto):
    """Normaliza textos simples para comparar opciones escritas por consola."""
    return texto.strip().lower()


def buscar_empleado(dni):
    """Busca un empleado por DNI comparándolo como texto."""
    empleados = leer_csv(ARCHIVO_EMPLEADOS)
    for empleado in empleados:
        if empleado.get("dni", "").strip() == dni.strip():
            return empleado
    return None


def empleado_es_jefe(empleado):
    """Convierte el campo es_jefe del CSV a un valor booleano."""
    return empleado.get("es_jefe", "").strip().lower() == "true"


def obtener_dias_anuales(empleado):
    """Obtiene los días anuales del empleado con manejo de errores."""
    try:
        return int(empleado.get("dias_anuales", "0"))
    except ValueError:
        return 0


def iniciar_sesion():
    """Gestiona el login por DNI y clave hasta que los datos sean correctos."""
    while True:
        print("\n--- Inicio de sesión ---")
        dni = input("Ingresá tu DNI: ").strip()
        empleado = buscar_empleado(dni)

        if empleado is None:
            print("Error: DNI no encontrado. Intentá nuevamente.")
            continue

        clave = input("Ingresá tu clave: ").strip()
        if clave != empleado.get("clave", ""):
            print("Error: clave incorrecta. Intentá nuevamente.")
            continue

        print(
            f"\nHola {empleado.get('nombre', '')}, bienvenido/a a Lissy, "
            "tu mejor amigo para gestionar licencias y vacaciones."
        )
        return empleado


def convertir_fecha(fecha_texto):
    """Valida una fecha en formato DD/MM/AAAA y la convierte a date."""
    try:
        return datetime.strptime(fecha_texto, "%d/%m/%Y").date()
    except ValueError:
        raise ValueError("La fecha debe tener formato DD/MM/AAAA y ser una fecha válida.")


def calcular_dias_habiles(fecha_inicio, fecha_fin):
    """Calcula días hábiles entre dos fechas, excluyendo sábados y domingos."""
    if fecha_fin < fecha_inicio:
        raise ValueError("La fecha de fin no puede ser anterior a la fecha de inicio.")

    total = 0
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        if fecha_actual.weekday() < 5:
            total += 1
        fecha_actual += timedelta(days=1)
    return total


def hay_superposicion(dni, fecha_inicio, fecha_fin):
    """Verifica si una licencia se superpone con otra pendiente o aprobada."""
    licencias = leer_csv(ARCHIVO_LICENCIAS)

    for licencia in licencias:
        mismo_empleado = licencia.get("dni_empleado", "").strip() == dni.strip()
        estado_comprometido = normalizar_texto(licencia.get("estado", "")) in ESTADOS_COMPROMETIDOS

        if not mismo_empleado or not estado_comprometido:
            continue

        try:
            inicio_existente = convertir_fecha(licencia.get("fecha_inicio", ""))
            fin_existente = convertir_fecha(licencia.get("fecha_fin", ""))
        except ValueError:
            continue

        se_cruzan = fecha_inicio <= fin_existente and fecha_fin >= inicio_existente
        if se_cruzan:
            return True

    return False


def calcular_dias_comprometidos(dni):
    """Suma días de licencias pendientes y aprobadas de un empleado."""
    total = 0
    licencias = leer_csv(ARCHIVO_LICENCIAS)

    for licencia in licencias:
        mismo_empleado = licencia.get("dni_empleado", "").strip() == dni.strip()
        estado_comprometido = normalizar_texto(licencia.get("estado", "")) in ESTADOS_COMPROMETIDOS

        if mismo_empleado and estado_comprometido:
            try:
                total += int(licencia.get("dias", "0"))
            except ValueError:
                pass

    return total


def calcular_dias_restantes(empleado):
    """Calcula los días restantes según días anuales menos comprometidos."""
    dias_anuales = obtener_dias_anuales(empleado)
    dias_comprometidos = calcular_dias_comprometidos(empleado.get("dni", ""))
    return dias_anuales - dias_comprometidos


def obtener_proximo_id():
    """Obtiene el próximo ID disponible para una nueva licencia."""
    licencias = leer_csv(ARCHIVO_LICENCIAS)
    mayor_id = 0

    for licencia in licencias:
        try:
            id_actual = int(licencia.get("id", "0"))
            if id_actual > mayor_id:
                mayor_id = id_actual
        except ValueError:
            pass

    return str(mayor_id + 1)


def mostrar_licencias(lista_licencias, incluir_empleado=False):
    """Muestra licencias en consola con un formato simple."""
    if not lista_licencias:
        print("No hay licencias para mostrar.")
        return

    print("\nLicencias:")
    print("-" * 90)
    for licencia in lista_licencias:
        partes = [
            f"ID: {licencia.get('id', '')}",
            f"Tipo: {licencia.get('tipo', '')}",
            f"Desde: {licencia.get('fecha_inicio', '')}",
            f"Hasta: {licencia.get('fecha_fin', '')}",
            f"Días: {licencia.get('dias', '')}",
            f"Estado: {licencia.get('estado', '')}",
        ]

        if incluir_empleado:
            empleado = buscar_empleado(licencia.get("dni_empleado", ""))
            nombre = empleado.get("nombre", "Sin nombre") if empleado else "Sin nombre"
            partes.insert(1, f"Empleado: {nombre} - DNI {licencia.get('dni_empleado', '')}")

        aprobador = licencia.get("dni_aprobador", "").strip()
        if aprobador:
            partes.append(f"Aprobador: {aprobador}")

        print(" | ".join(partes))
    print("-" * 90)


def opcion_alta_licencia(empleado):
    """Opción 1: registra una nueva licencia pendiente si supera las validaciones."""
    print("\n--- Opción 1: Alta de licencia ---")
    print("Tipos disponibles:", ", ".join(TIPOS_LICENCIA))

    try:
        tipo = normalizar_texto(pedir_dato("Ingresá el tipo de licencia: "))
        if tipo not in TIPOS_LICENCIA:
            print("Error: tipo de licencia inválido.")
            return

        fecha_inicio_texto = pedir_dato("Ingresá la fecha de inicio (DD/MM/AAAA): ")
        fecha_fin_texto = pedir_dato("Ingresá la fecha de fin (DD/MM/AAAA): ")

        fecha_inicio = convertir_fecha(fecha_inicio_texto)
        fecha_fin = convertir_fecha(fecha_fin_texto)
        dias = calcular_dias_habiles(fecha_inicio, fecha_fin)

        if dias <= 0:
            print("Error: el período seleccionado no contiene días hábiles.")
            return

        dni = empleado.get("dni", "")

        if hay_superposicion(dni, fecha_inicio, fecha_fin):
            print("Error: la licencia se superpone con otra licencia pendiente o aprobada.")
            return

        dias_restantes = calcular_dias_restantes(empleado)
        if dias > dias_restantes:
            print(
                f"Error: no tenés días disponibles suficientes. "
                f"Pediste {dias} y te quedan {dias_restantes}."
            )
            return

        licencias = leer_csv(ARCHIVO_LICENCIAS)
        nueva_licencia = {
            "id": obtener_proximo_id(),
            "dni_empleado": dni,
            "tipo": tipo,
            "fecha_inicio": fecha_inicio_texto,
            "fecha_fin": fecha_fin_texto,
            "dias": str(dias),
            "estado": "pendiente",
            "dni_aprobador": "",
        }
        licencias.append(nueva_licencia)
        escribir_csv(ARCHIVO_LICENCIAS, CAMPOS_LICENCIAS, licencias)

        print("Licencia registrada correctamente con estado pendiente.")
        print(f"Días hábiles solicitados: {dias}")

    except VolverAlMenu:
        raise
    except ValueError as error:
        print(f"Error: {error}")
    except Exception as error:
        print(f"Error inesperado al registrar la licencia: {error}")


def opcion_solicitudes_gestionadas(empleado):
    """Opción 2: muestra licencias propias pendientes y aprobadas."""
    print("\n--- Opción 2: Solicitudes gestionadas ---")
    dni = empleado.get("dni", "")
    licencias = leer_csv(ARCHIVO_LICENCIAS)

    propias = []
    for licencia in licencias:
        mismo_empleado = licencia.get("dni_empleado", "").strip() == dni.strip()
        estado_visible = normalizar_texto(licencia.get("estado", "")) in ESTADOS_COMPROMETIDOS
        if mismo_empleado and estado_visible:
            propias.append(licencia)

    if not propias:
        print("Aviso: no tenés solicitudes pendientes o aprobadas.")
        return

    mostrar_licencias(propias)


def opcion_aprobacion_licencias(empleado):
    """Opción 3: permite que un jefe apruebe licencias pendientes ajenas."""
    print("\n--- Opción 3: Aprobación de licencias ---")

    if not empleado_es_jefe(empleado):
        print("Por tu rol, no tenés disponible esta opción.")
        return

    dni_jefe = empleado.get("dni", "")
    licencias = leer_csv(ARCHIVO_LICENCIAS)
    pendientes_ajenas = []

    for licencia in licencias:
        es_pendiente = normalizar_texto(licencia.get("estado", "")) == "pendiente"
        es_ajena = licencia.get("dni_empleado", "").strip() != dni_jefe.strip()
        if es_pendiente and es_ajena:
            pendientes_ajenas.append(licencia)

    if not pendientes_ajenas:
        print("Aviso: no hay licencias pendientes de otros usuarios para aprobar.")
        return

    mostrar_licencias(pendientes_ajenas, incluir_empleado=True)

    try:
        id_elegido = pedir_dato("Ingresá el ID de la licencia que querés aprobar: ")
        licencia_encontrada = None

        for licencia in pendientes_ajenas:
            if licencia.get("id", "").strip() == id_elegido.strip():
                licencia_encontrada = licencia
                break

        if licencia_encontrada is None:
            print("Error: no se encontró una licencia pendiente ajena con ese ID.")
            return

        if licencia_encontrada.get("dni_empleado", "").strip() == dni_jefe.strip():
            print("Error: no podés aprobar una licencia propia.")
            return

        for licencia in licencias:
            if licencia.get("id", "").strip() == id_elegido.strip():
                licencia["estado"] = "aprobada"
                licencia["dni_aprobador"] = dni_jefe
                break

        escribir_csv(ARCHIVO_LICENCIAS, CAMPOS_LICENCIAS, licencias)
        print("Licencia aprobada correctamente.")

    except VolverAlMenu:
        raise
    except Exception as error:
        print(f"Error inesperado al aprobar la licencia: {error}")


def opcion_dias_disponibles(empleado):
    """Opción 4: muestra días anuales, comprometidos y restantes."""
    print("\n--- Opción 4: Días disponibles ---")
    dni = empleado.get("dni", "")
    dias_anuales = obtener_dias_anuales(empleado)
    dias_comprometidos = calcular_dias_comprometidos(dni)
    dias_restantes = dias_anuales - dias_comprometidos

    print(f"Días anuales totales: {dias_anuales}")
    print(f"Días comprometidos: {dias_comprometidos}")
    print(f"Días restantes: {dias_restantes}")


def opcion_baja_licencia(empleado):
    """Opción 5: anula una licencia propia que todavía esté pendiente."""
    print("\n--- Opción 5: Baja de licencia ---")
    dni = empleado.get("dni", "")
    licencias = leer_csv(ARCHIVO_LICENCIAS)

    propias_pendientes = []
    for licencia in licencias:
        mismo_empleado = licencia.get("dni_empleado", "").strip() == dni.strip()
        es_pendiente = normalizar_texto(licencia.get("estado", "")) == "pendiente"
        if mismo_empleado and es_pendiente:
            propias_pendientes.append(licencia)

    if not propias_pendientes:
        print("Aviso: no tenés licencias pendientes para anular.")
        return

    mostrar_licencias(propias_pendientes)

    try:
        id_elegido = pedir_dato("Ingresá el ID de la licencia que querés anular: ")
        licencia_encontrada = None

        for licencia in propias_pendientes:
            if licencia.get("id", "").strip() == id_elegido.strip():
                licencia_encontrada = licencia
                break

        if licencia_encontrada is None:
            print("Error: no se encontró una licencia pendiente propia con ese ID.")
            return

        confirmacion = normalizar_texto(pedir_dato("Confirmás la anulación? (s/n): "))
        if confirmacion not in ["s", "si", "sí"]:
            print("Anulación cancelada.")
            return

        for licencia in licencias:
            if licencia.get("id", "").strip() == id_elegido.strip():
                licencia["estado"] = "anulada"
                break

        escribir_csv(ARCHIVO_LICENCIAS, CAMPOS_LICENCIAS, licencias)
        print("Licencia anulada correctamente.")

    except VolverAlMenu:
        raise
    except Exception as error:
        print(f"Error inesperado al anular la licencia: {error}")


def mostrar_menu():
    """Muestra las opciones principales del chatbot."""
    print("\n========== MENÚ PRINCIPAL DE LISSY ==========")
    print("1. Alta de licencia")
    print("2. Solicitudes gestionadas")
    print("3. Aprobación de licencias")
    print("4. Días disponibles")
    print("5. Baja de licencia")
    print("6. Salida")
    print("Podés escribir 'menu' o 'menú' para volver al menú principal.")


def ejecutar_menu(empleado):
    """Ejecuta el ciclo principal del menú hasta que el usuario elija salir."""
    while True:
        try:
            mostrar_menu()
            opcion = input("Seleccioná una opción (1 a 6): ").strip()

            if opcion.lower() in ["menu", "menú"]:
                continue
            elif opcion == "1":
                opcion_alta_licencia(empleado)
            elif opcion == "2":
                opcion_solicitudes_gestionadas(empleado)
            elif opcion == "3":
                opcion_aprobacion_licencias(empleado)
            elif opcion == "4":
                opcion_dias_disponibles(empleado)
            elif opcion == "5":
                opcion_baja_licencia(empleado)
            elif opcion == "6":
                print("Gracias por usar Lissy. ¡Hasta luego!")
                break
            else:
                print("Aviso: opción inválida. Elegí un número del 1 al 6.")

        except VolverAlMenu:
            print("Volviendo al menú principal...")
        except KeyboardInterrupt:
            print("\nPrograma interrumpido. Gracias por usar Lissy.")
            break
        except Exception as error:
            print(f"Error inesperado en el menú: {error}")


def main():
    """Punto de entrada del programa Lissy."""
    crear_archivos_si_no_existen()
    print("========================================")
    print("LISSY - Sistema de gestión de licencias")
    print("========================================")
    empleado = iniciar_sesion()
    ejecutar_menu(empleado)


if __name__ == "__main__":
    main()
