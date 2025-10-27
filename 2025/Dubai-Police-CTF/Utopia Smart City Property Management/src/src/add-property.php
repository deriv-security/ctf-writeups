<?php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);

require_once './includes/functions.php';
require_once './includes/config.php';

SessionManager::start();
SessionManager::requireLogin();

$error_message = '';
$success_message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['title']) && isset($_POST['description']) && !filter_sql_input($_POST['title']) && !filter_sql_input($_POST['description'])) {
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
        $result = add_property($data);
        
        if ($result) {
            $success_message = 'Property added successfully!';
        } else {
            $error_message = 'Failed to add property. Please check your input.';
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
    <title>UTOPIA Smart City - Add Property</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="stylesheet" href="/assets/styles.css">
    <meta name="description" content="Add Property to UTOPIA Smart City">
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
            <h1>Add New Property</h1>
            <p>List your property in UTOPIA Smart City</p>
        </div>

        <div class="form-container">
            <?php if ($success_message): ?>
                <div class="alert alert-success">
                    <?= htmlspecialchars($success_message) ?>
                </div>
            <?php endif; ?>


            <form method="post" action="add-property.php">
                <div class="form-group">
                    <label for="title">Property Title *</label>
                    <input type="text" id="title" name="title" required maxlength="96"
                           placeholder="e.g., Modern Downtown Apartment">
                </div>

                <div class="form-group">
                    <label for="description">Description *</label>
                    <textarea id="description" name="description" required
                              placeholder="Describe your property, its features, and what makes it special..."></textarea>
                </div>

                <div class="form-group">
                    <label for="address">Address *</label>
                    <input type="text" id="address" name="address" required
                           placeholder="e.g., 123 Innovation Boulevard, UTOPIA District 1">
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="price">Monthly Rent ($) *</label>
                        <input type="number" id="price" name="price" required min="0" step="0.01"
                               placeholder="2500.00">
                    </div>

                    <div class="form-group">
                        <label for="property_type">Property Type *</label>
                        <select id="property_type" name="property_type" required>
                            <option value="apartment">Apartment</option>
                            <option value="house">House</option>
                            <option value="condo">Condo</option>
                            <option value="studio">Studio</option>
                        </select>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="bedrooms">Bedrooms</label>
                        <input type="number" id="bedrooms" name="bedrooms" min="0" max="10" value="1">
                    </div>

                    <div class="form-group">
                        <label for="bathrooms">Bathrooms</label>
                        <input type="number" id="bathrooms" name="bathrooms" min="0" max="10" value="1">
                    </div>
                </div>

                <div class="form-group">
                    <label for="area_sqft">Area (Square Feet)</label>
                    <input type="number" id="area_sqft" name="area_sqft" min="0" value="500"
                           placeholder="1200">
                </div>

                <div class="form-group">
                    <label for="amenities">Amenities (JSON format)</label>
                    <textarea id="amenities" name="amenities"
                              placeholder='["smart_thermostat", "high_speed_internet", "gym", "rooftop_garden"]'></textarea>
                </div>

                <div class="form-group">
                    <label for="contact_info">Contact Information</label>
                    <input type="text" id="contact_info" name="contact_info"
                           placeholder="contact@example.com or +1-555-0123">
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Add Property</button>
                    <a href="dashboard.php" class="btn btn-secondary">Cancel</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
