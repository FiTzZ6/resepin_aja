<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ChatbotController extends Controller
{
    /**
     * Kirim pesan teks ke server Flask (chatbot NLP)
     */
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

    /**
     * Kirim file gambar ke server Flask (model CNN)
     */
    public function handleImage(Request $request)
    {
        $request->validate([
            'file' => 'required|file|mimes:jpg,jpeg,png|max:5120', // max 5MB
        ]);

        $file = $request->file('file');

        try {
            $result = $this->predictImageFile($file);

            return response()->json([
                'status' => 'success',
                'data' => $result
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => $e->getMessage()
            ], 500);
        }
    }

    /**
     * Fungsi helper untuk kirim file ke server Flask Vision
     */
    protected function predictImageFile($file)
    {
        $response = Http::timeout(15)->attach(
            'file',
            file_get_contents($file->getPathname()),
            $file->getClientOriginalName()
        )->post('http://localhost:5001/predict_image');

        if ($response->successful()) {
            return $response->json();
        } else {
            throw new \Exception('Gagal menerima respon dari server prediksi gambar.');
        }
    }

    public function predictImages(Request $request)
    {
        $request->validate([
            'files' => 'required|array',
            'files.*' => 'image|max:5120'
        ]);

        $http = Http::timeout(20);

        foreach ($request->file('files') as $file) {
            $http->attach(
                'files[]',
                file_get_contents($file->getPathname()),
                $file->getClientOriginalName()
            );
        }

        $response = $http->post('http://localhost:5001/predict_images');

        if ($response->successful()) {
            return response()->json($response->json());
        }

        return response()->json([
            'status' => 'error',
            'message' => 'Gagal memproses gambar'
        ], 500);
    }

}
