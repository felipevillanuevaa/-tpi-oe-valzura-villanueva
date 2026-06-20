# Diccionario de datos — Lissy

Este documento describe las entidades, campos, variables calculadas y constantes que maneja el sistema **Lissy**, persistidas en los archivos `empleados.csv` y `licencias.csv`.

---

## Entidad: Empleado

**Archivo:** `empleados.csv`

| Campo          | Tipo     | Descripción                                                                      | Valores posibles           |
| -------------- | -------- | -------------------------------------------------------------------------------- | -------------------------- |
| `dni`          | Texto    | Identificador único del empleado. Se usa como clave para buscarlo en el sistema. | Numérico, ej. `12345678`   |
| `clave`        | Texto    | Contraseña utilizada para iniciar sesión.                                        | Alfanumérico, ej. `abc123` |
| `nombre`       | Texto    | Nombre y apellido del empleado.                                                  | Texto libre                |
| `es_jefe`      | Booleano | Indica si el empleado tiene permisos para aprobar licencias de otros usuarios.   | `True` / `False`           |
| `dias_anuales` | Entero   | Cantidad de días de licencia que el empleado tiene asignados por año.            | Numérico, ej. `15`, `20`   |

---

## Entidad: Licencia

**Archivo:** `licencias.csv`

| Campo           | Tipo   | Descripción                                                                                    | Valores posibles                                              |
| --------------- | ------ | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `id`            | Entero | Identificador único de la licencia. Se autogenera de forma incremental.                        | Numérico, ej. `1`, `2`, `3`                                   |
| `dni_empleado`  | Texto  | DNI del empleado que solicitó la licencia. Relaciona la licencia con la entidad Empleado.      | Numérico, debe existir en `empleados.csv`                     |
| `tipo`          | Texto  | Categoría de la licencia solicitada.                                                           | `vacaciones`, `enfermedad`, `estudio`, `duelo`                |
| `fecha_inicio`  | Fecha  | Primer día del período solicitado.                                                             | Formato `DD/MM/AAAA`                                          |
| `fecha_fin`     | Fecha  | Último día del período solicitado.                                                             | Formato `DD/MM/AAAA`, debe ser mayor o igual a `fecha_inicio` |
| `dias`          | Entero | Cantidad de días hábiles que abarca el período, excluyendo sábados y domingos.                 | Numérico, calculado automáticamente                           |
| `estado`        | Texto  | Situación actual de la licencia.                                                               | `pendiente`, `aprobada`, `anulada`                            |
| `dni_aprobador` | Texto  | DNI del jefe que aprobó la licencia. Permanece vacío mientras esté pendiente o si fue anulada. | Numérico o vacío (`""`)                                       |

---

## Relaciones entre entidades

* Una **Licencia** pertenece a un único **Empleado** mediante el campo `dni_empleado`, que referencia al campo `dni`.
* Una **Licencia** puede tener un **Empleado aprobador** distinto del solicitante mediante el campo `dni_aprobador`.
* El campo `dni_aprobador` solo se completa cuando la licencia fue aprobada por un usuario con `es_jefe = True`.
* Un **Empleado** puede tener múltiples **Licencias** asociadas a lo largo del tiempo.

---

## Variables calculadas en tiempo de ejecución

Estas variables no se almacenan directamente en los archivos CSV, pero se calculan a partir de ellos para tomar decisiones dentro del proceso.

| Variable             | Descripción                                                                                                 | Origen del cálculo                                          |
| -------------------- | ----------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `dias_comprometidos` | Suma de los días de todas las licencias pendientes o aprobadas de un empleado.                              | Recorrido de `licencias.csv`, filtrando por `dni_empleado`. |
| `dias_restantes`     | Días disponibles para nuevas solicitudes.                                                                   | `dias_anuales - dias_comprometidos`                         |
| `superposicion`      | Indica si el rango de fechas solicitado se cruza con otra licencia pendiente o aprobada del mismo empleado. | Comparación de rangos de fechas en `licencias.csv`.         |

---

## Constantes del sistema

| Constante               | Valor                                          | Uso                                                                                     |
| ----------------------- | ---------------------------------------------- | --------------------------------------------------------------------------------------- |
| `TIPOS_LICENCIA`        | `vacaciones`, `enfermedad`, `estudio`, `duelo` | Valida el campo `tipo` al dar de alta una licencia.                                     |
| `ESTADOS_COMPROMETIDOS` | `pendiente`, `aprobada`                        | Define qué licencias cuentan para el cálculo de saldo y la validación de superposición. |
