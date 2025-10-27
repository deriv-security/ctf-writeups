<?php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);

require_once './includes/functions.php';

SessionManager::start();
SessionManager::requireLogin();

$property_id = $_POST['property_id'] ?? $_GET['id'] ?? 0;
$error_message = '';
$success_message = '';
$property = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['title']) && isset($_POST['description'])) {
    $title = $_POST['title'] ?? '';
    $description = $_POST['description'] ?? '';
    $address = $_POST['address'] ?? '';
    $price = $_POST['price'] ?? 0;
    $property_type = $_POST['property_type'] ?? 'apartment';
    $bedrooms = $_POST['bedrooms'] ?? 1;
    $bathrooms = $_POST['bathrooms'] ?? 1;
    $area_sqft = $_POST['area_sqft'] ?? 500;
    $amenities = $_POST['amenities'] ?? '';
    $contact_info = $_POST['contact_info'] ?? '';
    
    if (!SessionManager::isAdmin()) {
        header("Location: property.php?id={$property_id}");
        exit();
    }
    
    $data = [
        'title' => $title,
        'description' => $description,
        'address' => $address,
        'price' => $price,
        'property_type' => $property_type,
        'bedrooms' => $bedrooms,
        'bathrooms' => $bathrooms,
        'area_sqft' => $area_sqft,
        'amenities' => $amenities,
        'contact_info' => $contact_info
    ];
    $result = update_property($property_id, $data);
    
    if ($result) {
        header("Location: property.php?id={$property_id}");
        exit();
    } else {
        $error_message = 'Failed to update property. Please check your input.';
    }
}

if (!SessionManager::isAdmin()) {
    $property = [
        'idx' => $property_id,
        'title' => str_repeat('*', 39),
        'description' => str_repeat('*', 1390),
        'address' => str_repeat('*', 50),
        'price' => '****',
        'property_type' => '****',
        'bedrooms' => '*',
        'bathrooms' => '*',
        'area_sqft' => '****',
        'amenities' => str_repeat('*', 100),
        'contact_info' => str_repeat('*', 30)
    ];
} else {
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
}

$username = SessionManager::getUsername();
$is_admin = SessionManager::isAdmin();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UTOPIA Smart City - Edit Property</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="/assets/styles.css">
    <meta name="description" content="Edit Property in UTOPIA Smart City">
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
        <div class="page-header">
            <h1>Edit Property</h1>
            <p>Update property information</p>
        </div>

        <?php if (!$is_admin): ?>
            <div class="restricted-notice">
                Access Restricted: You can only view limited property information. Admin access required for editing.
            </div>
        <?php endif; ?>

        <div class="form-container">
            <?php if ($success_message): ?>
                <div class="alert alert-success">
                    <?= htmlspecialchars($success_message) ?>
                </div>
            <?php endif; ?>

            <?php /* Error messages disabled */ ?>

            <?php if ($property): ?>
                <form method="post" action="edit-property.php">
                    <input type="hidden" name="property_id" value="<?= htmlspecialchars($property['idx']) ?>">
                    
                    <div class="form-group">
                        <label for="title">Property Title *</label>
                        <input type="text" id="title" name="title" required maxlength="96"
                               value="<?= htmlspecialchars($property['title']) ?>">
                    </div>

                    <div class="form-group">
                        <label for="description">Description *</label>
                        <textarea id="description" name="description" required><?= htmlspecialchars($property['description']) ?></textarea>
                    </div>

                    <div class="form-group">
                        <label for="address">Address *</label>
                        <input type="text" id="address" name="address" required
                               value="<?= htmlspecialchars($property['address']) ?>">
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="price">Monthly Rent ($) *</label>
                            <input type="number" id="price" name="price" required min="0" step="0.01"
                                   value="<?= htmlspecialchars($property['price']) ?>">
                        </div>

                        <div class="form-group">
                            <label for="property_type">Property Type *</label>
                            <select id="property_type" name="property_type" required>
                                <option value="apartment" <?= $property['property_type'] === 'apartment' ? 'selected' : '' ?>>Apartment</option>
                                <option value="house" <?= $property['property_type'] === 'house' ? 'selected' : '' ?>>House</option>
                                <option value="condo" <?= $property['property_type'] === 'condo' ? 'selected' : '' ?>>Condo</option>
                                <option value="studio" <?= $property['property_type'] === 'studio' ? 'selected' : '' ?>>Studio</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="bedrooms">Bedrooms</label>
                            <input type="number" id="bedrooms" name="bedrooms" min="0" max="10"
                                   value="<?= htmlspecialchars($property['bedrooms']) ?>">
                        </div>

                        <div class="form-group">
                            <label for="bathrooms">Bathrooms</label>
                            <input type="number" id="bathrooms" name="bathrooms" min="0" max="10"
                                   value="<?= htmlspecialchars($property['bathrooms']) ?>">
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="area_sqft">Area (Square Feet)</label>
                        <input type="number" id="area_sqft" name="area_sqft" min="0"
                               value="<?= htmlspecialchars($property['area_sqft']) ?>">
                    </div>

                    <div class="form-group">
                        <label for="amenities">Amenities (JSON format)</label>
                        <textarea id="amenities" name="amenities"><?= htmlspecialchars($property['amenities']) ?></textarea>
                    </div>

                    <div class="form-group">
                        <label for="contact_info">Contact Information</label>
                        <input type="text" id="contact_info" name="contact_info"
                               value="<?= htmlspecialchars($property['contact_info']) ?>">
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">Update Property</button>
                        <a href="property.php?id=<?= $property['idx'] ?>" class="btn btn-secondary">Cancel</a>
                    </div>
                </form>
            <?php else: ?>
                <div class="alert alert-error">
                    Property not found or access denied.
                </div>
                <div class="form-actions">
                    <a href="dashboard.php" class="btn btn-secondary">Back to Dashboard</a>
                </div>
            <?php endif; ?>
        </div>
    </div>
</body>
</html>
