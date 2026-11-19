<?php
session_start();
require 'config/conexion.php';

if (isset($_SESSION['usuario_id'])) {
    header("Location: modules/dashboard.php");
    exit;
}

$error = "";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username']);
    $password = trim($_POST['password']);

    $sql = "SELECT u.*, p.nombre AS rol 
            FROM usuarios u 
            INNER JOIN perfiles p ON u.perfil_id = p.perfil_id 
            WHERE u.username = :username AND u.activo = 1 LIMIT 1";
    $stmt = $pdo->prepare($sql);
    $stmt->execute(['username' => $username]);
    $usuario = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($usuario && $password === $usuario['password_hash']) {
        $_SESSION['usuario_id'] = $usuario['usuario_id'];
        $_SESSION['nombre']     = $usuario['nombre'];
        $_SESSION['rol']        = $usuario['rol'];
        header("Location: modules/dashboard.php");
        exit;
    } else {
        $error = "Usuario o contraseña incorrectos.";
    }
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Acceso - Estacionamiento Público</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light d-flex align-items-center justify-content-center" style="height: 100vh;">
    <div class="card shadow p-4" style="width: 100%; max-width: 400px;">
        <h3 class="text-center mb-3">Estacionamiento</h3>
        <p class="text-muted text-center small">Ingresa con tu cuenta de sistema</p>

        <?php if ($error): ?>
            <div class="alert alert-danger py-2"><?= $error ?></div>
        <?php endif; ?>

        <form method="POST">
            <div class="mb-3">
                <label class="form-label">Usuario</label>
                <input type="text" name="username" class="form-control" placeholder="Ej. admin" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Contraseña</label>
                <input type="password" name="password" class="form-control" placeholder="Ej. 12345" required>
            </div>
            <button type="submit" class="btn btn-primary w-100">Entrar</button>
        </form>
    </div>
</body>
</html>