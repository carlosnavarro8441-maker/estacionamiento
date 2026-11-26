# Sistema de Estacionamiento Público

Proyecto final de Base de datos. Tiene dos partes que usan la misma base de datos MySQL/MariaDB:

- **`python_app/`**: aplicación de escritorio (patrón MVC: `modelos/`, `vistas/`, `controladores/`). Es la aplicación completa.
- **Web en PHP** (`index.php` y `modules/`): entradas y salidas, cobros y tarifas.

La aplicación de escritorio incluye: login con perfiles, clientes, vehículos con historial, entradas y salidas con cobro, pensiones, reportes, administración de usuarios, **control de capacidad** y **mapa de cajones**.

## Instalación

1. Enciende MySQL (por ejemplo desde XAMPP) y abre `http://localhost/phpmyadmin`.
2. Crea la base de datos `estacionamiento_publico` e importa, **en este orden** (con el juego de caracteres del archivo en **utf-8**):

| # | Archivo | Para qué sirve |
|---|---|---|
| 1 | `database/estacionamiento_publico.sql` | Tablas y datos de prueba |
| 2 | `database/restricciones.sql` | Reglas: una entrada abierta por vehículo, salida posterior a la entrada, una pensión activa por vehículo |
| 3 | `database/ajustes_finales.sql` | Tarifas del PDF, nombres de servicio y valores de la pensión |
| 4 | `database/capacidad.sql` | Tabla `configuracion` (capacidad total del estacionamiento) |
| 5 | `database/cajones.sql` | Tabla `cajones` y columna `servicios.cajon_id` |

`capacidad.sql` y `cajones.sql` van **después** de `ajustes_finales.sql`. Se pueden volver a importar sin problema (XAMPP usa MariaDB).

3. Inicia sesión con usuario `admin` y contraseña `12345`. Al entrar, la contraseña se guarda cifrada (bcrypt).
4. El administrador crea el usuario `cobrador` desde **Usuarios**.

## Aplicación de escritorio (Python)

```
cd python_app
pip install -r requirements.txt
copy config_ejemplo.py config.py     (y ajusta los datos de conexión si hace falta)
python main.py
```

Pruebas automáticas (desde `python_app/`):

```
python -m unittest pruebas.test_cobros pruebas.test_pensiones
python pruebas/test_permisos.py
```

## Capacidad y cajones

**Capacidad.** El administrador define cuántos vehículos caben en la pantalla **Capacidad**. El número se guarda en la tabla `configuracion` (clave `capacidad_total`). La pantalla muestra capacidad, ocupados y disponibles, con una barra verde, amarilla (80 % o más) o roja (lleno). Reglas al cambiarla:

- Debe ser un número entero mayor a 0.
- No puede ser menor a los vehículos que están dentro.
- No se puede reducir si un cajón que desaparecería está ocupado.

Un espacio está **ocupado** cuando existe un servicio sin `fecha_hora_salida` (de cajón o de pensión). Si no hay capacidad configurada, no se bloquea ninguna entrada. En la barra superior del menú, todos los usuarios ven **«Espacios libres: X de Y»** o **«ESTACIONAMIENTO LLENO»**.

**Cajones.** Se generan solos del 1 al total de la capacidad. La pantalla **Cajones** muestra un mapa (verde = libre, rojo = ocupado, con la matrícula) y permite **asignar** o **quitar** el cajón de un vehículo que está dentro. Elegir cajón es opcional, y al registrar la salida el cajón se libera solo.

**Funciones disponibles para otros módulos** (por ejemplo, Entradas y salidas):

| Función | Archivo | Qué hace |
|---|---|---|
| `hay_espacio()` | `controladores/capacidad_controlador.py` | Devuelve `(True/False, mensaje)`. Si es `False`, no se debe registrar la entrada |
| `espacios_disponibles()` | `controladores/capacidad_controlador.py` | Cuántos lugares quedan (o `None` si no hay límite) |
| `obtener_estado()` | `controladores/capacidad_controlador.py` | Capacidad, ocupados, disponibles y si está lleno |
| `listar_cajones_libres()` | `controladores/cajon_controlador.py` | Cajones libres para una lista desplegable |
| `validar_cajon(cajon_id)` | `controladores/cajon_controlador.py` | Revisa que el cajón exista y esté libre (`None` = sin cajón, permitido) |
| `asignar_cajon(servicio_id, cajon_id)` | `controladores/cajon_controlador.py` | Asigna o quita (con `None`) el cajón de un vehículo que está dentro |

Como la tabla `servicios` ahora tiene la columna `cajon_id`, todo `INSERT INTO servicios` debe llevar la **lista de columnas**.

**Cambios en la base de datos** (no están en `estacionamiento_publico.sql`):

| Objeto | Detalle |
|---|---|
| Tabla `configuracion` | `clave` (PK), `valor` |
| Tabla `cajones` | `cajon_id` (PK), `numero` (único), `activo` |
| Columna `servicios.cajon_id` | Opcional; llave foránea a `cajones.cajon_id` |

## Vehículos

La pantalla **Vehículos** muestra cuántas **visitas** tiene cada uno y su **estado** (Dentro, Fuera o Sin visitas), con un filtro para ver los que están dentro, los que tienen visitas o los que no tienen historial. Un vehículo solo se puede **eliminar** si nunca tuvo visitas ni pensiones, para conservar el historial de cobros. Los clientes no se borran: se dan de baja.

## Versión web (PHP)

Copia el proyecto dentro de `htdocs` y entra a `http://localhost/Estacionamiento`. La versión web todavía no usa la capacidad ni los cajones.

## Perfiles de usuario

| Perfil | Puede hacer |
|---|---|
| admin | Todo: entradas y salidas, clientes, vehículos, cajones, capacidad, pensiones, tarifas, usuarios y reportes |
| cobrador | Registrar vehículos, entradas y salidas (con su cobro), datos de clientes, y ver y asignar cajones |

## Reglas de cobro (requisito 5)

| Cliente | Horas 1 a 5 | Hora 6 en adelante |
|---|---|---|
| De paso | $30.00 por hora | $25.00 por hora |
| Frecuente | $26.00 por hora | $22.00 por hora |
