<?php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);

define('SQL_BAN_LIST', [
    '!',
    '"',
    '$',
    '%',
    '&',
    '+',
    '.',
    ':',
    '<',
    '>',
    '?',
    '@',
    '[',
    '\\',
    ']',
    '^',
    '_',
    '`',
    '|',
    '~',
    'alter',
    'benchmark',
    'count',
    'create',
    'cursor',
    'database',
    'declare',
    'delay',
    'delete',
    'describe',
    'drop',
    'exec',
    'extract',
    'fetch',
    'insert',
    'right',
    'rlike',
    'rpad',
    'set',
    'sha2',
    'sleep',
    'table',
    'union',
    'update',
    'wait'
]);

function filter_sql_input($input) {
    if (empty($input)) {
        return false;
    }
    
    $input_lower = strtolower($input);
    
    foreach (SQL_BAN_LIST as $banned_keyword) {
        if (strpos($input_lower, strtolower($banned_keyword)) !== false) {
            echo "Input contains banned pattern: " . htmlspecialchars($banned_keyword) . "\n"; // Debug line
            return true; 
        }
    }
    
    return false; 
}

function sanitize_sql_input($input) {
    if (filter_sql_input($input)) {
        return ''; 
    }
    return $input;
}

function is_safe_input($input) {
    return !filter_sql_input($input);
}
