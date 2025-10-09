<template>
    <div class="chatbot-container p-4">
        <h3 class="fw-bold mb-3 text-center">Chat Asisten Resepin Aja 🍳</h3>

        <div class="chat-box border rounded-4 p-3 mb-3 overflow-auto" style="height: 400px;">
            <div v-for="(chat, index) in chats" :key="index" class="mb-2">
                <div class="fw-bold text-primary">Kamu:</div>
                <div class="bg-light p-2 rounded mb-1">{{ chat.user }}</div>
                <div class="fw-bold text-success">Chatbot:</div>
                <div class="bg-warning-subtle p-2 rounded">{{ chat.bot }}</div>
            </div>
        </div>

        <div class="d-flex">
            <input v-model="message" class="form-control me-2" placeholder="Tanya resep apa hari ini..."
                @keyup.enter="sendMessage" />
            <button @click="sendMessage" class="btn btn-danger fw-bold">Kirim</button>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const message = ref('')
const chats = ref([])

const sendMessage = async () => {
    if (!message.value) return

    const userMsg = message.value
    message.value = ''

    const { data } = await axios.post('/chatbot', { message: userMsg })

    chats.value.push({
        user: userMsg,
        bot: data.bot_response
    })
}
</script>

<style scoped>
.chatbot-container {
    max-width: 600px;
    margin: 0 auto;
}
</style>
