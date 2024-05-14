<?php

$command = escapeshellcmd('/var/www/html/ValveOn.py');
$output = shell_exec($command);
echo $output;

?>
