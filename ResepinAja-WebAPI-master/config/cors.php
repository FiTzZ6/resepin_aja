<?php

return [
    'paths' => ['api/*', 'sanctum/csrf-cookie', 'login', 'register'],
    'allowed_methods' => ['*'],
    'allowed_origins' => ['http://127.0.0.1:5173'],
    'allowed_headers' => ['*'],
    'supports_credentials' => true,
];
