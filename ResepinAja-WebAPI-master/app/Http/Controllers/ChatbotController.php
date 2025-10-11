<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ChatbotController extends Controller
{
    public function sendMessage(Request $request)
    {
        $request->validate([
            'message' => 'required|string',
        ]);

        try {
            // Kirim pesan ke Flask chatbot API
            $response = Http::timeout(10)->post('http://localhost:5000/chat', [
                'message' => $request->input('message'),
            ]);

            // Jika Flask merespon dengan sukses
            if ($response->successful()) {
                return response()->json([
                    'status' => 'success',
                    'data' => $response->json(),
                ]);
            } else {
                return response()->json([
                    'status' => 'error',
                    'message' => 'Gagal menerima respon dari Chatbot Python.',
                    'error' => $response->body(),
                ], $response->status());
            }
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => 'Tidak dapat terhubung ke server Chatbot Python.',
                'error' => $e->getMessage(),
            ], 500);
        }
    }
}
