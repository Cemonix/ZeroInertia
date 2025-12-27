<template>
    <div class="public-layout">
        <PublicHeader />
        <main class="public-content">
            <slot />
        </main>
        <PublicFooter />
    </div>
</template>

<script setup lang="ts">
import PublicHeader from '@/components/public/PublicHeader.vue';
import PublicFooter from '@/components/public/PublicFooter.vue';
</script>

<style scoped>
.public-layout {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.public-content {
    flex: 1;
}
</style>
