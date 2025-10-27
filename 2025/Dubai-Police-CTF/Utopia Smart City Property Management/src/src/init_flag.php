<?php
require __DIR__ . '/includes/db.php';

$flag = getenv('FLAG');
if (!$flag) {
    $flag = 'FLAG{fa2e}'; 
}

function randomHexString($len) {
    return bin2hex(random_bytes($len / 2));
}


$stmt = $conn->prepare("UPDATE users SET password = ? WHERE username = 'admin'");
$stmt->bind_param("s", randomHexString(32));
$stmt->execute();
$stmt->close();


$stmt= $conn->prepare("INSERT INTO flags (flag) VALUES (?) ON DUPLICATE KEY UPDATE flag=VALUES(flag)");
$stmt->bind_param("s", $flag);
$stmt->execute();
$stmt->close();

?>
