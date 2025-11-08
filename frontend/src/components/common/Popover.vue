<template>
    <Teleport to="body">
        <Transition name="popover-fade">
            <div v-if="visible" class="popover-overlay" @click="handleOverlayClick">
                <div
                    ref="popoverContent"
                    class="popover-container"
                    :style="containerStyle"
                    @click.stop
                >
                    <div class="popover-header">
                        <span>{{ title }}</span>
                        <Button
                            text
                            rounded
                            size="small"
                            @click="closePopover"
                        >
                            <FontAwesomeIcon icon="times" />
                        </Button>
                    </div>
                    <div class="popover-body">
                        <slot></slot>
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<script lang="ts" setup>
import { ref, computed, watch, onUnmounted } from 'vue';
import Button from 'primevue/button';

interface Props {
    visible: boolean;
    title?: string;
    width?: string;
    triggerElement?: HTMLElement | null;
}

const props = withDefaults(defineProps<Props>(), {
    title: 'Popover',
    width: '300px',
    triggerElement: null
});

const emit = defineEmits<{
    (e: 'update:visible', value: boolean): void;
}>();

const popoverContent = ref<HTMLElement | null>(null);

const containerStyle = computed(() => ({
    width: props.width
}));

function closePopover() {
    emit('update:visible', false);
}

function handleOverlayClick() {
    closePopover();
}

function handleEscape(event: KeyboardEvent) {
    if (event.key === 'Escape' && props.visible) {
        closePopover();
    }
}

// Add escape key listener
watch(() => props.visible, (newVal) => {
    if (newVal) {
        document.addEventListener('keydown', handleEscape);
    } else {
        document.removeEventListener('keydown', handleEscape);
    }
});

onUnmounted(() => {
    document.removeEventListener('keydown', handleEscape);
});
</script>

<style scoped>
.popover-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1200;
    padding: 1rem;
}

.popover-container {
    background-color: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: 8px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    max-height: 80vh;
    max-width: 95vw;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.popover-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--p-content-border-color);
    font-weight: 600;
    flex-shrink: 0;
}

.popover-body {
    padding: 1rem;
    overflow-y: auto;
}

/* Mobile responsive styles */
@media (max-width: 480px) {
    .popover-overlay {
        padding: 0.5rem;
    }

    .popover-container {
        max-width: 100%;
        width: 100% !important;
    }

    .popover-header {
        padding: 0.625rem 0.75rem;
        font-size: 0.9375rem;
    }

    .popover-body {
        padding: 0.75rem;
    }
}

/* Transition animations */
.popover-fade-enter-active,
.popover-fade-leave-active {
    transition: opacity 0.2s ease;
}

.popover-fade-enter-from,
.popover-fade-leave-to {
    opacity: 0;
}

.popover-fade-enter-active .popover-container,
.popover-fade-leave-active .popover-container {
    transition: transform 0.2s ease;
}

.popover-fade-enter-from .popover-container,
.popover-fade-leave-to .popover-container {
    transform: scale(0.95);
}
</style>
