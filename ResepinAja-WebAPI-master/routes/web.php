<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\RecipeController;
use App\Http\Controllers\UserController;
use App\Http\Controllers\ChatbotController;


// Route::get('/', function () {
//     return view('show');
// });
// Route::get('/{any}', function () {
//     return view('app');
// })->where('any', '.*');


Route::post('/register', [AuthController::class, 'register']);
Route::post('/login', [AuthController::class, 'login'])->name('login');

Route::get('/', [RecipeController::class, 'HomePage'])->name('home');
Route::get('/detailresep/{id_resep}', [ RecipeController::class, 'DetailPage']);
Route::get('/profil/{id_user}', [ RecipeController::class, 'ProfilePage']);
Route::get('/resepcari', [ RecipeController::class, 'FilterPage']);

Route::middleware('auth:sanctum')->group(function () {
    Route::get('/tambahresep', [RecipeController::class, 'AddRecipePage']);
    Route::get('/user-rating/{id_resep}/{id_user}', [UserController::class, 'getUserRating']);
    Route::post('/edit-profile', [UserController::class, 'editProfile']);

    Route::get('/tersimpanresep/{id_user}', [ RecipeController::class, 'SavedPage']);
    Route::post('/addresep', [RecipeController::class, 'addRecipe']);
    Route::get('/editresep/{id_user}', [RecipeController::class, 'UpdatePage']);
    // Route::delete('/deleteresep/{id_resep}', [RecipeController::class, 'deleteResep']);
    Route::get('/logout', [AuthController::class, 'logout']);
});

Route::post('/chatbot', [ChatbotController::class, 'sendMessage']);



