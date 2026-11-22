<?php
session_start();
// Si no  iniciado, lo regresamos al login
if (!isset($_SESSION['usuario_id'])) {
    header("Location: ../index.php");
    exit;
}

require '../config/conexion.php'; 
include '../includes/header.php';

$mensaje = "";

// 1. log para registro del vehiculo
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['matricula'])) {
    $matricula = strtoupper(trim($_POST['matricula']));
    $usuario_id = $_SESSION['usuario_id'];

    // Buscamos si el vehiculo ya existe en la tabla vehiculos
    $stmt = $pdo->prepare("SELECT vehiculo_id FROM vehiculos WHERE matricula = :mat LIMIT 1");
    $stmt->execute(['mat' => $matricula]);
    $vehiculo = $stmt->fetch(PDO::FETCH_ASSOC);

    // Si el carro nunca ha venido (cliente de paso nuevo), lo registramos
    if (!$vehiculo) {
        $stmtInsertVeh = $pdo->prepare("INSERT INTO vehiculos (matricula, marca, modelo, color, cliente_id) VALUES (:mat, 'Por definir', 'Por definir', 'Por definir', NULL)");
        $stmtInsertVeh->execute(['mat' => $matricula]);
        $vehiculo_id = $pdo->lastInsertId();
    } else {
        $vehiculo_id = $vehiculo['vehiculo_id'];
    }

    // Verificamos que no tenga ya una entrada abierta (sin fecha_hora_salida)
    $stmtCheck = $pdo->prepare("SELECT servicio_id FROM servicios WHERE vehiculo_id = :vid AND fecha_hora_salida IS NULL");
    $stmtCheck->execute(['vid' => $vehiculo_id]);

    if ($stmtCheck->fetch()) {
        $mensaje = "<div class='alert alert-warning'>El vehiculo con matricula <b>$matricula</b> ya se encuentra dentro del estacionamiento.</div>";
    } else {
        //  la entrada tabla servicios (tipo_servicio_id = 1 es 'cajon')
        $stmtEntrada = $pdo->prepare("INSERT INTO servicios (vehiculo_id, tipo_servicio_id, fecha_hora_entrada, usuario_entrada_id) VALUES (:vid, 1, NOW(), :uid)");
        $stmtEntrada->execute(['vid' => $vehiculo_id, 'uid' => $usuario_id]);
        $mensaje = "<div class='alert alert-success'>-Entrada registrada para <b>$matricula</b>!</div>";
    }
}

// 2. Consulta ara ver qn esta dentro
$sqlActivos = "SELECT s.servicio_id, v.matricula, s.fecha_hora_entrada, 
               COALESCE(tc.nombre, 'paso') AS tipo_cliente
               FROM servicios s
               INNER JOIN vehiculos v ON s.vehiculo_id = v.vehiculo_id
               LEFT JOIN clientes c ON v.cliente_id = c.cliente_id
               LEFT JOIN tipos_cliente tc ON c.tipo_cliente_id = tc.tipo_cliente_id
               WHERE s.fecha_hora_salida IS NULL
               ORDER BY s.fecha_hora_entrada DESC";
$vehiculosActivos = $pdo->query($sqlActivos)->fetchAll(PDO::FETCH_ASSOC);
?>

<div class="container mt-4">
    <h2 class="mb-4">Control de Entradas y Cajones</h2>
    
    <?= $mensaje ?>

    <!-- Formulario de Entrada -->
    <div class="card shadow-sm mb-4">
        <div class="card-header bg-dark text-white">Registrar Nueva Entrada</div>
        <div class="card-body">
            <form method="POST" class="row g-3 align-items-center">
                <div class="col-auto">
                    <label class="col-form-label fw-bold">Matricula / Placas:</label>
                </div>
                <div class="col-auto">
                    <input type="text" name="matricula" class="form-control text-uppercase" placeholder="Ej. JLA1234" maxlength="7" required>
                </div>
                <div class="col-auto">
                    <button type="submit" class="btn btn-primary">Registrar Entrada</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Tabla de Vehiculos Estacionados Actualmente -->
    <div class="card shadow-sm">
        <div class="card-header bg-secondary text-white">Vehiculos Actualmente en Estacionamiento</div>
        <div class="card-body">
            <table class="table table-bordered table-hover">
                <thead class="table-light">
                    <tr>
                        <th>Folio</th>
                        <th>Matricula</th>
                        <th>Tipo Cliente</th>
                        <th>Hora de Entrada</th>
                        <th>Accion</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (count($vehiculosActivos) > 0): ?>
                        <?php foreach ($vehiculosActivos as $auto): ?>
                            <tr>
                                <td>#<?= $auto['servicio_id'] ?></td>
                                <td class="fw-bold"><?= $auto['matricula'] ?></td>
                                <td>
                                    <span class="badge <?= $auto['tipo_cliente'] == 'frecuente' ? 'bg-info text-dark' : 'bg-secondary' ?>">
                                        <?= ucfirst($auto['tipo_cliente']) ?>
                                    </span>
                                </td>
                                <td><?= $auto['fecha_hora_entrada'] ?></td>
                                <td>
                                    <!-- a laasegunda pantalla cobros -->
                                    <a href="Cobros.php?servicio_id=<?= $auto['servicio_id'] ?>" class="btn btn-success btn-sm">
                                        Dar Salida y Cobrar
                                    </a>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php else: ?>
                        <tr>
                            <td colspan="5" class="text-center text-muted">No hay vehiculos estacionados en este momento.</td>
                        </tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>
</div>

<?php include '../includes/footer.php'; ?>