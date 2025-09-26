<template>
  <PublicLayout>
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-background"></div>
      <div class="hero-container">
        <h1 class="hero-title">
          Beat <span class="hero-gradient">Procrastination</span> with AI
        </h1>
        <p class="hero-subtitle">
          Zero Inertia transforms your to-do list into an intelligent productivity machine.
          AI categorization, smart timing, and streak tracking that actually motivates you to get things done.
        </p>
        <div class="hero-buttons">
          <Button label="Start Free Today" @click="handleAuth" class="btn-primary-large" :disabled="authStore.isLoading"/>
        </div>
        <div v-if="errorMessage" class="error-message">
          ⚠️ {{ errorMessage }}
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section">
      <div class="features-container">
        <div class="features-header">
          <h2>Why Zero Inertia Works</h2>
          <p>Stop fighting your brain's resistance. Our AI-powered approach makes starting tasks effortless.</p>
        </div>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon brain-icon">🧠</div>
            <h3>AI Smart Categorization</h3>
            <p>Never waste time organizing again. Our AI instantly categorizes and prioritizes your tasks based on context, urgency, and your personal patterns.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon timer-icon">⏱️</div>
            <h3>Intelligent Time Tracking</h3>
            <p>Built-in timer that learns your work patterns. Get insights on your most productive hours and optimal task duration for maximum focus.</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon fire-icon">🔥</div>
            <h3>AI Motivator + Streaks</h3>
            <p>Personalized motivation with voice encouragement and visual streak tracking. Turn productivity into a game you actually want to win.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How it Works Section -->
    <section class="how-it-works-section">
      <div class="how-it-works-container">
        <div class="how-it-works-header">
          <h2>How it Works</h2>
          <p>From overwhelmed to organized in three simple steps</p>
        </div>
        <div class="steps-grid">
          <div class="step-card">
            <div class="step-number">1</div>
            <h3>Add Your Tasks</h3>
            <p>Just brain-dump everything you need to do. Don't worry about organizing - that's our job.</p>
          </div>
          <div class="step-card">
            <div class="step-number">2</div>
            <h3>AI Does the Thinking</h3>
            <p>Our AI instantly categorizes, prioritizes, and suggests the best time to tackle each task.</p>
          </div>
          <div class="step-card">
            <div class="step-number">3</div>
            <h3>Start & Build Streaks</h3>
            <p>Hit the timer, get motivated by AI coaching, and watch your productivity streaks grow.</p>
          </div>
        </div>
      </div>
    </section>

  </PublicLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Button from 'primevue/button'
import PublicLayout from '@/components/layout/PublicLayout.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()
const errorMessage = ref<string | null>(null)

// Check for OAuth error messages in URL params
onMounted(() => {
  const message = route.query.message as string
  if (message) {
    errorMessage.value = message.replace(/\+/g, ' ')
  }
})

const handleAuth = () => {
  authStore.redirectToLogin()
}
</script>

<style scoped>
.hero-section {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.hero-background {
  position: absolute;
  inset: 0;
  opacity: 0.1;
  background: linear-gradient(135deg, var(--blue-500), var(--purple-600));
  background-image: radial-gradient(circle at 25% 25%, rgba(255,255,255,0.3) 1px, transparent 1px);
  background-size: 40px 40px;
  pointer-events: none;
}

.hero-container {
  max-width: 800px;
  padding: 0 2rem;
  text-align: center;
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 4rem;
  font-weight: bold;
  color: var(--grey-900);
  margin-bottom: 1rem;
  line-height: 1.4;
}

.hero-gradient {
  background: linear-gradient(135deg, var(--blue-500), var(--purple-600));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--grey-500);
  margin-bottom: 3rem;
  line-height: 1.6;
}

.hero-buttons {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #fecaca;
  margin-bottom: 2rem;
  text-align: center;
  max-width: 500px;
  margin-left: auto;
  margin-right: auto;
}


.features-section {
  width: 100%;
  padding: 6rem 0;
  background: rgba(255, 255, 255, 0.5);
}

.features-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.features-header {
  text-align: center;
  margin-bottom: 4rem;
}

.features-header h2 {
  font-size: 2.5rem;
  font-weight: bold;
  color: var(--grey-900);
  margin-bottom: 1rem;
}

.features-header p {
  font-size: 1.125rem;
  color: var(--grey-500);
  max-width: 600px;
  margin: 0 auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.feature-card {
  text-align: center;
  padding: 1rem;
}

.feature-icon {
  width: 4rem;
  height: 4rem;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
  font-size: 1.5rem;
  transition: transform 0.3s ease;
  cursor: default;
  user-select: none;
}

.feature-icon:hover {
  transform: scale(1.05) translateY(-2px);
  transition: transform 0.3s ease;
}

.brain-icon {
  background: linear-gradient(135deg, var(--purple-500), var(--red-400));
}

.timer-icon {
  background: linear-gradient(135deg, var(--green-500), var(--green-600));
}

.fire-icon {
  background: linear-gradient(135deg, var(--yellow-500), var(--orange-500));
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--grey-900);
  margin-bottom: 1rem;
}

.feature-card p {
  color: var(--grey-500);
  line-height: 1.6;
}



.how-it-works-section {
  width: 100%;
  padding: 6rem 0;
  background: var(--grey-50);
}

.how-it-works-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.how-it-works-header {
  text-align: center;
  margin-bottom: 4rem;
}

.how-it-works-header h2 {
  font-size: 2.5rem;
  font-weight: bold;
  color: var(--grey-900);
  margin-bottom: 1rem;
}

.how-it-works-header p {
  font-size: 1.125rem;
  color: var(--grey-600);
  max-width: 600px;
  margin: 0 auto;
}

.steps-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.step-card {
  text-align: center;
  padding: 2rem 1.5rem;
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.step-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px -3px rgba(0, 0, 0, 0.1);
}

.step-number {
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, var(--blue-500), var(--purple-600));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: bold;
  margin: 0 auto 1.5rem;
}

.step-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--grey-900);
  margin-bottom: 1rem;
}

.step-card p {
  color: var(--grey-600);
  line-height: 1.6;
}


:deep(.btn-primary-large) {
  background: linear-gradient(135deg, var(--blue-600), var(--purple-600)) !important;
  color: white !important;
  border: none !important;
  padding: 1rem 2.5rem !important;
  border-radius: 0.75rem !important;
  font-size: 1.125rem !important;
  font-weight: 600 !important;
  transition: all 0.2s !important;
}

:deep(.btn-primary-large:hover) {
  background: linear-gradient(135deg, var(--blue-700), var(--purple-700)) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.4) !important;
}


@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-buttons {
    flex-direction: column;
    align-items: center;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .steps-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .how-it-works-header h2 {
    font-size: 2rem;
  }
}
</style>