<?php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);

require_once './includes/auth.php';

SessionManager::start();

if (SessionManager::isLoggedIn()) {
    header('Location: dashboard.php');
    exit();
}

$error_message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $pwd = $_POST['pwd'] ?? '';
    
    if (!empty($username) && !empty($pwd)) {
        $user = authenticate_user($username, $pwd);
        
        if ($user) {
            SessionManager::setUser($username);
            header('Location: dashboard.php');
            exit();
        } else {
            http_response_code(401);
            $error_message = 'Invalid credentials';
        }
    } else {
        $error_message = 'Please enter both username and pwd';
    }
}

$page_title = 'Login - UTOPIA Smart City';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($page_title) ?></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="/assets/styles.css">
    <meta name="description" content="Login to UTOPIA Smart City Accommodation Finder V2">
    <meta name="robots" content="noindex, nofollow">
    <meta name="theme-color" content="#000000">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23000'/><text x='50' y='60' font-size='20' font-family='Poppins,sans-serif' font-weight='700' fill='%23fff' text-anchor='middle'>U</text></svg>">
</head>
<body>
    <div class="hero">
        <div class="container">
            <h1>UTOPIA</h1>
            <p class="hero-subtitle">Smart City Accommodation Finder V2</p>
        </div>
    </div>

    <div class="container" style="padding-top: 3rem; padding-bottom: 3rem;">
        <div class="filter-form">
            <h2 style="margin-bottom: 1.5rem; font-size: 1.5rem; font-weight: 600; text-align: center;">Access Your Dashboard</h2>
            
            <form method="post" action="login.php">
                <div class="form-group">
                    <label for="username" class="form-label">Username</label>
                    <input 
                        type="text" 
                        id="username" 
                        name="username" 
                        placeholder="Enter your username" 
                        required 
                        autocomplete="username"
                        value="<?= htmlspecialchars($_POST['username'] ?? '') ?>"
                    >
                </div>
                
                <div class="form-group">
                    <label for="pwd" class="form-label">pwd</label>
                    <input 
                        type="pwd" 
                        id="pwd" 
                        name="pwd" 
                        placeholder="Enter your pwd" 
                        required 
                        autocomplete="current-pwd"
                    >
                </div>
                
                <button type="submit" class="btn-primary">
                    Sign In
                </button>
            </form>
        </div>

        <div style="margin-top: 3rem; padding: 2rem; background: var(--gray-50); border-radius: var(--radius-lg); border: 1px solid var(--gray-200);">
            <h3 style="margin-bottom: 1.5rem; font-size: 1.125rem; font-weight: 600; text-align: center;">Demo Accounts</h3>
            
            <div style="display: grid; gap: 1rem;">
                <div style="padding: 1rem; background: var(--white); border-radius: var(--radius-md); border: 1px solid var(--gray-200);">
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">Guest Access</div>
                    <div style="font-size: 0.875rem; color: var(--gray-600);">
                        Username: <code style="background: var(--gray-100); padding: 0.125rem 0.5rem; border-radius: 0.25rem;">guest</code><br>
                        pwd: <code style="background: var(--gray-100); padding: 0.125rem 0.5rem; border-radius: 0.25rem;">guest</code>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
