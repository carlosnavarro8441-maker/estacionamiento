# Sistema de Estacionamiento Público

## Instalación rápida (4 pasos)
1. Descarga o clona este repositorio dentro de tu carpeta `htdocs` de XAMPP.
2. Enciende **Apache** y **MySQL** en XAMPP.
3. Abre `http://localhost/phpmyadmin`, crea la base de datos **`estacionamiento_publico`** e importa **`database/estacionamiento_publico.sql`**.
4. Entra en tu navegador a `http://localhost/Estacionamiento` e inicia sesión con:
   - **Usuario:** `admin`
   - **Contraseña:** `12345`

## División de módulos (`modules/`)
- `dashboard.php` -> Control de entradas y salidas
- `cobros.php` -> Cálculo de tarifas y pagos
- `pensiones.php` -> Clientes frecuentes y mensualidades
