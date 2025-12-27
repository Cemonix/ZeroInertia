<template>
    <PublicLayout>
        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-content">
                <h1 class="hero-headline">Simple, Transparent Pricing</h1>
                <p class="hero-subheadline">
                    Start free. Upgrade when you're ready.
                </p>
            </div>
        </section>

        <!-- Pricing Tiers -->
        <section class="landing-section">
            <div class="pricing-grid">
                <div class="pricing-card">
                    <div class="pricing-badge">Current Plan</div>
                    <h3 class="pricing-name">Free Beta</h3>
                    <div class="pricing-price">$0</div>
                    <div class="pricing-interval">/month</div>
                    <ul class="pricing-features">
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>Unlimited tasks and notes</span>
                        </li>
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>All task management features</span>
                        </li>
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>Knowledge hub with folders</span>
                        </li>
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>Media tracking</span>
                        </li>
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>Statistics and streaks</span>
                        </li>
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>Google OAuth sign-in</span>
                        </li>
                    </ul>
                    <Button
                        @click="handleSignUp"
                        label="Get Started Free"
                        class="pricing-cta"
                        size="large"
                    />
                </div>

                <div class="pricing-card highlighted">
                    <div class="pricing-badge">Coming Soon</div>
                    <h3 class="pricing-name">Pro</h3>
                    <div class="pricing-price">$5</div>
                    <div class="pricing-interval">/month</div>
                    <ul class="pricing-features">
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>Everything in Free</span>
                        </li>
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>AI-powered insights (future)</span>
                        </li>
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>Advanced analytics</span>
                        </li>
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>Priority support</span>
                        </li>
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>Team collaboration (future)</span>
                        </li>
                        <li>
                            <FontAwesomeIcon icon="check-circle" class="check-icon" />
                            <span>Custom integrations</span>
                        </li>
                    </ul>
                    <Button
                        label="Join Waitlist"
                        class="pricing-cta"
                        size="large"
                        disabled
                    />
                </div>
            </div>
        </section>

        <!-- FAQ Section -->
        <section class="landing-section">
            <div class="section-header">
                <h2 class="section-headline">Frequently Asked Questions</h2>
            </div>
            <div class="faq-container">
                <div class="faq-item">
                    <h3 class="faq-question">Is Zero Inertia really free?</h3>
                    <p class="faq-answer">
                        Yes! During beta, all features are free with no credit card required. We want you to experience
                        the full power of Zero Inertia before we introduce a Pro tier.
                    </p>
                </div>

                <div class="faq-item">
                    <h3 class="faq-question">Will I lose my data when Pro launches?</h3>
                    <p class="faq-answer">
                        Absolutely not. Your data is always yours, and the free tier will continue after Pro launches.
                        You'll never lose access to your tasks, notes, or tracking data.
                    </p>
                </div>

                <div class="faq-item">
                    <h3 class="faq-question">What payment methods do you accept?</h3>
                    <p class="faq-answer">
                        We'll support all major credit cards (Visa, Mastercard, American Express) when Pro launches.
                        We're also exploring support for PayPal and other payment methods.
                    </p>
                </div>

                <div class="faq-item">
                    <h3 class="faq-question">Can I cancel anytime?</h3>
                    <p class="faq-answer">
                        Yes! When Pro launches, you'll be able to cancel your subscription at any time with no penalties.
                        You'll retain access to your data on the free tier.
                    </p>
                </div>
            </div>
        </section>

        <!-- Final CTA -->
        <CTASection
            headline="Start Your Productivity Journey Today"
            description="No credit card required. Sign up free and start organizing your life."
            cta-label="Get Started Free"
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

.pricing-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 2rem;
    max-width: 900px;
    margin: 0 auto;
}

.pricing-cta {
    width: 100%;
    margin-top: auto;
}

.faq-container {
    max-width: 800px;
    margin: 3rem auto 0;
}

.faq-item {
    margin-bottom: 2.5rem;
}

.faq-question {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--p-text-color);
    margin-bottom: 0.75rem;
}

.faq-answer {
    color: var(--p-text-muted-color);
    line-height: 1.7;
}
</style>
