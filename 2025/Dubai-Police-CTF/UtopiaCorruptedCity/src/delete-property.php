<?php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);

require_once './includes/functions.php';

SessionManager::start();
SessionManager::requireLogin();

$property_id = $_POST['property_id'] ?? 0;
$error_message = '';
$property = null;

if (!$property_id || !is_numeric($property_id) || $property_id < 1) {
    http_response_code(400);
    $error_message = 'Invalid property ID';
} else {
    $property = get_property_by_id($property_id);
    if (!$property) {
        http_response_code(404);
        $error_message = 'Property not found';
    }
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['answer'])) {
    if ($_POST['answer'] === 'y') {
        $result = delete_property($property_id);
        if ($result) {
            header('Location: dashboard.php');
            exit();
        } else {
            $error_message = 'Failed to delete property';
        }
    } else {
        header("Location: property.php?id={$property_id}");
        exit();
    }
}

$username = SessionManager::getUsername();
$is_admin = SessionManager::isAdmin();
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UTOPIA Smart City - Delete Property</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="/assets/styles.css">
    <meta name="description" content="Delete Property in UTOPIA Smart City">
    <meta name="robots" content="noindex, nofollow">
    <meta name="theme-color" content="#000000">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23000'/><text x='50' y='60' font-size='20' font-family='Poppins,sans-serif' font-weight='700' fill='%23fff' text-anchor='middle'>U</text></svg>">
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <h1>UTOPIA</h1>
                <p>Smart City Accommodation Finder V2</p>
            </div>
            <div class="user-info">
                <div class="user-badge">
                    <?= htmlspecialchars($username) ?>
                    <?php if ($is_admin): ?>
                        <span class="admin-badge">ADMIN</span>
                    <?php endif; ?>
                </div>
                <a href="dashboard.php" class="nav-link">Dashboard</a>
                <a href="logout.php" class="nav-link">Logout</a>
            </div>
        </div>
    </header>

    <div class="container">
        <?php if ($property): ?>
            <div class="delete-container">
                <div class="delete-header">
                    <h1>Delete Property</h1>
                    <p>This action cannot be undone</p>
                </div>

                <div class="delete-content">
                    <div class="warning-icon">Warning</div>
                    
                    <div class="property-info">
                        <h3><?= htmlspecialchars($property['title']) ?></h3>
                        <p><strong>Address:</strong> <?= htmlspecialchars($property['address']) ?></p>
                        <?php if ($is_admin): ?>
                            <p><strong>Price:</strong> <?= format_price($property['price']) ?>/month</p>
                            <p><strong>Type:</strong> <?= htmlspecialchars($property['property_type']) ?></p>
                        <?php endif; ?>
                    </div>
                    
                    <div class="confirmation-text">
                        Are you sure you want to delete this property?<br>
                        This action cannot be undone.
                    </div>

                    <form method="post" action="delete-property.php">
                        <input type="hidden" name="property_id" value="<?= $property['idx'] ?>">
                        
                        <div class="delete-actions">
                            <button type="submit" name="answer" value="y" class="btn btn-danger">
                                Yes, Delete
                            </button>
                            <button type="submit" name="answer" value="n" class="btn btn-secondary">
                                Cancel
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>
