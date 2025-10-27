<?php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);

require_once './includes/functions.php';

SessionManager::start();
SessionManager::requireLogin();

$page = isset($_GET['page']) && is_numeric($_GET['page']) && $_GET['page'] > 0 ? (int)$_GET['page'] : 1;
$properties = get_properties_for_user($page, PAGINATION_SIZE);
$username = SessionManager::getUsername();
$is_admin = SessionManager::isAdmin();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UTOPIA Smart City - Property Listings</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="/assets/styles.css">
    <meta name="description" content="UTOPIA Smart City Property Listings">
    <meta name="robots" content="noindex, nofollow">
    <meta name="theme-color" content="#000000">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' fill='%23000'/><text x='50' y='60' font-size='20' font-family='Poppins,sans-serif' font-weight='700' fill='%23fff' text-anchor='middle'>U</text></svg>">
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="logo">
                <h1>UTOPIA</h1>
                <p>Smart City Accommodation Finder</p>
            </div>
            <div class="user-info">
                <div class="user-badge">
                    Welcome, <?= htmlspecialchars($username) ?>
                    <?php if ($is_admin): ?>
                        <span class="admin-badge">ADMIN</span>
                    <?php endif; ?>
                </div>
                <a href="logout.php" class="nav-link">Logout</a>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="page-header">
            <h1>Available Properties</h1>
            <p>Find your perfect home in the future</p>
        </div>


<?php if (!empty($is_admin) && $is_admin === true): ?>
    <div class="flag">
        You have full access to all property details.
        <b id='flag'>
        <?php
            echo getenv('FLAG');
        ?>
        <b>
    </div>
<?php else: ?>
    <div class="obfuscated-notice">
        Limited access: Property details are restricted. Contact admin for full access.
    </div>
<?php endif; ?>




        <div class="properties-grid">
            <?php foreach ($properties as $property): ?>
                <div class="property-card">
                    <div class="property-header">
                        <h3>
                            <a href="property.php?id=<?= $property['idx'] ?>">
                                <?= $is_admin ? htmlspecialchars($property['title']) : str_repeat('*', min(30, strlen($property['title']))) ?>
                            </a>
                        </h3>
                    </div>
                    <div class="property-details">
                        <?php if ($is_admin): ?>
                            <div class="property-meta">
                                <div class="price"><?= format_price($property['price']) ?>/month</div>
                                <div class="property-type"><?= htmlspecialchars($property['property_type']) ?></div>
                            </div>
                            <div class="address"><?= htmlspecialchars($property['address']) ?></div>
                            <div class="specs">
                                <div class="spec-item"><?= $property['bedrooms'] ?> BR</div>
                                <div class="spec-item"><?= $property['bathrooms'] ?> BA</div>
                                <div class="spec-item"><?= number_format($property['area_sqft']) ?> sq ft</div>
                            </div>
                        <?php else: ?>
                            <div class="property-meta">
                                <div class="price"><?= str_repeat('*', 10) ?></div>
                                <div class="property-type"><?= str_repeat('*', 10) ?></div>
                            </div>
                            <div class="address"><?= str_repeat('*', 50) ?></div>
                            <div class="specs">
                                <div class="spec-item">*** BR</div>
                                <div class="spec-item">*** BA</div>
                                <div class="spec-item">****** sq ft</div>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>
            <?php endforeach; ?>
        </div>

        <div class="actions">
            <a href="add-property.php" class="btn btn-success">Add New Property</a>
        </div>

        <div class="pagination">
            <?php if ($page > 1): ?>
                <a href="dashboard.php?page=<?= $page - 1 ?>" class="btn btn-secondary">← Previous</a>
            <?php endif; ?>
            <span class="btn" style="background: var(--gray-200); color: var(--gray-700);">Page <?= $page ?></span>
            <a href="dashboard.php?page=<?= $page + 1 ?>" class="btn btn-primary">Next →</a>
        </div>
    </div>
</body>
</html>
