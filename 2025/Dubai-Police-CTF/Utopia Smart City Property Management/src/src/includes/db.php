<?php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);

$h = getenv('DB_HOST');
$u = getenv('DB_USER');
$p = getenv('DB_PASS');
$n = getenv('DB_NAME');
$conn = new mysqli($h, $u, $p, $n);
if ($conn->connect_error) {
    exit;
}
