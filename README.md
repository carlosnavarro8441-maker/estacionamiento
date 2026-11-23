# Sistema de Estacionamiento Público

Proyecto final de Base de datos. Tiene dos partes que usan la misma base de datos MySQL/MariaDB:

- **`python_app/`**: aplicación de escritorio (patrón MVC: `modelos/`, `vistas/`, `controladores/`). Es la aplicación completa.
- **Web en PHP** (`index.php` y `modules/`): entradas y salidas, cobros y tarifas.

## Instalación

1. Enciende **MySQL** (por ejemplo desde XAMPP) y abre `http://localhost/phpmyadmin`.
2. Crea la base de datos **`estacionamiento_publico`** e importa, **en este orden**:
   1. `database/estacionamiento_publico.sql`
   2. `database/restricciones.sql` (reglas: una entrada abierta por vehículo, salida posterior a la entrada, una pensión activa por vehículo)
   3. `database/ajustes_finales.sql` (tarifas del PDF, nombres de servicio y valores de la pensión)
3. Inicia sesión con **usuario `admin`** y **contraseña `12345`**. Al entrar, la contraseña se guarda cifrada (bcrypt).
4. El administrador crea el usuario cobrador desde **Usuarios**.

### Aplicación de escritorio (Python)

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

### Versión web (PHP)

Copia el proyecto dentro de `htdocs` y entra a `http://localhost/Estacionamiento`.

## Perfiles de usuario

| Perfil | Puede hacer |
|---|---|
| **admin** | Todo: entradas y salidas, clientes, vehículos, pensiones, tarifas, usuarios y reportes |
| **cobrador** | Registrar vehículos, entradas y salidas (con su cobro) y datos de clientes |

## Reglas de cobro (requisito 5)

| Cliente | Horas 1 a 5 | Hora 6 en adelante |
|---|---|---|
| De paso | $30.00 por hora | $25.00 por hora |
| Frecuente | $26.00 por hora | $22.00 por hora |

Una fracción de hora cuenta como hora completa y siempre se cobra mínimo 1 hora. Los precios viven en la tabla `tarifas` y el administrador los cambia desde la pantalla **Tarifas**.

## Pensiones (requisito 6)

Se controlan por fecha y por vehículo. Las pensiones con **más de 2 años** de antigüedad reciben el descuento de la tabla `descuentos_pension`. El precio mensual y el porcentaje de descuento se configuran en la pantalla **Tarifas** (`ajustes_finales.sql` trae valores de ejemplo).

## Reportes (requisitos 7 a 10, pantalla Reportes, con selector de año)

- Entradas y salidas por mes
- Meses con mayor demanda
- Horarios con mayor demanda
- Ingresos por servicio (cajón y pensión)
