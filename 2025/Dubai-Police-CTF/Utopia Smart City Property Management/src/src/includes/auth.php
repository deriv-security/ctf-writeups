<?php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);

require_once 'db.php';

class SessionManager {
    public static function start() {
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }
    }
    
    public static function isLoggedIn() {
        return isset($_SESSION['username']);
    }
    
    public static function requireLogin() {
        if (!self::isLoggedIn()) {
            header('Location: login.php');
            exit();
        }
    }
    
    public static function setUser($username) {
        $_SESSION['username'] = $username;
    }
    
    public static function getUsername() {
        return $_SESSION['username'] ?? null;
    }
    
    public static function isAdmin() {
        $username = self::getUsername();
        return $username === 'admin';
    }
    
    public static function logout() {
        session_destroy();
    }
}

function authenticate_user($username, $password) {
    global $conn;

    $sql = "SELECT * FROM users WHERE username = ? AND password = ?";
    if ($stmt = $conn->prepare($sql)) {
        $stmt->bind_param('ss', $username, $password);
        if ($stmt->execute()) {
            $res = $stmt->get_result();
            $row = $res->fetch_assoc();
            $stmt->close();
            return $row ? $row : false;
        }
        $stmt->close();
    }

    return false;
}

?>
