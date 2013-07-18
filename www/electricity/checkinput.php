<?php 

function checkyear($year) {
   if (!preg_match_all('/^\d+$/',$year) || (intval($year < 2000)) || (intval($year > 2100))) {
      die('Wrong input for year');
   }
}

function checkmonth($month) {
   if (!preg_match_all('/^\d+$/',$month) || (intval($month < 1)) || (intval($month > 12))) {
      die('Wrong input for month');
   }
}

function checkday($day) {
  if (!preg_match_all('/^\d+$/',$day) || (intval($day < 1)) || (intval($day > 31))) {
      die('Wrong input for day');
   }
}

?>
