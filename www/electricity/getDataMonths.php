<?php 

include 'checkinput.php';

$year = $_GET["year"];
checkyear($year);

if (($handle = fopen("/usr/local/P1tools/database/$year/maand.stroom", 'r')) === false) {
    return;
}
// Ignore first row with headers
fgetcsv($handle, 1024, ';');
$table = array();
$table['cols'] = array(
   // Labels for the chart
   array('label' => 'Maand', 'type' => 'string'),
   array('label' => 'Verbruik laag', 'type' => 'number'),
   array('label' => 'Verbruik hoog', 'type' => 'number'),
   array('label' => 'Levering laag', 'type' => 'number'),
   array('label' => 'Levering hoog', 'type' => 'number')
   );

$rows = array();
while ($r = fgetcsv($handle, 1024, ';')) {
    $temp = array();
    $temp[] = array('v' => $r[0]);
    $temp[] = array('v' => floatval($r[11]));
    $temp[] = array('v' => floatval($r[12]));
    $temp[] = array('v' => floatval(-$r[13]));
    $temp[] = array('v' => floatval(-$r[14]));
    $rows[] = array('c' => $temp);
}
fclose($handle);

$table['rows'] = $rows;

echo json_encode($table);

// Instead you can query your database and parse into JSON etc etc
?>
