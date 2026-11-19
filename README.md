#Sistema de Estacionamiento Público

## Cómo ponerlo a funcionar en tu computadora
1. Clona este repositorio dentro de tu carpeta `htdocs` de XAMPP.
2. Inicia **Apache** y **MySQL** en XAMPP.
3. Entra a `http://localhost/phpmyadmin`, crea una base de datos llamada `estacionamiento_publico` e importa el archivo `database/estacionamiento_publico.sql`.
4. Ve a la carpeta `config/`, copia `conexion.example.php` y cámbiale el nombre a `conexion.php` (ajusta tu usuario/contraseña de MySQL si tienes).
5. Abre `http://localhost/Estacionamiento/` en tu navegador (Usuario de prueba: `admin` / Contraseña: `12345`).
