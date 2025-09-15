<template>
  <div class="public-layout">
    <nav class="navbar">
      <div class="navbar-container">
        <div class="logo-section">
          <div class="logo-icon">
          <span>ZI</span>
          </div>
          <span class="logo-text">Zero Inertia</span>
        </div>

        <div class="nav-actions">
          <Button
            label="Sign In"
            @click="handleSignIn"
            class="nav-button-ghost"
          />
          <Button
            label="Get Started"
            @click="handleGetStarted"
            class="nav-button"
          />
        </div>
      </div>
    </nav>
    <main class="main-content">
      <slot />
    </main>

    <footer class="footer">
      <div class="footer-container">
        <p>&copy; 2025 Zero Inertia. Built with ❤️ for productivity.</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const handleSignIn = () => {
  // TODO: Navigate to OAuth login
  console.log('Sign in clicked')
}

const handleGetStarted = () => {
  // TODO: Navigate to OAuth registration/login (same flow)
  console.log('Get started clicked')
}
</script>

<style scoped>
.public-layout {
  width: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, var(--blue-100) 0%, var(--purple-100) 100%);
}

.navbar {
  width: 100%;
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--blue-200);
  flex-shrink: 0;
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 4rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-icon {
  width: 2rem;
  height: 2rem;
  background: linear-gradient(135deg, var(--blue-500), var(--purple-600));
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon span {
  color: white;
  font-weight: bold;
  font-size: 0.875rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--grey-900);
}

.main-content {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.footer {
  width: 100%;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(8px);
  border-top: 1px solid var(--blue-200);
  flex-shrink: 0;
}

.footer-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  text-align: center;
  color: var(--grey-500);
}

.nav-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

:deep(.nav-button-ghost) {
  background: transparent !important;
  color: var(--grey-600) !important;
  border: 1px solid transparent !important;
  padding: 0.5rem 1rem !important;
  border-radius: 0.5rem !important;
  font-weight: 500 !important;
  transition: all 0.2s !important;
}

:deep(.nav-button-ghost:hover) {
  background: rgba(255, 255, 255, 0.5) !important;
  color: var(--grey-800) !important;
}
</style>
