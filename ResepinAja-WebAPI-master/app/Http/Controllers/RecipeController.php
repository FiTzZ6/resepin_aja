<?php

namespace App\Http\Controllers;

use App\Models\AlatResep;
use App\Models\BahanResep;
use App\Models\LangkahResep;
use App\Models\Rating;
use App\Models\Resep;
use App\Models\Saved;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use App\Http\Controllers\UserController;
use Inertia\Inertia;

class RecipeController extends Controller
{
    public function showRecipeNewest()
    {
        $items = DB::table('resep')
            ->leftJoin('rating', 'resep.id_resep', '=', 'rating.id_resep')
            ->join('bahan_resep', 'resep.id_resep', '=', 'bahan_resep.id_resep')
            ->select(
                'resep.id_resep',
                'resep.judul',
                'resep.gambar',
                'resep.wkt_masak',
                'resep.prs_masak',
                DB::raw('CAST(ROUND(AVG(rating.bintang), 1) AS float) as bintang'),
                DB::raw('COUNT(DISTINCT rating.id_user) as jml_bintang'),
                DB::raw('COUNT(bahan_resep.nama_bahan) as jumlah_bahan')
            )
            ->groupBy('resep.id_resep', 'resep.judul', 'resep.gambar', 'resep.wkt_masak', 'resep.prs_masak')
            ->orderBy('resep.created_at', 'desc')
            ->get();

        return $items;
    }
    public function showRecipeBest()
    {
        $items = DB::table('resep')
            ->leftJoin('rating', 'resep.id_resep', '=', 'rating.id_resep')
            ->join('bahan_resep', 'resep.id_resep', '=', 'bahan_resep.id_resep')
            ->select(
                'resep.id_resep',
                'resep.judul',
                'resep.gambar',
                'resep.wkt_masak',
                'resep.prs_masak',
                'resep.deskripsi',
                DB::raw('CAST(ROUND(AVG(rating.bintang), 1) AS float) as bintang'),
                DB::raw('COUNT(DISTINCT rating.id_user) as jml_bintang'),
                DB::raw('COUNT(bahan_resep.nama_bahan) as jumlah_bahan')
            )
            ->groupBy('resep.id_resep', 'resep.judul', 'resep.gambar', 'resep.wkt_masak', 'resep.prs_masak', 'resep.deskripsi')
            ->orderBy('bintang', 'desc')->limit(3)
            ->get();
        return $items;
    }
    public function APIshowRecipeNewest()
    {
        $resepbaru = $this->showRecipeNewest();
        return response()->json([
            'data' => $resepbaru
        ], 200);
    }
    public function APIshowRecipeBest()
    {
        $resepbest = $this->showRecipeBest();
        return response()->json([
            'data' => $resepbest
        ], 200);
    }
    public function HomePage()
    {
        $resepbest = $this->showRecipeBest();
        $resepbaru = $this->showRecipeNewest();
        return Inertia::render('Home', [
            'resepbest' => $resepbest,
            'resepbaru' => $resepbaru,
        ]);
    }



    public function showRecipeSelf($id_user)
    {
        $items = DB::table('resep')
            ->join('users', 'resep.id_user', '=', 'users.id_user')
            ->join('bahan_resep', 'resep.id_resep', '=', 'bahan_resep.id_resep')
            ->leftJoin('rating', 'resep.id_resep', '=', 'rating.id_resep')
            ->where('resep.id_user', $id_user)
            ->select(
                'resep.id_resep',
                'resep.judul',
                'resep.gambar',
                'resep.wkt_masak',
                'resep.prs_masak',
                DB::raw('CAST(ROUND(AVG(rating.bintang), 1) AS float) as bintang'),
                DB::raw('COUNT(DISTINCT rating.id_user) as jml_bintang'),
                DB::raw('COUNT(bahan_resep.nama_bahan) as jumlah_bahan')
            )
            ->groupBy('resep.id_resep', 'resep.judul', 'resep.gambar', 'resep.wkt_masak', 'resep.prs_masak')
            ->get();
        return $items;
    }
    public function APIshowRecipeSelf($id_user)
    {
        $resepProfile = $this->showRecipeSelf($id_user);
        return response()->json([
            'data' => $resepProfile,
        ], 200);
    }
    public function ProfilePage($id_user, UserController $userController)
    {
        $resepProfile = $this->showRecipeSelf($id_user);
        $userProfile = $userController->showProfile($id_user);
        return Inertia::render('Profil', [
            'userProfile' => $userProfile,
            'resepProfile' => $resepProfile,
        ]);
    }



