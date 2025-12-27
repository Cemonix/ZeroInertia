<template>
    <PublicLayout>
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-content">
                <h1 class="hero-headline">Overcome Inertia. Achieve More.</h1>
                <p class="hero-subheadline">
                    Zero Inertia is your all-in-one productivity ecosystem—combining task management,
                    knowledge hub, achievement tracking, and insights to keep you moving forward.
                </p>
                <div class="hero-actions">
                    <Button
                        @click="handleSignUp"
                        label="Get Started with Google"
                        class="cta-button-primary"
                        size="large"
                    />
                    <Button
                        @click="scrollToFeatures"
                        label="See How It Works"
                        class="cta-button-secondary"
                        size="large"
                    />
                </div>
            </div>
        </section>

        <!-- Problem Statement -->
        <section class="landing-section">
            <div class="section-header">
                <h2 class="section-headline">Too Many Tools. Too Much Friction.</h2>
                <p class="section-subheadline">
                    Switching between task managers, note apps, and tracking spreadsheets creates friction.
                    Zero Inertia eliminates the overhead by unifying everything you need in one seamless platform.
                </p>
            </div>
        </section>

        <!-- Key Features Grid -->
        <section class="landing-section" ref="featuresSection">
            <div class="section-header">
                <h2 class="section-headline">Everything You Need in One Place</h2>
            </div>
            <div class="features-grid">
                <FeatureCard
                    icon="check-square"
                    title="Powerful Task Management"
                    description="Kanban boards, recurring tasks, natural language dates, and smart organization. Stay on top of your work with visual project management."
                    learn-more-link="/features"
                />
                <FeatureCard
                    icon="pen"
                    title="Knowledge Hub"
                    description="Markdown notes, folder organization, and your second brain—all integrated. Capture ideas and link them to tasks seamlessly."
                    learn-more-link="/features"
                />
                <FeatureCard
                    icon="infinity"
                    title="All-in-One Platform"
                    description="Tasks + Notes + Media Tracking + Statistics = Complete productivity ecosystem. One login, one platform, zero friction."
                    learn-more-link="/features"
                />
            </div>
        </section>

        <!-- Feature Showcases -->
        <section class="landing-section">
            <FeatureShowcase
                title="Organize with Kanban Boards & Smart Sections"
                :features="[
                    'Visual project management with drag-and-drop Kanban boards',
                    'Recurring tasks for habits and repeating work',
                    'Natural language date entry: \'tomorrow at 3pm\' or \'next Monday\'',
                    'Priority levels, labels, and checklists for detailed organization'
                ]"
                image-src="/screenshots/feature-kanban-board.png"
                image-alt="Kanban board with project tasks"
                image-position="right"
            />

            <FeatureShowcase
                title="Build Your Second Brain"
                :features="[
                    'Markdown-powered notes with folder organization',
                    'Search across all your knowledge instantly',
                    'Link notes to tasks for context-rich productivity',
                    'Version history and note snapshots for peace of mind'
                ]"
                image-src="/screenshots/feature-notes-editor.png"
                image-alt="Notes editor with markdown"
                image-position="left"
            />

            <FeatureShowcase
                title="Everything Connected. Everything Accessible."
                :features="[
                    'Track books, games, courses, and media you consume',
                    'Visualize streaks and productivity patterns',
                    'Statistics dashboard for insights into your work',
                    'One login, one platform, zero context switching'
                ]"
                image-src="/screenshots/feature-today-view.png"
                image-alt="Today view with calendar and statistics"
                image-position="right"
            />
        </section>

        <!-- Final CTA -->
        <CTASection
            headline="Ready to Overcome Inertia?"
            description="Start unifying your productivity with Zero Inertia today."
            cta-label="Sign Up with Google - It's Free"
            :cta-action="handleSignUp"
        />
    </PublicLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import PublicLayout from '@/layouts/PublicLayout.vue';
import FeatureCard from '@/components/public/FeatureCard.vue';
import FeatureShowcase from '@/components/public/FeatureShowcase.vue';
import CTASection from '@/components/public/CTASection.vue';

const featuresSection = ref<HTMLElement | null>(null);

function handleSignUp() {
    window.location.href = '/api/v1/auth/google/login';
}

function scrollToFeatures() {
    featuresSection.value?.scrollIntoView({ behavior: 'smooth' });
}
</script>

<style scoped>
/* Hero Section */
.hero-section {
    background: var(--landing-gradient-primary);
    padding: 6rem 2rem;
    text-align: center;
    color: white;
}

.hero-content {
    max-width: 900px;
    margin: 0 auto;
}

.hero-headline {
    font-size: var(--landing-hero-font-size);
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 1.5rem;
}

.hero-subheadline {
    font-size: 1.5rem;
    line-height: 1.5;
    margin-bottom: 2.5rem;
    opacity: 0.95;
}

.hero-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

@media (max-width: 768px) {
    .hero-section {
        padding: 4rem 1.5rem;
    }

    .hero-headline {
        font-size: 2rem;
    }

    .hero-subheadline {
        font-size: 1.125rem;
    }
}
</style>
