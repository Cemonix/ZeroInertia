<template>
    <div class="feature-card">
        <div class="feature-icon">
            <FontAwesomeIcon :icon="icon" />
        </div>
        <h3 class="feature-title">{{ title }}</h3>
        <p class="feature-description">{{ description }}</p>
        <router-link v-if="learnMoreLink" :to="learnMoreLink" class="feature-link">
            Learn more →
        </router-link>
    </div>
</template>

<script setup lang="ts">
interface Props {
    icon: string;
    title: string;
    description: string;
    learnMoreLink?: string;
}

defineProps<Props>();
</script>

<style scoped>
.feature-card {
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: var(--landing-card-border-radius);
    padding: 2rem;
    box-shadow: var(--landing-card-shadow);
    transition: box-shadow 0.3s ease, transform 0.3s ease;
    text-align: center;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.feature-card:hover {
    box-shadow: var(--landing-card-shadow-hover);
    transform: translateY(-4px);
}

.feature-icon {
    font-size: 3rem;
    background: var(--landing-gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1rem;
}

.feature-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--p-text-color);
}

.feature-description {
    color: var(--p-text-muted-color);
    line-height: 1.6;
    margin-bottom: 1rem;
    flex: 1;
}

.feature-link {
    color: var(--p-primary-color);
    text-decoration: none;
    font-weight: 500;
    transition: opacity 0.2s ease;
}

.feature-link:hover {
    opacity: 0.8;
}
</style>