    public function showDetailRecipe($id_resep)
    {
        $resep = DB::table('resep')
            ->leftJoin('rating', 'resep.id_resep', '=', 'rating.id_resep')
            ->join('users', 'resep.id_user', '=', 'users.id_user')
            ->where('resep.id_resep', $id_resep)
            ->select(
                'resep.*',
                'users.username',
                DB::raw('COUNT(DISTINCT rating.id_user) as jml_bintang'),
                DB::raw('CAST(ROUND(AVG(rating.bintang), 1) AS float) as bintang')
            )
            ->groupBy(
                'resep.id_resep',
                'resep.judul',
                'resep.gambar',
                'resep.deskripsi',
                'resep.id_user',
                'resep.created_at',
                'resep.updated_at',
                'users.username',
                'resep.wkt_masak',
                'resep.prs_masak',
                'resep.ktg_masak'
            )
            ->first();

        $alat = DB::table('alat_resep')
            ->where('id_resep', $id_resep)
            ->get();

        $bahan = DB::table('bahan_resep')
            ->where('id_resep', $id_resep)
            ->get();

        $langkah = DB::table('langkah_resep')
            ->where('id_resep', $id_resep)
            ->orderBy('urutan')
            ->get();

        return compact('resep', 'alat', 'bahan', 'langkah');
    }
    public function APIshowDetailRecipe($id_user)
    {
        $resepDetail = $this->showDetailRecipe($id_user);
        return response()->json([
            'data' => [
                'resep' => $resepDetail['resep'],
                'alat' => $resepDetail['alat'],
                'bahan' => $resepDetail['bahan'],
                'langkah' => $resepDetail['langkah']
            ]
        ], 200);
    }
    public function DetailPage($id_user)
    {
        $resepDetail = $this->showDetailRecipe($id_user);
        return Inertia::render('Detail', [
            'resepDetail' => [
                'resep' => $resepDetail['resep'],
                'alat' => $resepDetail['alat'],
                'bahan' => $resepDetail['bahan'],
                'langkah' => $resepDetail['langkah']
            ]
        ]);
    }


    public function AddRecipePage()
    {
        return Inertia::render('TambahResep');
    }
    public function addRecipe(Request $request)
    {
        $validated = $request->validate([
            'judul' => 'required|string|max:255',
            'deskripsi' => 'required|string',
            'gambar' => 'required|image|max:2048',
            'id_user' => 'required',
            'wkt_masak' => 'required',
            'prs_masak' => 'required',
            'ktg_masak' => 'required',
            'bahan' => 'required|json',
            'jumlah' => 'required|json',
            'satuan' => 'required|json',
            'alat' => 'required|json',
            'langkah' => 'required|json',
        ]);

        $imagePath = $request->file('gambar')->store('public/recipes');

        $recipe = Resep::create([
            'judul' => $validated['judul'],
            'deskripsi' => $validated['deskripsi'],
            'id_user' => $validated['id_user'],
            'gambar' => str_replace('public/', '', $imagePath),
            'wkt_masak' => $validated['wkt_masak'],
            'prs_masak' => $validated['prs_masak'],
            'ktg_masak' => $validated['ktg_masak'],
        ]);

        $bahanList = json_decode($validated['bahan'], true);
        $jumlahList = json_decode($validated['jumlah'], true);
        $satuanList = json_decode($validated['satuan'], true);
        foreach ($bahanList as $index => $bahan) {
            BahanResep::create([
                'id_resep' => $recipe->id_resep,
                'nama_bahan' => $bahan,
                'jml_bahan' => $jumlahList[$index],
                'stn_bahan' => $satuanList[$index],
            ]);
        }

        $alatList = json_decode($validated['alat'], true);
        foreach ($alatList as $alat) {
            AlatResep::create([
                'id_resep' => $recipe->id_resep,
                'nama_alat' => $alat,
            ]);
        }

        $langkahList = json_decode($validated['langkah'], true);
        foreach ($langkahList as $index => $langkah) {
            LangkahResep::create([
                'id_resep' => $recipe->id_resep,
                'urutan' => $index + 1,
                'cara_langkah' => $langkah,
            ]);
        }
        return $request->wantsJson() ?
            response()->json(['message' => 'Upload berhasil'], 200)
            : redirect()->back()->with('success', 'Upload berhasil');
    }
    public function showSavedRecipe($id_user)
    {
        $items = DB::table('saved')
            ->join('users', 'saved.id_user', '=', 'users.id_user')
            ->join('resep', 'saved.id_resep', '=', 'resep.id_resep')
            ->join('bahan_resep', 'resep.id_resep', '=', 'bahan_resep.id_resep')
            ->leftJoin('rating', 'resep.id_resep', '=', 'rating.id_resep')
            ->where('saved.id_user', $id_user)
            ->select(
                'resep.id_resep',
                'resep.judul',
                'resep.gambar',
                'resep.wkt_masak',
                'resep.prs_masak',
                DB::raw('CAST(ROUND(AVG(rating.bintang), 1) AS float) as bintang'),
                DB::raw('COUNT(DISTINCT rating.id_user) as jml_bintang'),
                DB::raw('COUNT(bahan_resep.nama_bahan) as jumlah_bahan')
            )
            ->groupBy('resep.id_resep', 'resep.judul', 'resep.gambar', 'resep.wkt_masak', 'resep.prs_masak')
            ->get();
        return $items;
    }
    public function APIshowSavedRecipe($id_user)
    {
        $resepSaved = $this->showSavedRecipe($id_user);
        return response()->json([
            'data' => $resepSaved,
        ], 200);
    }
    public function SavedPage($id_user)
    {
        $resepSaved = $this->showSavedRecipe($id_user);
        return Inertia::render('Tersimpan', [
            'resepSaved' => $resepSaved,
        ]);
    }



