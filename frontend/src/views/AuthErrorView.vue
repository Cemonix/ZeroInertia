<template>
    <div class="auth-error-container">
        <div class="error-card">
            <div class="error-icon">
                <FontAwesomeIcon icon="exclamation-circle" />
            </div>
            <h1 class="error-title">Authentication Failed</h1>
            <p class="error-message">{{ errorMessage }}</p>
            <div class="error-actions">
                <Button
                    @click="tryAgain"
                    label="Try Again"
                    class="cta-button-primary"
                    size="large"
                />
                <Button
                    @click="goHome"
                    label="Go Home"
                    text
                    size="large"
                />
            </div>
            <p class="support-text">
                If this problem persists,
                <router-link to="/contact">contact support</router-link>.
            </p>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();

const errorMessage = ref('We couldn\'t complete your sign-in. Please try again.');

onMounted(() => {
    const message = route.query.message;
    if (message && typeof message === 'string') {
        errorMessage.value = decodeURIComponent(message.replace(/\+/g, ' '));
    }
});

function tryAgain() {
    router.push('/login');
}

function goHome() {
    router.push('/');
}
</script>

<style scoped>
.auth-error-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
}

.error-card {
    background: white;
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    padding: 3rem 2.5rem;
    max-width: 480px;
    width: 100%;
    text-align: center;
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

.error-icon {
    font-size: 4rem;
    color: #ef4444;
    margin-bottom: 1.5rem;
}

.error-title {
    font-size: 2rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 1rem;
}

.error-message {
    font-size: 1.125rem;
    color: #6b7280;
    margin-bottom: 2rem;
    line-height: 1.6;
}

.error-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}

.support-text {
    font-size: 0.875rem;
    color: #9ca3af;
}

.support-text a {
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
}

.support-text a:hover {
    text-decoration: underline;
}

@media (max-width: 480px) {
    .error-card {
        padding: 2rem 1.5rem;
    }

    .error-title {
        font-size: 1.5rem;
    }

    .error-message {
        font-size: 1rem;
    }

    .error-actions {
        flex-direction: column;
    }

    .error-actions button {
        width: 100%;
    }
}
</style>
