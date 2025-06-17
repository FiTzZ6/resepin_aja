<?php

namespace App\Http\Controllers;

use App\Models\Rating;
use App\Models\Saved;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;

class UserController extends Controller
{
    public function showProfile($id_user) {
        $items = User::where("id_user", $id_user)->select('id_user', 'username', 'deskripsi_user')->first();
        return $items;
    }
    public function APIshowProfile($id_user) {
        $dataProfil = $this->showProfile($id_user);
        return response()->json([
            'success' => true,
            'data' => $dataProfil
        ], 200);
    }

    public function showRating($id_resep)
    {
        $items = DB::table('users')
            ->join('rating', 'users.id_user', '=', 'rating.id_user')
            ->where('rating.id_resep', $id_resep)
            ->select(
                'rating.*',
                'users.username',
            )
            ->groupBy(
                'rating.id_rating',
                'rating.id_resep',
                'rating.bintang',
                'rating.id_user',
                'rating.komentar',
                'rating.created_at',
                'rating.updated_at',
                'users.username',
            )
            ->orderBy('rating.created_at', 'desc')->get();
        return response()->json([
            'success' => true,
            'message' => 'Rating submitted',
            'data' => $items
        ]);
    }
    public function addRating(Request $request)
    {
        $validated = $request->validate([
            'id_resep' => 'required|integer',
            'bintang' => 'required|integer|min:1|max:5',
            'id_user' => 'required|integer',
            'komentar' => 'sometimes|string|max:500'
        ]);

        $rating = Rating::updateOrCreate(
            [
                'id_resep' => $validated['id_resep'],
                'id_user' => $validated['id_user']
            ],
            [
                'bintang' => $validated['bintang'],
                'komentar' => $validated['komentar'] ?? null
            ]
        );

        return response()->json([
            'success' => true,
            'message' => 'Rating submitted',
            'data' => $rating
        ]);
    }
    public function saveRecipe(Request $request)
    {
        $saved = Saved::firstOrCreate([
            'id_user' => $request->id_user,
            'id_resep' => $request->id_resep
        ]);

        return response()->json([
            'success' => true,
            'message' => 'Recipe saved',
            'data' => $saved
        ]);
    }

    public function unsaveRecipe(Request $request)
    {
        $deleted = Saved::where([
            'id_user' => $request->id_user,
            'id_resep' => $request->id_resep
        ])->delete();

        return response()->json([
            'success' => (bool)$deleted,
            'message' => $deleted ? 'Recipe unsaved' : 'Failed to unsave'
        ]);
    }

    public function checkSaved($id_user, $id_resep)
    {
        $isSaved = Saved::where([
            'id_user' => $id_user,
            'id_resep' => $id_resep
        ])->exists();

        return response()->json([
            'is_saved' => $isSaved
        ], 200);
    }
    public function editProfile(Request $request)
    {
        $user = $request->user();
        $validated = $request->validate([
            'deskripsi_user' => 'nullable|string|max:500',
            'password' => 'nullable|string|min:6|confirmed', 
        ]);
        if (array_key_exists('deskripsi_user', $validated)) {
            $user->deskripsi_user = $validated['deskripsi_user'];
        }
        if (!empty($validated['password'])) {
            $user->password = Hash::make($validated['password']);
        }
        $user->save();
        return response()->json([
            'success' => true,
            'message' => 'Profile updated successfully',
            'data' => [
                'username' => $user->username,
                'no_hp' => $user->no_hp,
                'deskripsi_user' => $user->deskripsi_user,
            ],
        ]);
    }

    public function getUserRating($id_resep, $id_user)
    {
        $items = DB::table('users')
            ->join('rating', 'users.id_user', '=', 'rating.id_user')
            ->where(['rating.id_resep' => $id_resep, 'rating.id_user' => $id_user])
            ->select(
                'rating.*',
                'users.username',
            )
            ->groupBy(
                'rating.id_rating',
                'rating.id_resep',
                'rating.bintang',
                'rating.id_user',
                'rating.komentar',
                'rating.created_at',
                'rating.updated_at',
                'users.username',
            )
            ->orderBy('rating.created_at', 'desc')->first();
        return response()->json([
            'exists' => $items !== null,
            'rating' => $items
        ], 200);
    }

    public function DeleteUserRating(Request $request){
        $request->validate([
            'id_resep' => 'required|integer',
            'id_user' => 'required|integer',
        ]);
        $items = Rating::where(['id_resep' => $request->id_resep, 'id_user' => $request->id_user]);
        $items->delete();
        return response()->json([
            'success' => (bool)$items,
            'message' => $items ? 'Rating deleted' : 'Failed to delete'
        ], 200);
    }
}
