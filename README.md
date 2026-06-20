# -tpi-oe-valzura-villanueva
Lissy — Sistema de Gestión de Licencias y Vacaciones

Trabajo Práctico Integrador — Organización Empresarial
Tecnicatura Universitaria en Programación a Distancia (UTN)

Descripción

Lissy es un chatbot simulado por consola, desarrollado en Python, que automatiza el proceso administrativo de gestión de licencias y vacaciones dentro de una organización. El bot permite a los empleados solicitar licencias, consultar su saldo de días disponibles y dar de baja solicitudes propias, mientras que los jefes pueden aprobar las licencias pendientes de su equipo.

El diseño de Lissy responde al diagrama BPMN 2.0 elaborado para este TPI, distinguiendo entre las tareas del Usuario (ingreso de datos, decisiones) y las tareas del Sistema/Bot (validaciones, cálculos, persistencia), e implementando las compuertas de decisión correspondientes a las reglas de negocio del proceso.

Proceso modelado

Lissy automatiza el ciclo completo de una licencia, desde la solicitud hasta su resolución:


Inicio de sesión del empleado mediante DNI y clave.
Alta de licencia: el empleado elige un tipo, indica fechas y el sistema valida la solicitud.
Aprobación de licencia: un jefe revisa y aprueba solicitudes pendientes de otros empleados.
Consulta de días disponibles: días anuales, comprometidos y restantes.
Baja de licencia: el empleado anula una solicitud propia aún pendiente.
Consulta de solicitudes gestionadas: licencias propias pendientes o aprobadas.


El detalle completo del flujo, incluyendo los caminos "as-is" y "to-be", se encuentra en el diagrama BPMN adjunto en la carpeta docs/.

Stack tecnológico

ComponenteDetalleLenguajePython 3 (librerías estándar: csv, os, datetime)InterfazSimulador por consola (CLI)PersistenciaArchivos CSV (empleados.csv, licencias.csv)Gestión de estadosControl de flujo por excepciones y bucle de menú


La plataforma de despliegue real (Telegram, WhatsApp Business o Web) queda planteada como trabajo futuro. Para este TPI, el proceso se valida mediante un simulador de consola que reproduce fielmente la lógica del diagrama BPMN.



Estructura del repositorio

.
├── docs/
│   ├── lissy_bpmn_01_navegacion_general.png         # Diagrama de navegacion general
│   ├── lissy_bpmn_02_alta_licencia.png         # Diagrama de alta de licencia
│   ├── lissy_bpmn_03_aprobacion_licencias.png         # Diagrama de aprobacion de licencia
│   ├── lissy_bpmn_04_baja_consultas.png         # Diagrama de aprobacion de licencia
│   ├── diccionario_datos.md   # Descripción de variables y entidades
│   └── TPI_Lissy_OrganizacionEmpresarial.pdf      # PDF entrega final
├── empleados.csv               # Datos de empleados (se genera automáticamente)
├── licencias.csv                # Registro de licencias (se genera automáticamente)
├── main.py                      # Punto de entrada del simulador
├── README.md


Instalación

Lissy solo utiliza librerías estándar de Python, por lo que no requiere dependencias externas.

bashgit clone <url-del-repositorio>
cd <nombre-del-repositorio>
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate

Ejecución

bashpython main.py

Al ejecutarse por primera vez, Lissy crea automáticamente empleados.csv (con tres usuarios de ejemplo) y licencias.csv (vacío) si no existen.

Usuarios de prueba

DNI        Clave      Nombre    Rol  Días anuales
12345678  abc123   Juan Perez  Empleado  15
87654321  xyz789   Maria Lopez  Jefe     15  
11223344  qwe456   Ana Gomez  Empleado   20

Flujo de la simulación


El bot solicita DNI y clave, validando contra empleados.csv hasta obtener credenciales correctas.
Una vez autenticado, se muestra el menú principal con seis opciones.
Desde cualquier punto de carga de datos, el usuario puede escribir menu o menú para cancelar la operación en curso y volver al menú principal.
Según la opción elegida, Lissy ejecuta la lógica correspondiente y persiste los cambios en licencias.csv.


Menú principal

Opción

1 Alta de licencia - Todos los empleados
2 Solicitudes gestionadas - Todos los empleados
3 Aprobación de licencias - Solo jefes (es_jefe = True)
4 Días disponibles - Todos los empleados
5 Baja de licencia - Todos los empleados
6 Salida - Todos los empleados

Gestión de estados - Maquina de estados simulada

A diferencia de una máquina de estados explícita, Lissy resuelve la "memoria" del proceso mediante un bucle de menú (ejecutar_menu) que mantiene al usuario autenticado durante toda la sesión, combinado con una excepción de control (VolverAlMenu) que permite abortar cualquier carga de datos en curso y regresar al estado de menú principal sin perder la sesión activa.


Estados representados en la lógica del bot:

INICIO_SESION — validación de DNI y clave.
MENU_PRINCIPAL — espera de selección de opción.
CARGANDO_DATOS — el bot pide datos de una operación (tipo, fechas, ID, confirmación), interrumpible en cualquier momento.
PROCESANDO — validaciones y escritura en licencias.csv.
FIN — cierre del programa (opción 6).


Cada licencia, además, tiene su propio estado persistido en el CSV: pendiente, aprobada o anulada.

Reglas de negocio implementadas (compuertas de decisión)


Tipo de licencia válido: debe ser vacaciones, enfermedad, estudio o duelo.
Formato de fecha: DD/MM/AAAA, validado y convertido con datetime.
Cálculo de días hábiles: excluye sábados y domingos del rango solicitado.
Sin superposición: una nueva licencia no puede cruzarse en fechas con otra pendiente o aprobada del mismo empleado.
Saldo suficiente: los días solicitados no pueden superar los días anuales menos los ya comprometidos.
Restricción de aprobación: un jefe no puede aprobar sus propias licencias, ni licencias que no estén en estado pendiente.
Restricción de baja: solo se pueden anular licencias propias que estén pendientes.


Manejo de errores (camino infeliz)

Lissy contempla validaciones explícitas ante entradas inválidas del usuario:


DNI inexistente o clave incorrecta al iniciar sesión (reintento indefinido).
Tipo de licencia fuera de la lista permitida.
Fechas con formato inválido o fecha de fin anterior a la de inicio.
Período sin días hábiles (por ejemplo, un fin de semana completo).
Solicitud que se superpone con otra ya comprometida.
Solicitud que excede el saldo de días disponible.
ID de licencia inexistente al aprobar o anular.
Intento de un jefe de aprobar una licencia propia.
Interrupción manual (Ctrl+C) capturada de forma controlada.
Cualquier excepción no prevista, capturada para evitar que el programa se cierre abruptamente.



Autoría

Trabajo realizado para Organización Empresarial — UTN, Tecnicatura Universitaria en Programación a Distancia.

Integrantes: Villanueva Felipe y Valzura Lourdes
Comision: 6
