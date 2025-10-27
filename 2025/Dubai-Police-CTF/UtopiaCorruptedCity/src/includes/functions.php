<?php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);

require_once __DIR__ . '/auth.php';

define('PAGINATION_SIZE', 10);
define('MAX_PAGINATION_LIMIT', 50);

function safe_int($v, $default = 0) {
    if (!isset($v)) return $default;
    return (int) $v;
}

function safe_float($v, $default = 0.0) {
    if (!isset($v)) return $default;
    return (float) $v;
}

function get_properties_for_user($page = 1, $limit = PAGINATION_SIZE) {
    global $conn;

    $page = max(1, safe_int($page, 1));
    $limit = safe_int($limit, PAGINATION_SIZE);
    if ($limit < 1) $limit = PAGINATION_SIZE;
    if ($limit > MAX_PAGINATION_LIMIT) $limit = MAX_PAGINATION_LIMIT;

    $offset = ($page - 1) * $limit;

    $sql = "SELECT * FROM properties ORDER BY created_at DESC LIMIT ? OFFSET ?";
    if ($stmt = $conn->prepare($sql)) {
        $stmt->bind_param('ii', $limit, $offset);
        if ($stmt->execute()) {
            $res = $stmt->get_result();
            $properties = $res->fetch_all(MYSQLI_ASSOC);
            $stmt->close();
            return $properties;
        }
        $stmt->close();
    }
    return [];
}

function get_property_by_id($id) {
    global $conn;
    $id = safe_int($id, 0);
    if ($id <= 0) return false;

    $sql = "SELECT * FROM properties WHERE idx = ?";
    if ($stmt = $conn->prepare($sql)) {
        $stmt->bind_param('i', $id);
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

function format_price($price) {
    return '$' . number_format($price, 2);
}

function add_property($data) {
    global $conn;
    
    $title = $data['title'];
    $description = $conn->real_escape_string($data['description']);
    $address = $conn->real_escape_string($data['address']);
    $price = floatval($data['price']);
    $property_type = $conn->real_escape_string($data['property_type']);
    $bedrooms = intval($data['bedrooms']);
    $bathrooms = intval($data['bathrooms']);
    $area_sqft = intval($data['area_sqft']);
    $amenities = $conn->real_escape_string($data['amenities']);
    $contact_info = $conn->real_escape_string($data['contact_info']);
    
    $sql = "INSERT INTO properties (description, address, price, property_type, bedrooms, bathrooms, area_sqft, amenities, contact_info,title) 
            VALUES ('$description', '$address', $price, '$property_type', $bedrooms, $bathrooms, $area_sqft, '$amenities', '$contact_info','$title')";

    return $conn->query($sql);
}

function update_property($id, $data) {
    global $conn;

    $id = safe_int($id, 0);
    if ($id <= 0) return false;

    $title = isset($data['title']) ? $data['title'] : '';
    $description = isset($data['description']) ? $data['description'] : '';
    $address = isset($data['address']) ? $data['address'] : '';
    $price = safe_float($data['price'] ?? 0.0);
    $property_type = isset($data['property_type']) ? $data['property_type'] : '';
    $bedrooms = safe_int($data['bedrooms'] ?? 0);
    $bathrooms = safe_int($data['bathrooms'] ?? 0);
    $area_sqft = safe_int($data['area_sqft'] ?? 0);
    $amenities = isset($data['amenities']) ? $data['amenities'] : '';
    $contact_info = isset($data['contact_info']) ? $data['contact_info'] : '';

    $sql = "UPDATE properties SET
                title = ?,
                description = ?,
                address = ?,
                price = ?,
                property_type = ?,
                bedrooms = ?,
                bathrooms = ?,
                area_sqft = ?,
                amenities = ?,
                contact_info = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE idx = ?";

    if ($stmt = $conn->prepare($sql)) {
        $stmt->bind_param('sssdiiiissi',
            $title,
            $description,
            $address,
            $price,
            $property_type,
            $bedrooms,
            $bathrooms,
            $area_sqft,
            $amenities,
            $contact_info,
            $id
        );
        $ok = $stmt->execute();
        $affected = $stmt->affected_rows;
        $stmt->close();
        return $ok ? $affected : false;
    }
    return false;
}

function delete_property($id) {
    global $conn;
    $id = safe_int($id, 0);
    if ($id <= 0) return false;

    $sql = "DELETE FROM properties WHERE idx = ?";
    if ($stmt = $conn->prepare($sql)) {
        $stmt->bind_param('i', $id);
        $ok = $stmt->execute();
        $affected = $stmt->affected_rows;
        $stmt->close();
        return $ok ? $affected : false;
    }
    return false;
}

?>
