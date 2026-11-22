<?php
session_start();
// Verificamos que haya sesion iniciada y que sea admin
if (!isset($_SESSION['usuario_id']) || $_SESSION['rol'] !== 'admin') {
    echo "<div class='container mt-4'><div class='alert alert-danger'>Acceso denegado. Solo el administrador puede modificar tarifas. <a href='dashboard.php'>Volver</a></div></div>";
    exit;
}

require '../config/conexion.php';
include '../includes/header.php';

$mensaje = "";

// 1. update a price
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['tarifa_id'], $_POST['precio'])) {
    $tarifa_id = (int)$_POST['tarifa_id'];
    $nuevo_precio = (float)$_POST['precio'];

    if ($nuevo_precio > 0) {
        $stmtUpdate = $pdo->prepare("UPDATE tarifas SET precio = :precio WHERE tarifa_id = :tid");
        $stmtUpdate->execute(['precio' => $nuevo_precio, 'tid' => $tarifa_id]);
        $mensaje = "<div class='alert alert-success'>Tarifa #$tarifa_id actualizada correctamente a <b>$" . number_format($nuevo_precio, 2) . " MXN</b>.</div>";
    } else {
        $mensaje = "<div class='alert alert-warning'>El precio debe ser mayor a cero.</div>";
    }
}

// 2. CONSULTAR TODO
$sqlTarifas = "SELECT t.tarifa_id, ts.nombre AS servicio, COALESCE(tc.nombre, 'General') AS cliente, 
               t.hora_desde, t.hora_hasta, t.precio, t.unidad
               FROM tarifas t
               INNER JOIN tipos_servicio ts ON t.tipo_servicio_id = ts.tipo_servicio_id
               LEFT JOIN tipos_cliente tc ON t.tipo_cliente_id = tc.tipo_cliente_id
               ORDER BY t.tarifa_id ASC";
$tarifas = $pdo->query($sqlTarifas)->fetchAll(PDO::FETCH_ASSOC);
?>

<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h2>Administracion de Tarifas (Solo Admin)</h2>
        <a href="dashboard.php" class="btn btn-outline-secondary">Volver a Cajones</a>
    </div>

    <?= $mensaje ?>

    <div class="card shadow-sm">
        <div class="card-header bg-dark text-white">Tarifas Configuradas en el Sistema</div>
        <div class="card-body">
            <table class="table table-bordered align-middle">
                <thead class="table-light">
                    <tr>
                        <th>ID</th>
                        <th>Servicio</th>
                        <th>Tipo Cliente</th>
                        <th>Tramo de Horas</th>
                        <th>Precio Actual (MXN)</th>
                        <th>Accion</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($tarifas as $t): ?>
                        <tr>
                            <td>#<?= $t['tarifa_id'] ?></td>
                            <td><?= ucfirst($t['servicio']) ?></td>
                            <td>
                                <span class="badge <?= $t['cliente'] == 'frecuente' ? 'bg-info text-dark' : 'bg-secondary' ?>">
                                    <?= ucfirst($t['cliente']) ?>
                                </span>
                            </td>
                            <td>
                                <?php 
                                if ($t['hora_hasta'] !== null) {
                                    echo "De la hora {$t['hora_desde']} a la {$t['hora_hasta']}";
                                } else {
                                    echo "De la hora {$t['hora_desde']} en adelante";
                                }
                                ?>
                            </td>
                            <td>
                                <form method="POST" class="d-flex gap-2">
                                    <input type="hidden" name="tarifa_id" value="<?= $t['tarifa_id'] ?>">
                                    <div class="input-group input-group-sm" style="max-width: 150px;">
                                        <span class="input-group-text">$</span>
                                        <input type="number" step="0.01" name="precio" class="form-control" value="<?= $t['precio'] ?>" required>
                                    </div>
                            </td>
                            <td>
                                    <button type="submit" class="btn btn-primary btn-sm">Guardar Cambio</button>
                                </form>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<?php include '../includes/footer.php'; ?>