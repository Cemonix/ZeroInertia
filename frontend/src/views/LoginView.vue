<template>
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <h1 class="app-title">Zero Inertia</h1>
                <p class="app-subtitle">Your personal productivity ecosystem</p>
            </div>

            <div class="login-content">
                <Button
                    @click="handleLogin"
                    :loading="isLoading"
                    class="google-login-btn"
                    size="large"
                    label="Continue with Google"
                />
            </div>

            <div class="login-footer">
                <p class="footer-text">
                    By continuing, you agree to Zero Inertia's Terms of Service
                    and Privacy Policy.
                </p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const isLoading = ref(false);

function handleLogin() {
    isLoading.value = true;
    authStore.redirectToLogin();
}
</script>

<style scoped>
.login-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
}

.login-card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    padding: 3rem 2.5rem;
    max-width: 440px;
    width: 100%;
    animation: slideUp 0.4s ease-out;
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.login-header {
    text-align: center;
    margin-bottom: 1rem;
}

.app-title {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.5rem 0;
}

.app-subtitle {
    color: #6b7280;
    font-size: 1rem;
    margin: 0;
}

.login-content {
    margin-bottom: 2rem;
}

.google-login-btn {
    width: 100%;
    font-size: 1rem;
    font-weight: 500;
}

.login-footer {
    text-align: center;
}

.footer-text {
    color: #9ca3af;
    font-size: 0.875rem;
    line-height: 1.5;
    margin: 0;
}

@media (max-width: 480px) {
    .login-card {
        padding: 2rem 1.5rem;
    }

    .app-title {
        font-size: 2rem;
    }

    .app-subtitle {
        font-size: 0.9rem;
    }

    .google-login-btn {
        height: 48px;
        font-size: 0.9rem;
    }
}
</style>
