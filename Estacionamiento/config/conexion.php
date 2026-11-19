<?php
$host = "localhost";
$db   = "estacionamiento_publico";
$user = "root";
$pass = ""; // En XAMPP por defecto va vacío. Si tienes clave, escríbela aquí.

try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=utf8mb4", $user, $pass);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("<div style='font-family:sans-serif; padding:20px; border:2px solid red;'>
            <h3>⚠️ Error de conexión a la Base de Datos</h3>
            <p>1. Verifica que <b>MySQL</b> esté encendido en tu XAMPP.</p>
            <p>2. Asegúrate de haber creado la base de datos <b>estacionamiento_publico</b> e importado el archivo de la carpeta <code>database/</code>.</p>
            <p>3. Si tu MySQL tiene contraseña, agrégala en <code>config/conexion.php</code>.</p>
            <small>Detalle técnico: " . $e->getMessage() . "</small>
         </div>");
}
?>
