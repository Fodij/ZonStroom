<?php 

include 'checkinput.php';

if (($handle = fopen("/usr/local/P1tools/database/jaar.gas", 'r')) === false) {
    return;
}
// Ignore first row with headers
fgetcsv($handle, 1024, ';');
$table = array();
$table['cols'] = array(
   // Labels for the chart
   array('label' => 'Jaar', 'type' => 'string'),
   array('label' => 'Verbruik laag', 'type' => 'number')
   );

$rows = array();
while ($r = fgetcsv($handle, 1024, ';')) {
    $temp = array();
    $temp[] = array('v' => $r[0]);
    $temp[] = array('v' => floatval($r[5]));
    $rows[] = array('c' => $temp);
}
fclose($handle);

$table['rows'] = $rows;

echo json_encode($table);

// Instead you can query your database and parse into JSON etc etc
?>
