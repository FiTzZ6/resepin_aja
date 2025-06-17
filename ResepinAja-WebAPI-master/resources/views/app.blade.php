<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <meta name="csrf-token" content="{{ csrf_token() }}">
  @vite(['resources/css/bootstrap.min.css', 'resources/css/style.css', 
  'resources/js/app.js', 'resources/js/popper.min.js', 'resources/js/bootstrap.min.js'])
  @inertiaHead
  <title inertia>{{ config('app.name') }}</title>
</head>

<body>
  {{-- <div id="app"></div> --}}
  @inertia
</body>

</html>
