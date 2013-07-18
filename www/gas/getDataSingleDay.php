<?php 

include 'checkinput.php';

$year = $_GET["year"];
$month = $_GET["month"];
$day = $_GET["day"];
checkyear($year);
checkmonth($month);   
checkday($day);

if (($handle = fopen("/usr/local/P1tools/database/$year/$month/$day.gas", 'r')) === false) {
    return;
}
// Ignore first row with headers
fgetcsv($handle, 1024, ';');
$table = array();
$table['cols'] = array(
   // Labels for the chart
   array('label' => 'Dag', 'type' => 'datetime'),
   array('label' => 'Verbruik', 'type' => 'number'),
   );

$rows = array();
while ($r = fgetcsv($handle, 1024, ';')) {
    $temp = array();
    $temp[] = array('v' => $r[0]);
    $temp[] = array('v' => floatval($r[2]));
    $rows[] = array('c' => $temp);
}
fclose($handle);

$table['rows'] = $rows;

echo json_encode($table);

// Instead you can query your database and parse into JSON etc etc
?>
