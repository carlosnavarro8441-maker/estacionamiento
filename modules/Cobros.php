<?php
session_start();
if (!isset($_SESSION['usuario_id'])) {
    header("Location: ../index.php");
    exit;
}

require '../config/conexion.php';
include '../includes/header.php';

// --- FUNCION DE CALCULO DINAMICA (Lee los precios reales de la BD) ---
function calcularCobro($pdo, $horas, $tipo_cliente) {
    $total = 0;
    $desglose = [];

    if ($horas < 1) {
        $horas = 1;
    }

    // Consultamos los precios actuales de la tabla tarifas
    $stmtTarifas = $pdo->query("SELECT tarifa_id, precio FROM tarifas");
    $precios = $stmtTarifas->fetchAll(PDO::FETCH_KEY_PAIR); // Crea un arreglo [tarifa_id => precio]

    // Asignamos los precios segun lo que haya en la BD (o usamos los base por respaldo)
    $p_paso_normal = $precios[1] ?? 30.00;
    $p_paso_extra  = $precios[2] ?? 25.00;
    $p_frec_normal = $precios[3] ?? 26.00;
    $p_frec_extra  = $precios[4] ?? 22.00;

    if ($tipo_cliente == 'paso') {
        if ($horas <= 5) {
            $total = $horas * $p_paso_normal;
            $desglose[] = ['tarifa_id' => 1, 'horas' => $horas, 'precio' => $p_paso_normal, 'subtotal' => $total, 'texto' => "$horas hrs x $$p_paso_normal = $$total"];
        } else {
            $horas_extra = $horas - 5;
            $sub1 = 5 * $p_paso_normal;
            $sub2 = $horas_extra * $p_paso_extra;
            $total = $sub1 + $sub2;
            $desglose[] = ['tarifa_id' => 1, 'horas' => 5, 'precio' => $p_paso_normal, 'subtotal' => $sub1, 'texto' => "5 hrs normales x $$p_paso_normal = $$sub1"];
            $desglose[] = ['tarifa_id' => 2, 'horas' => $horas_extra, 'precio' => $p_paso_extra, 'subtotal' => $sub2, 'texto' => "$horas_extra hrs extra x $$p_paso_extra = $$sub2"];
        }
    } elseif ($tipo_cliente == 'frecuente') {
        if ($horas <= 5) {
            $total = $horas * $p_frec_normal;
            $desglose[] = ['tarifa_id' => 3, 'horas' => $horas, 'precio' => $p_frec_normal, 'subtotal' => $total, 'texto' => "$horas hrs x $$p_frec_normal = $$total"];
        } else {
            $horas_extra = $horas - 5;
            $sub1 = 5 * $p_frec_normal;
            $sub2 = $horas_extra * $p_frec_extra;
            $total = $sub1 + $sub2;
            $desglose[] = ['tarifa_id' => 3, 'horas' => 5, 'precio' => $p_frec_normal, 'subtotal' => $sub1, 'texto' => "5 hrs normales x $$p_frec_normal = $$sub1"];
            $desglose[] = ['tarifa_id' => 4, 'horas' => $horas_extra, 'precio' => $p_frec_extra, 'subtotal' => $sub2, 'texto' => "$horas_extra hrs extra x $$p_frec_extra = $$sub2"];
        }
    }

    return ['total' => $total, 'desglose' => $desglose];
}

// Verificamos que nos hayan mandado un servicio_id desde el boton de dashboard
if (!isset($_GET['servicio_id']) && !isset($_POST['servicio_id'])) {
    echo "<div class='container mt-4'><div class='alert alert-warning'>Selecciona un vehiculo desde <a href='dashboard.php'>Inicio / Cajones</a> para cobrar.</div></div>";
    include '../includes/footer.php';
    exit;
}

$servicio_id = $_GET['servicio_id'] ?? $_POST['servicio_id'];

// Buscamos el servicio vehiculo y si su cliente es frecuente o de paso
$sql = "SELECT s.servicio_id, s.fecha_hora_entrada, v.matricula,
        COALESCE(tc.nombre, 'paso') AS tipo_cliente,
        CEIL(TIMESTAMPDIFF(SECOND, s.fecha_hora_entrada, NOW()) / 3600) AS horas_transcurridas
        FROM servicios s
        INNER JOIN vehiculos v ON s.vehiculo_id = v.vehiculo_id
        LEFT JOIN clientes c ON v.cliente_id = c.cliente_id
        LEFT JOIN tipos_cliente tc ON c.tipo_cliente_id = tc.tipo_cliente_id
        WHERE s.servicio_id = :sid AND s.fecha_hora_salida IS NULL LIMIT 1";
