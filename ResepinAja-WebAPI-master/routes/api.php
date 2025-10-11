<?php

// DONT USE, THE CONTROLLER IS UPDATED TO ALIGN WITH THE SESSION BASED
// JANGAN DIPAKE, UDAH DIGANTI

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\RecipeController;
use App\Http\Controllers\UserController;
use App\Http\Controllers\ChatbotController;

Route::post('/register', [AuthController::class, 'register']);
Route::post('/login', [AuthController::class, 'login']);

Route::get('/resepbaru', [RecipeController::class, 'APIshowRecipeNewest']);
Route::get('/reseppopuler', [RecipeController::class, 'APIshowRecipeBest']);
Route::get('/ratingresep/{id_resep}', [ UserController::class, 'showRating']);
Route::get('/detailresep/{id_resep}', [ RecipeController::class, 'APIshowDetailRecipe']);
Route::get('/resepsendiri/{id_user}', [ RecipeController::class, 'APIshowRecipeSelf']);
Route::get('/resepcari', [ RecipeController::class, 'filterProduk']);
Route::get('/profil/{id_user}', [ UserController::class, 'APIshowProfile']);

Route::middleware('auth:sanctum')->group(function () {
    Route::post('/save-recipe', [UserController::class, 'saveRecipe']);
    Route::post('/unsave-recipe', [UserController::class, 'unsaveRecipe']);
    Route::get('/check-saved/{id_user}/{id_resep}', [UserController::class, 'checkSaved']);
    
    Route::get('/user-rating/{id_resep}/{id_user}', [UserController::class, 'getUserRating']);
    Route::post('/submit-rating', [UserController::class, 'addRating']);
    Route::delete('/del-rating', [UserController::class, 'DeleteUserRating']);
    
    Route::post('/edit-profile', [UserController::class, 'editProfile']);
    Route::get('/tersimpanresep/{id_user}', [ RecipeController::class, 'APIshowSavedRecipe']);
    Route::post('/addresep', [RecipeController::class, 'addRecipe']);
    Route::put('/updateresep', [RecipeController::class, 'updateResep']);
    Route::delete('/deleteresep', [RecipeController::class, 'deleteResep']);
    Route::post('/logout', [AuthController::class, 'logoutToken']);
});

Route::post('/chatbot', [ChatbotController::class, 'sendMessage']);
