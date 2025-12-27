<template>
    <header class="public-header">
        <div class="header-container">
            <div class="header-logo">
                <router-link to="/">
                    <img src="/ZeroInertia_logo.png" alt="Zero Inertia" />
                </router-link>
            </div>

            <nav class="header-nav desktop-nav">
                <router-link to="/">Home</router-link>
                <router-link to="/features">Features</router-link>
                <router-link to="/about">About</router-link>
                <router-link to="/pricing">Pricing</router-link>
                <router-link to="/contact">Contact</router-link>
            </nav>

            <div class="header-actions desktop-actions">
                <Button
                    v-if="!authStore.isAuthenticated"
                    @click="handleSignUp"
                    class="cta-button-primary"
                    label="Get Started"
                    size="large"
                />
                <Button
                    v-else
                    @click="goToApp"
                    label="Go to App"
                    size="large"
                    icon="pi pi-arrow-right"
                    icon-pos="right"
                />
            </div>

            <Button
                class="mobile-menu-toggle"
                @click="isMobileMenuOpen = true"
                text
                rounded
                aria-label="Open menu"
            >
                <FontAwesomeIcon icon="bars" />
            </Button>
        </div>
    </header>

    <Drawer
        v-model:visible="isMobileMenuOpen"
        position="right"
        class="mobile-menu-drawer"
    >
        <template #header>
            <div class="mobile-header-logo">
                <img src="/ZeroInertia_logo.png" alt="Zero Inertia" />
            </div>
        </template>

        <nav class="mobile-nav">
            <router-link to="/" @click="closeMobileMenu">Home</router-link>
            <router-link to="/features" @click="closeMobileMenu">Features</router-link>
            <router-link to="/about" @click="closeMobileMenu">About</router-link>
            <router-link to="/pricing" @click="closeMobileMenu">Pricing</router-link>
            <router-link to="/contact" @click="closeMobileMenu">Contact</router-link>
        </nav>

        <div class="mobile-actions">
            <Button
                v-if="!authStore.isAuthenticated"
                @click="handleSignUp"
                class="cta-button-primary"
                label="Get Started"
                size="large"
            />
            <Button
                v-else
                @click="goToApp"
                label="Go to App"
                size="large"
                icon="pi pi-arrow-right"
                icon-pos="right"
            />
        </div>
    </Drawer>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import Drawer from 'primevue/drawer';

const router = useRouter();
const authStore = useAuthStore();
const isMobileMenuOpen = ref(false);

function handleSignUp() {
    window.location.href = '/api/v1/auth/google/login';
}

function goToApp() {
    router.push('/home');
}

function closeMobileMenu() {
    isMobileMenuOpen.value = false;
}
</script>

<style scoped>
.header-container {
    max-width: var(--landing-max-width);
    margin: 0 auto;
    padding: 1rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
}

.header-logo img {
    height: 40px;
    display: block;
}

.header-nav {
    display: flex;
    gap: 2rem;
    align-items: center;
}

.header-nav a {
    color: var(--p-text-color);
    text-decoration: none;
    font-weight: 500;
    font-size: 1rem;
    transition: color 0.2s ease;
    position: relative;
    padding-bottom: 0.5rem;
}

.header-nav a:hover {
    color: var(--p-primary-color);
}

.header-nav a.router-link-active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: var(--landing-gradient-primary);
    border-radius: 2px;
}

.header-actions {
    display: flex;
    gap: 1rem;
    align-items: center;
}

.mobile-menu-toggle {
    display: none;
    font-size: 1.5rem;
}

.mobile-header-logo {
    padding: 1rem 0;
}

.mobile-header-logo img {
    height: 36px;
}

.mobile-nav {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 1rem;
}

.mobile-nav a {
    color: var(--p-text-color);
    text-decoration: none;
    font-weight: 500;
    font-size: 1.125rem;
    padding: 1rem;
    border-radius: 8px;
    transition: background 0.2s ease;
}

.mobile-nav a:hover {
    background: var(--p-content-hover-background);
}

.mobile-nav a.router-link-active {
    background: var(--p-primary-color);
    color: white;
}

.mobile-actions {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 1px solid var(--p-content-border-color);
}

.mobile-actions button {
    width: 100%;
}

@media (max-width: 768px) {
    .header-container {
        padding: 1rem;
    }

    .header-nav.desktop-nav,
    .desktop-actions {
        display: none;
    }

    .mobile-menu-toggle {
        display: flex;
    }
}
</style>
