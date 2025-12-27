<template>
    <div class="cta-section landing-section">
        <div class="cta-content">
            <h2 class="cta-headline">{{ headline }}</h2>
            <p v-if="description" class="cta-description">{{ description }}</p>
            <div class="cta-actions">
                <Button
                    @click="ctaAction"
                    :label="ctaLabel"
                    class="cta-button-primary"
                    size="large"
                />
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
interface Props {
    headline: string;
    description?: string;
    ctaLabel: string;
    ctaAction: () => void;
}

defineProps<Props>();
</script>

<style scoped>
.cta-section {
    background: var(--landing-gradient-primary);
    padding: 4rem 2rem;
    text-align: center;
    border-radius: 16px;
    color: white;
    margin: 4rem auto;
}

.cta-content {
    max-width: 800px;
    margin: 0 auto;
}

.cta-headline {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.cta-description {
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.95;
}

.cta-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

@media (max-width: 768px) {
    .cta-headline {
        font-size: 1.75rem;
    }

    .cta-description {
        font-size: 1rem;
    }
}
</style>
