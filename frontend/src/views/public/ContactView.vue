<template>
    <PublicLayout>
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-content">
                <h1 class="hero-headline">Get in Touch</h1>
                <p class="hero-subheadline">
                    Questions, feedback, or just want to say hello? We'd love to hear from you.
                </p>
            </div>
        </section>

        <!-- Contact Info -->
        <section class="landing-section">
            <div class="contact-container">
                <div class="contact-methods">
                    <h2 class="section-headline">Contact Us</h2>
                    <p class="contact-description">
                        Have a question or feedback? The best way to reach us is via email.
                        We typically respond within 24 hours.
                    </p>

                    <div class="contact-card">
                        <div class="contact-icon">
                            <FontAwesomeIcon icon="inbox" />
                        </div>
                        <div class="contact-details">
                            <h3>Email</h3>
                            <a href="mailto:support@zeroinertia.app" class="contact-link">
                                support@zeroinertia.app
                            </a>
                        </div>
                    </div>

                    <div class="support-links">
                        <h3>Additional Resources</h3>
                        <ul>
                            <li><router-link to="/features">Browse Features</router-link></li>
                            <li><router-link to="/pricing">View Pricing</router-link></li>
                            <li><router-link to="/about">Learn About Us</router-link></li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <!-- CTA Section -->
        <CTASection
            headline="Ready to Get Started?"
            description="Join Zero Inertia and transform your productivity."
            cta-label="Sign Up Free"
            :cta-action="handleSignUp"
        />
    </PublicLayout>
</template>

<script setup lang="ts">
import PublicLayout from '@/layouts/PublicLayout.vue';
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

.contact-container {
    max-width: 700px;
    margin: 0 auto;
}

.contact-methods h2 {
    margin-bottom: 1rem;
    text-align: center;
}

.contact-description {
    color: var(--p-text-muted-color);
    line-height: 1.7;
    margin-bottom: 2rem;
    text-align: center;
}

.contact-card {
    display: flex;
    gap: 1.5rem;
    padding: 2rem;
    background: var(--p-content-background);
    border: 1px solid var(--p-content-border-color);
    border-radius: var(--landing-card-border-radius);
    box-shadow: var(--landing-card-shadow);
    margin-bottom: 2rem;
}

.contact-icon {
    font-size: 2.5rem;
    color: var(--p-primary-color);
}

.contact-details h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--p-text-color);
}

.contact-link {
    color: var(--p-primary-color);
    text-decoration: none;
    font-size: 1.125rem;
    font-weight: 500;
}

.contact-link:hover {
    text-decoration: underline;
}

.support-links h3 {
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--p-text-color);
}

.support-links ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.support-links li {
    margin-bottom: 0.75rem;
}

.support-links a {
    color: var(--p-primary-color);
    text-decoration: none;
    font-weight: 500;
}

.support-links a:hover {
    text-decoration: underline;
}
</style>