    public function FilterPage()
    {
        return Inertia::render('Search');
    }
    public function filterProduk(Request $request)
    {
        $query = DB::table('resep')
            ->join('bahan_resep', 'resep.id_resep', '=', 'bahan_resep.id_resep')
            ->leftJoin('rating', 'resep.id_resep', '=', 'rating.id_resep');

        // 🔍 Filter judul resep
        if ($request->filled('cari_resep')) {
            $query->where('resep.judul', 'like', '%' . $request->input('cari_resep') . '%');
        }

        // 👤 Filter berdasarkan username pembuat
        if ($request->filled('user_resep')) {
            $userIds = User::where('username', 'like', '%' . $request->input('user_resep') . '%')
                ->pluck('id_user');
            $query->whereIn('resep.id_user', $userIds);
        }

        // 🍲 Filter kategori
        if ($request->filled('ktg_masak')) {
            $query->whereIn('resep.ktg_masak', (array) $request->input('ktg_masak'));
        }

        // 🧄 Filter berdasarkan bahan (misal: /resepcari?bahan=telur,cabai)
        if ($request->filled('bahan')) {
            $bahanList = array_map('trim', explode(',', $request->input('bahan')));

            $query->whereIn('resep.id_resep', function ($subquery) use ($bahanList) {
                $subquery->select('id_resep')
                    ->from('bahan_resep')
                    ->where(function ($q) use ($bahanList) {
                        foreach ($bahanList as $bahan) {
                            $q->orWhere('nama_bahan', 'like', '%' . $bahan . '%');
                        }
                    });
            });
        }



        // 📅 Urutkan berdasarkan tanggal
        if ($request->filled('tgl_masak')) {
            $query->orderBy('resep.created_at', $request->input('tgl_masak'));
        }


        $produk = $query->select(
            'resep.id_resep',
            'resep.judul',
            'resep.gambar',
            'resep.wkt_masak',
            'resep.prs_masak',
            DB::raw('CAST(ROUND(AVG(rating.bintang), 1) AS float) as bintang'),
            DB::raw('COUNT(DISTINCT rating.id_user) as jml_bintang'),
            DB::raw('COUNT(bahan_resep.nama_bahan) as jumlah_bahan')
        )
            ->groupBy('resep.id_resep', 'resep.judul', 'resep.gambar', 'resep.wkt_masak', 'resep.prs_masak')
            ->get();

        return response()->json([
            'data' => $produk
        ], 200);
    }


