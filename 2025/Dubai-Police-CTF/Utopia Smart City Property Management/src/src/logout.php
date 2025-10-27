<?php
require_once './includes/auth.php';

SessionManager::start();
SessionManager::logout();

header('Location: login.php');
exit();
?>
