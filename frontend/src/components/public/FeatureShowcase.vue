<template>
    <div class="feature-showcase" :class="{ reverse: imagePosition === 'right' }">
        <div class="showcase-content">
            <h2 class="showcase-title">{{ title }}</h2>
            <ul class="showcase-features">
                <li v-for="(feature, index) in features" :key="index">
                    <FontAwesomeIcon icon="check-circle" class="check-icon" />
                    <span>{{ feature }}</span>
                </li>
            </ul>
        </div>
        <div class="showcase-image">
            <img :src="imageSrc" :alt="imageAlt" />
        </div>
    </div>
</template>

<script setup lang="ts">
interface Props {
    title: string;
    features: string[];
    imageSrc: string;
    imageAlt: string;
    imagePosition?: 'left' | 'right';
}

withDefaults(defineProps<Props>(), {
    imagePosition: 'left'
});
</script>

<style scoped>
.feature-showcase {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
    margin-bottom: 4rem;
}

.feature-showcase.reverse .showcase-content {
    order: 2;
}

.feature-showcase.reverse .showcase-image {
    order: 1;
}

.showcase-title {
    font-size: var(--landing-subsection-font-size);
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--p-text-color);
}

.showcase-features {
    list-style: none;
    padding: 0;
    margin: 0;
}

.showcase-features li {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
    color: var(--p-text-color);
    line-height: 1.6;
}

.showcase-features .check-icon {
    color: #10b981;
    font-size: 1.25rem;
    flex-shrink: 0;
    margin-top: 0.25rem;
}

.showcase-image img {
    width: 100%;
    border-radius: var(--landing-card-border-radius);
    box-shadow: var(--landing-card-shadow-hover);
}

@media (max-width: 1024px) {
    .feature-showcase {
        grid-template-columns: 1fr;
        gap: 2rem;
    }

    .feature-showcase.reverse .showcase-content,
    .feature-showcase.reverse .showcase-image {
        order: initial;
    }
}
</style>
