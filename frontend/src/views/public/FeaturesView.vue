<template>
    <PublicLayout>
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-content">
                <h1 class="hero-headline">Everything You Need. Nothing You Don't.</h1>
                <p class="hero-subheadline">
                    Zero Inertia brings professional-grade productivity tools into one unified platform.
                </p>
            </div>
        </section>

        <!-- Task Management Features -->
        <section class="landing-section">
            <div class="landing-section-header">
                <h2 class="section-headline">Task Management</h2>
                <p class="section-subheadline">
                    Powerful tools to organize your work and stay on track.
                </p>
            </div>

            <FeatureShowcase
                title="Kanban Boards"
                :features="[
                    'Visual project management with drag-and-drop interface',
                    'Organize tasks into sections and projects',
                    'Real-time updates across all your devices',
                    'Customizable workflows for any project type'
                ]"
                image-src="/screenshots/feature-kanban-board.png"
                image-alt="Kanban board view"
                image-position="right"
            />

            <FeatureShowcase
                title="Recurring Tasks"
                :features="[
                    'Daily, weekly, monthly, and yearly patterns',
                    'Flexible intervals and end conditions',
                    'Automatic task generation for habits',
                    'Never miss a repeating obligation again'
                ]"
                image-src="/screenshots/feature-recurring-tasks.png"
                image-alt="Recurring task setup"
                image-position="left"
            />

            <FeatureShowcase
                title="Natural Language Dates"
                :features="[
                    'Type &quot;tomorrow at 3pm&quot; instead of clicking through date pickers',
                    'Parse complex dates like &quot;next Monday&quot; or &quot;in 2 weeks&quot;',
                    'Fast task entry without breaking your flow',
                    'Intelligent date recognition powered by chrono-node'
                ]"
                image-src="/screenshots/feature-natural-language-dates.png"
                image-alt="Natural language date entry"
                image-position="right"
            />

            <FeatureShowcase
                title="Priority & Labels"
                :features="[
                    'Color-coded labels for quick categorization',
                    'Multi-label support for flexible organization',
                    'Priority levels (low, medium, high)',
                    'Filter and sort by any criteria'
                ]"
                image-src="/screenshots/feature-priority-labels.png"
                image-alt="Task with labels and priority"
                image-position="left"
            />
        </section>

        <!-- Knowledge Hub Features -->
        <section class="landing-section">
            <div class="landing-section-header">
                <h2 class="section-headline">Knowledge Hub</h2>
                <p class="section-subheadline">
                    Your second brain for capturing and organizing ideas.
                </p>
            </div>

            <FeatureShowcase
                title="Markdown Notes"
                :features="[
                    'Rich text editing with markdown syntax',
                    'Syntax highlighting for code blocks',
                    'Live preview as you type',
                ]"
                image-src="/screenshots/feature-notes-editor.png"
                image-alt="Markdown note editor"
                image-position="right"
            />

            <FeatureShowcase
                title="Folder Organization"
                :features="[
                    'Hierarchical folder structure for notes',
                    'Drag-and-drop to reorganize',
                    'Search across all notes instantly',
                    'Organize notes with flexible folder categories'
                ]"
                image-src="/screenshots/feature-folder-organization.png"
                image-alt="Notes folder organization"
                image-position="left"
            />
        </section>

        <!-- Tracking & Insights Features -->
        <section class="landing-section">
            <div class="landing-section-header">
                <h2 class="section-headline">Tracking & Insights</h2>
                <p class="section-subheadline">
                    Understand your productivity patterns and celebrate achievements.
                </p>
            </div>

            <FeatureShowcase
                title="Media Tracker"
                :features="[
                    'Track books, games, courses, shows, and podcasts',
                    'Status tracking: planned, in-progress, completed',
                    'Rating system and personal notes',
                    'See your learning and entertainment history'
                ]"
                image-src="/screenshots/feature-media-tracker.png"
                image-alt="Media tracker"
                image-position="right"
            />

            <FeatureShowcase
                title="Streak Visualization"
                :features="[
                    'GitHub-style calendar heatmap',
                    'Daily completion tracking',
                    'Maintain motivation with streak counters',
                    'Visualize your consistency over time'
                ]"
                image-src="/screenshots/feature-streak-calendar.png"
                image-alt="Streak calendar"
                image-position="left"
            />

            <FeatureShowcase
                title="Statistics Dashboard"
                :features="[
                    'Productivity patterns and trends analysis',
                    'Task completion rates by project',
                    'Time-based insights and charts',
                    'Data-driven productivity improvements'
                ]"
                image-src="/screenshots/feature-statistics.png"
                image-alt="Statistics dashboard"
                image-position="right"
            />
        </section>

        <!-- All-in-One Platform Features -->
        <section class="landing-section">
            <div class="landing-section-header">
                <h2 class="section-headline">All-in-One Platform</h2>
                <p class="section-subheadline">
                    Everything works together seamlessly.
                </p>
            </div>

            <div class="features-grid">
                <FeatureCard
                    icon="infinity"
                    title="Unified Interface"
                    description="Single login, single workspace. No context switching between apps. Everything you need in one place."
                />
                <FeatureCard
                    icon="check-circle"
                    title="Google OAuth"
                    description="Secure, one-click sign-in with your Google account. No password to remember, no security worries."
                />
                <FeatureCard
                    icon="chart-line"
                    title="Responsive Design"
                    description="Works beautifully on mobile, tablet, and desktop. Your productivity ecosystem wherever you go."
                />
            </div>
        </section>

        <!-- Final CTA -->
        <CTASection
            headline="See It in Action"
            description="Start organizing your life with Zero Inertia today."
            cta-label="Sign Up Free"
            :cta-action="handleSignUp"
        />
    </PublicLayout>
</template>

<script setup lang="ts">
import PublicLayout from '@/layouts/PublicLayout.vue';
import FeatureCard from '@/components/public/FeatureCard.vue';
import FeatureShowcase from '@/components/public/FeatureShowcase.vue';
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
</style>