    public function UpdatePage($id_user)
    {
        $resepDetail = $this->showDetailRecipe($id_user);
        return Inertia::render('EditResep', [
            'existingResep' => [
                'resep' => $resepDetail['resep'],
                'alat' => $resepDetail['alat'],
                'bahan' => $resepDetail['bahan'],
                'langkah' => $resepDetail['langkah']
            ]
        ]);
    }
    public function updateResep(Request $request)
    {
        $request->validate([
            'id_resep' => 'required',
            'judul' => 'required|string|max:255',
            'deskripsi' => 'required|string',
            'wkt_masak' => 'required',
            'prs_masak' => 'required',
            'ktg_masak' => 'required',
            'bahan' => 'required|json',
            'jumlah' => 'required|json',
            'satuan' => 'required|json',
            'alat' => 'required|json',
            'langkah' => 'required|json',
        ]);

        try {
            DB::beginTransaction();

            $resep = Resep::findOrFail($request->id_resep);

            if ($resep->id_user != auth()->id()) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Anda tidak memiliki izin untuk mengubah resep ini'
                ], 403);
            }

            $resep->judul = $request->judul;
            $resep->deskripsi = $request->deskripsi;
            $resep->wkt_masak = $request->wkt_masak;
            $resep->prs_masak = $request->prs_masak;
            $resep->ktg_masak = $request->ktg_masak;

            if ($request->hasFile('gambar')) {
                if ($resep->gambar && Storage::exists($resep->gambar)) {
                    Storage::delete($resep->gambar);
                }

                $path = $request->file('gambar')->store('resep_images', 'public');
                $resep->gambar = $path;
            }

            $resep->save();

            $bahan = json_decode($request->bahan, true);
            $jumlah = json_decode($request->jumlah, true);
            $satuan = json_decode($request->satuan, true);
            $resep->bahanReseps()->delete();
            foreach ($bahan as $index => $item) {
                if (!empty(trim($item))) {
                    $resep->bahanReseps()->create([
                        'nama_bahan' => $item,
                        'jml_bahan' => $jumlah[$index],
                        'stn_bahan' => $satuan[$index]
                    ]);
                }
            }

            $alat = json_decode($request->alat, true);
            $resep->alatReseps()->delete();
            foreach ($alat as $item) {
                if (!empty(trim($item))) {
                    $resep->alatReseps()->create(['nama_alat' => $item]);
                }
            }

            $langkah = json_decode($request->langkah, true);
            $resep->langkahReseps()->delete();
            foreach ($langkah as $index => $item) {
                if (!empty(trim($item))) {
                    $resep->langkahReseps()->create([
                        'cara_langkah' => $item,
                        'urutan' => $index + 1
                    ]);
                }
            }

            DB::commit();

            return response()->json([
                'status' => 'success',
                'message' => 'Resep berhasil diperbarui',
                'data' => $resep
            ]);
        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json([
                'status' => 'error',
                'message' => 'Gagal memperbarui resep',
                'error' => $e->getMessage()
            ], 500);
        }
    }
    public function deleteResep(Request $request)
    {
        $request->validate([
            'id_resep' => 'required|exists:resep,id_resep'
        ]);

        $id_resep = $request->input('id_resep');

        try {
            DB::beginTransaction();
            $resep = Resep::findOrFail($id_resep);
            if ($resep->id_user != auth()->id()) {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Anda tidak memiliki izin untuk menghapus resep ini'
                ], 403);
            }

            BahanResep::where('id_resep', $id_resep)->delete();
            AlatResep::where('id_resep', $id_resep)->delete();
            LangkahResep::where('id_resep', $id_resep)->delete();
            Rating::where('id_resep', $id_resep)->delete();
            Saved::where('id_resep', $id_resep)->delete();

            if ($resep->gambar && Storage::exists($resep->gambar)) {
                Storage::delete($resep->gambar);
            }

            $resep->delete();
            DB::commit();
            return response()->json([
                'status' => 'success',
                'message' => 'Resep berhasil dihapus'
            ], 200);
        } catch (\Exception $e) {
            DB::rollBack();
            return response()->json([
                'status' => 'error',
                'message' => 'Gagal menghapus resep',
                'error' => $e->getMessage()
            ], 500);
        }
    }


}
