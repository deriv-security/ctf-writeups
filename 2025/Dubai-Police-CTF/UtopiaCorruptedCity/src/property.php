<?php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);

require_once './includes/functions.php';

SessionManager::start();
SessionManager::requireLogin();


$property_id = $_GET['id'] ?? 0;
$property = get_property_by_id($property_id);



if (!$property) {
    http_response_code(404);
    $error_message = 'Property not found';
}

$username = SessionManager::getUsername();
$is_admin = SessionManager::isAdmin();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UTOPIA Smart City - Property Details</title>
    
    <!-- Preload critical fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    
    <!-- Main stylesheet -->
    <link rel="stylesheet" href="/assets/styles.css">
    
    <!-- Meta tags -->
    <meta name="description" content="UTOPIA Smart City Property Details">
    <meta name="robots" content="noindex, nofollow">
    
    <!-- Theme color -->
    <meta name="theme-color" content="#000000">
    
    <!-- Favicon -->
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
        <?php if (!$is_admin): ?>
            <div class="obfuscated-notice">
                Limited Access: Property details are restricted. Contact admin for full information.
            </div>
        <?php endif; ?>

        <?php if ($property): ?>
            <div class="property-detail">
                <div class="property-header">
                    <h1><?= $is_admin ? htmlspecialchars($property['title']) : str_repeat('*', min(30, strlen($property['title']))) ?></h1>
                    <div class="property-meta">
                        <div class="meta-item">
                            <span class="meta-value"><?= $is_admin ? format_price($property['price']) : str_repeat('*', 10) ?></span>
                            <span class="meta-label">Monthly Rent</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-value"><?= $is_admin ? htmlspecialchars($property['property_type']) : str_repeat('*', 10) ?></span>
                            <span class="meta-label">Property Type</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-value"><?= $is_admin ? htmlspecialchars($property['bedrooms']) : '***' ?></span>
                            <span class="meta-label">Bedrooms</span>
                        </div>
                    </div>
                </div>

                <div class="property-content">
                    <div class="property-section">
                        <h3>Description</h3>
                        <p><?= $is_admin ? nl2br(htmlspecialchars($property['description'])) : str_repeat('*', 100) ?></p>
                    </div>

                    <div class="property-section">
                        <h3>Location</h3>
                        <p><?= $is_admin ? htmlspecialchars($property['address']) : str_repeat('*', 50) ?></p>
                    </div>

                    <div class="property-section">
                        <h3>Property Details</h3>
                        <div class="property-grid">
                            <div class="property-item">
                                <span class="property-item-value"><?= $is_admin ? htmlspecialchars($property['bedrooms']) : '***' ?></span>
                                <span class="property-item-label">Bedrooms</span>
                            </div>
                            <div class="property-item">
                                <span class="property-item-value"><?= $is_admin ? htmlspecialchars($property['bathrooms']) : '***' ?></span>
                                <span class="property-item-label">Bathrooms</span>
                            </div>
                            <div class="property-item">
                                <span class="property-item-value"><?= $is_admin ? number_format($property['area_sqft']) : '******' ?></span>
                                <span class="property-item-label">Square Feet</span>
                            </div>
                        </div>
                    </div>

                    <?php if ($is_admin && !empty($property['amenities']) && $property['amenities'] !== str_repeat('*', 100)): ?>
                        <div class="property-section">
                            <h3>Amenities</h3>
                            <div class="amenities-list">
                                <?php
                                $amenities = json_decode($property['amenities'], true);
                                if (is_array($amenities)) {
                                    foreach ($amenities as $amenity) {
                                        echo '<span class="amenity-tag">' . htmlspecialchars(ucwords(str_replace('_', ' ', $amenity))) . '</span>';
                                    }
                                } else {
                                    echo '<span class="amenity-tag">' . htmlspecialchars($property['amenities']) . '</span>';
                                }
                                ?>
                            </div>
                        </div>
                    <?php endif; ?>

                    <?php if ($is_admin && !empty($property['contact_info']) && $property['contact_info'] !== str_repeat('*', 30)): ?>
                        <div class="property-section">
                            <h3>Contact Information</h3>
                            <p><?= htmlspecialchars($property['contact_info']) ?></p>
                        </div>
                    <?php endif; ?>
                </div>

                <div class="property-actions">
                    <form method="post" action="edit-property.php" style="display: inline;">
                        <input type="hidden" name="property_id" value="<?= $property['idx'] ?>">
                        <button type="submit" class="btn btn-warning">Edit Property</button>
                    </form>
                    
                    <form method="post" action="delete-property.php" style="display: inline;">
                        <input type="hidden" name="property_id" value="<?= $property['idx'] ?>">
                        <button type="submit" class="btn btn-danger">Delete Property</button>
                    </form>
                    
                    <a href="dashboard.php" class="btn btn-secondary">Back to Listings</a>
                </div>
            </div>
        <?php endif; ?>
    </div>
</body>
</html>
