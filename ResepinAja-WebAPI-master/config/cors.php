<?php

return [
    'paths' => ['api/*', 'sanctum/csrf-cookie', 'login', 'register'],
    'allowed_methods' => ['*'],
    'allowed_origins' => ['http://localhost:5173', 'http://localhost:5173', 'http://localhost:8000', 'http://localhost:8000'],
    'allowed_headers' => ['*'],
    'supports_credentials' => true,
];