$stmt = $pdo->prepare($sql);
$stmt->execute(['sid' => $servicio_id]);
$servicio = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$servicio) {
    echo "<div class='container mt-4'><div class='alert alert-danger'>Este servicio no existe o ya fue cobrado. <a href='dashboard.php'>Volver</a></div></div>";
    include '../includes/footer.php';
    exit;
}

// horas (minimo 1 hora si acaba de entrar)
$horas_a_cobrar = max(1, (int)$servicio['horas_transcurridas']);
$calculo = calcularCobro($pdo, $horas_a_cobrar, $servicio['tipo_cliente']);

// --- Presiono boton cobro ---
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['confirmar_cobro'])) {
    $metodo_pago_id = $_POST['metodo_pago_id'];
    $usuario_id = $_SESSION['usuario_id'];

    // 1.servuce close
    $stmtSalida = $pdo->prepare("UPDATE servicios SET fecha_hora_salida = NOW(), usuario_salida_id = :uid WHERE servicio_id = :sid");
    $stmtSalida->execute(['uid' => $usuario_id, 'sid' => $servicio_id]);

    // 2. save  la tabla cobros
    $stmtCobro = $pdo->prepare("INSERT INTO cobros (servicio_id, horas_cobradas, monto_total, fecha_hora_cobro, metodo_pago_id, usuario_id) VALUES (:sid, :hrs, :tot, NOW(), :mpid, :uid)");
    $stmtCobro->execute([
        'sid' => $servicio_id,
        'hrs' => $horas_a_cobrar,
        'tot' => $calculo['total'],
        'mpid' => $metodo_pago_id,
        'uid' => $usuario_id
    ]);
    $cobro_id = $pdo->lastInsertId();

    // 3. Save en la tabla cobros_detalle
    $stmtDetalle = $pdo->prepare("INSERT INTO cobros_detalle (cobro_id, tarifa_id, horas, precio_hora_aplicado, subtotal) VALUES (:cid, :tid, :hrs, :precio, :sub)");
    foreach ($calculo['desglose'] as $item) {
        $stmtDetalle->execute([
            'cid' => $cobro_id,
            'tid' => $item['tarifa_id'],
            'hrs' => $item['horas'],
            'precio' => $item['precio'],
            'sub' => $item['subtotal']
        ]);
    }

    echo "<div class='container mt-4'>
            <div class='alert alert-success'>
                <h4>Cobro registrado con exito</h4>
                <p>El vehiculo <b>{$servicio['matricula']}</b> ha salido del estacionamiento. Total cobrado: <b>\${$calculo['total']}.00 MXN</b></p>
                <a href='dashboard.php' class='btn btn-primary'>Volver a Entradas / Cajones</a>
            </div>
          </div>";
    include '../includes/footer.php';
    exit;
}
?>

<div class="container mt-4">
    <div class="card shadow" style="max-width: 600px; margin: auto;">
        <div class="card-header bg-success text-white">
            <h4 class="mb-0">Resumen de Salida y Cobro</h4>
        </div>
        <div class="card-body">
            <p><strong>Folio Servicio:</strong> #<?= $servicio['servicio_id'] ?></p>
            <p><strong>Matricula:</strong> <?= $servicio['matricula'] ?></p>
            <p><strong>Tipo de Cliente:</strong> <?= ucfirst($servicio['tipo_cliente']) ?></p>
            <p><strong>Hora de Entrada:</strong> <?= $servicio['fecha_hora_entrada'] ?></p>
            <p><strong>Tiempo a Cobrar:</strong> <?= $horas_a_cobrar ?> hora(s)</p>
            
            <hr>
            <h5>Desglose de Tarifa:</h5>
            <ul>
                <?php foreach ($calculo['desglose'] as $linea): ?>
                    <li><?= $linea['texto'] ?></li>
                <?php endforeach; ?>
            </ul>

            <div class="alert alert-secondary text-center my-3">
                <span class="text-muted d-block">TOTAL A PAGAR</span>
                <h1 class="display-4 fw-bold text-dark mb-0">$<?= number_format($calculo['total'], 2) ?> MXN</h1>
            </div>

            <form method="POST">
                <input type="hidden" name="servicio_id" value="<?= $servicio['servicio_id'] ?>">
                
                <div class="mb-3">
                    <label class="form-label fw-bold">Metodo de Pago:</label>
                    <select name="metodo_pago_id" class="form-select" required>
                        <option value="1">Efectivo</option>
                        <option value="2">Tarjeta</option>
                    </select>
                </div>

                <div class="d-flex justify-content-between">
                    <a href="dashboard.php" class="btn btn-outline-secondary">Cancelar</a>
                    <button type="submit" name="confirmar_cobro" class="btn btn-success btn-lg">Confirmar y Cobrar</button>
                </div>
            </form>
        </div>
    </div>
</div>

<?php include '../includes/footer.php'; ?>