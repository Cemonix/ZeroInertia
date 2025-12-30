<template>
    <PublicLayout>
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-content">
                <h1 class="hero-headline">Built to Eliminate Friction from Productivity</h1>
                <p class="hero-subheadline">
                    Zero Inertia was born from a simple observation: productivity tools often create more work than they save.
                </p>
            </div>
        </section>

        <!-- Mission Statement -->
        <section class="landing-section">
            <div class="landing-section-header">
                <h2 class="section-headline">Our Mission</h2>
            </div>
            <div class="content-block">
                <p>
                    Switching between task managers, note apps, and tracking systems creates cognitive overhead and kills momentum.
                    Every context switch costs you time and mental energy that could be better spent on actually getting things done.
                </p>
                <p>
                    We set out to build something different—a unified ecosystem where everything works together seamlessly.
                    No more copy-pasting between apps. No more context switching. Just one platform that keeps you moving forward.
                </p>
                <p>
                    Zero Inertia means zero friction. It means the tools get out of your way so you can focus on what matters:
                    achieving your goals, learning new things, and building the life you want.
                </p>
            </div>
        </section>

        <!-- Core Values -->
        <section class="landing-section">
            <div class="landing-section-header">
                <h2 class="section-headline">Core Values</h2>
            </div>
            <div class="features-grid">
                <FeatureCard
                    icon="infinity"
                    title="Zero Friction"
                    description="Every feature is designed to reduce, not increase, overhead. We obsess over making things simple and intuitive."
                />
                <FeatureCard
                    icon="check-square"
                    title="Unified Experience"
                    description="One platform for tasks, notes, tracking, and insights. Everything connected, everything accessible."
                />
                <FeatureCard
                    icon="chart-line"
                    title="Privacy-First"
                    description="Your data is yours. We use secure Google OAuth and never sell your information to third parties."
                />
                <FeatureCard
                    icon="trophy"
                    title="Continuously Improving"
                    description="We're constantly refining based on user feedback. Your productivity ecosystem evolves with you."
                />
            </div>
        </section>

        <!-- Final CTA -->
        <CTASection
            headline="Join the Zero Inertia Community"
            description="Start your productivity journey today."
            cta-label="Get Started Free"
            :cta-action="handleSignUp"
        />
    </PublicLayout>
</template>

<script setup lang="ts">
import PublicLayout from '@/layouts/PublicLayout.vue';
import FeatureCard from '@/components/public/FeatureCard.vue';
import CTASection from '@/components/public/CTASection.vue';

function handleSignUp() {
    window.location.href = '/api/v1/auth/google/login';
}
</script>

<style scoped>
.hero-section {
    background: var(--landing-gradient-primary);
    padding: 4rem 2rem;
    text-align: center;
    color: white;
}

.hero-content {
    max-width: 900px;
    margin: 0 auto;
}

.hero-headline {
    font-size: var(--landing-section-font-size);
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 1rem;
}

.hero-subheadline {
    font-size: 1.25rem;
    line-height: 1.5;
    opacity: 0.95;
}

.content-block {
    max-width: 800px;
    margin: 0 auto;
    color: var(--p-text-color);
    line-height: 1.8;
}

.content-block p {
    margin-bottom: 1.5rem;
}

.tech-list {
    margin: 2rem 0;
    padding-left: 1.5rem;
}

.tech-list li {
    margin-bottom: 1rem;
    line-height: 1.6;
}

.highlight {
    background: var(--p-content-hover-background);
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid var(--p-primary-color);
    margin-top: 2rem;
}
</style>
