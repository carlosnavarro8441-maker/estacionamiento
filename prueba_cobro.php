<?php
function calcularCobro($horas, $tipo_cliente) {
    $total = 0;
    $desglose = [];

    //cobrar 1 hora
    if ($horas < 1) {
        $horas = 1;
    }

    if ($tipo_cliente == 'paso') {
        // Regla cliente de paso: $30 las primeras 5 horas, $25 de la hora 6 en adelante
        if ($horas <= 5) {
            $total = $horas * 30;
            $desglose[] = "$horas hrs x $30.00 = $" . ($horas * 30);
        } else {
            $horas_extra = $horas - 5;
            $subtotal1 = 5 * 30; // Siempre serán $150 por las primeras 5
            $subtotal2 = $horas_extra * 25;
            $total = $subtotal1 + $subtotal2;
            
            $desglose[] = "5 hrs normales x $30.00 = $$subtotal1";
            $desglose[] = "$horas_extra hrs extra x $25.00 = $$subtotal2";
        }
    } elseif ($tipo_cliente == 'frecuente') {
        // Regla cliente frecuente: $26 las primeras 5 horas, $22 de la hora 6 en adelante
        if ($horas <= 5) {
            $total = $horas * 26;
            $desglose[] = "$horas hrs x $26.00 = $" . ($horas * 26);
        } else {
            $horas_extra = $horas - 5;
            $subtotal1 = 5 * 26; // Siempre serán $130 por las primeras 5
            $subtotal2 = $horas_extra * 22;
            $total = $subtotal1 + $subtotal2;
            
            $desglose[] = "5 hrs normales x $26.00 = $$subtotal1";
            $desglose[] = "$horas_extra hrs extra x $22.00 = $$subtotal2";
        }
    }

    return [
        'total' => $total,
        'desglose' => $desglose
    ];
}

// --- PRUEBAS AUTOMÁTICAS 
echo "<h2>Pruebas de Cobro </h2>";

$casos_prueba = [
    ['horas' => 1, 'tipo' => 'paso'],
    ['horas' => 5, 'tipo' => 'paso'],
    ['horas' => 6, 'tipo' => 'paso'],
    ['horas' => 7, 'tipo' => 'paso'],
    ['horas' => 1, 'tipo' => 'frecuente'],
    ['horas' => 5, 'tipo' => 'frecuente'],
    ['horas' => 6, 'tipo' => 'frecuente'],
    ['horas' => 7, 'tipo' => 'frecuente'],
];

foreach ($casos_prueba as $caso) {
    $resultado = calcularCobro($caso['horas'], $caso['tipo']);
    echo "<b>Cliente {$caso['tipo']} ({$caso['horas']} hrs):</b> Total = <b>\${$resultado['total']}.00 MXN</b><br>";
    foreach ($resultado['desglose'] as $linea) {
        echo " &nbsp;&nbsp; - $linea <br>";
    }
    echo "<hr>";
}
?>