<?php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('display_startup_errors', 0);

define('SQL_BAN_LIST', [
    '_',
    ';',
    ':',
    '!',
    '?',
    '.',
    '"',
    '[',
    '@',
    '*',
    '/',
    '\\',
    '&',
    '%',
    '`',
    '^',
    '+',
    '<',
    '>',
    '|',
    '~',
    '$',
    '#',
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
    'into',
    'or',
    'right',
    'rlike',
    'rpad',
    'set',
    'sha2',
    'sleep',
    'string'
    'table',
    'union',
    'update',
    'wait',
]);

function is_input_safe(string $input): bool
{
    if (trim($input) === '') {
        return false;
    }

    $inputLower = strtolower($input);

    foreach (SQL_BAN_LIST as $banned) {
        $pattern = ctype_alpha($banned)
            ? '/\b' . preg_quote($banned, '/') . '\b/i'
            : '/' . preg_quote($banned, '/') . '/';

        if (preg_match($pattern, $inputLower)) {
            return false;
        }
    }

    return true;
}

function sanitize_sql_input($input) {
    if (is_input_safe($input)) {
        return ''; 
    }
    return $input;
}
