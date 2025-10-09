<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ChatbotController extends Controller
{
    public function sendMessage(Request $request)
    {
        $request->validate([
            'message' => 'required|string'
        ]);@

        $response = Http::post('http://127.0.0.1:5000/chat', [
            'message' => $request->message
        ]);

        $botResponse = $response->json();

        return response()->json([
            'user_message' => $request->message,
            'bot_response' => $botResponse['message'] ?? 'Maaf, chatbot tidak merespons.',
            'redirect_url' => $botResponse['url'] ?? null,
            'type' => $botResponse['type'] ?? 'text'
        ]);

    }
}
