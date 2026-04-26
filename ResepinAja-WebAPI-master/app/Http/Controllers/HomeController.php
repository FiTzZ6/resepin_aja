<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Carbon\Carbon;

class HomeController extends Controller
{
    public function rekomendasiWaktu()
    {
        // Ambil waktu Indonesia (WIB)
        $hour = Carbon::now('Asia/Jakarta')->hour;

        // Tentukan kategori waktu
        if ($hour >= 5 && $hour < 7) {
            $waktu = 'pagi';
        } elseif ($hour <= 11 && $hour < 15) {
            $waktu = 'siang';
        } elseif ($hour >= 15 && $hour < 18) {
            $waktu = 'sore';
        } else {
            $waktu = 'malam';
        }

        // Ambil resep random sesuai waktu
        $resep = DB::table('resep')
            ->where('ktg_masak', 'like', "%$waktu%")
            ->inRandomOrder()
            ->limit(6)
            ->get();

        // Kalau kosong → fallback random semua
        if ($resep->isEmpty()) {
            $resep = DB::table('resep')
                ->inRandomOrder()
                ->limit(6)
                ->get();
        }

        return response()->json([
            'status' => 'success',
            'waktu' => $waktu,
            'jam' => Carbon::now('Asia/Jakarta')->format('H:i'),
            'data' => $resep
        ]);
    }
}