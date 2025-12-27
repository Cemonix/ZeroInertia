<template>
    <footer class="public-footer">
        <div class="footer-container">
            <div class="footer-brand">
                <h3>Zero Inertia</h3>
                <p>Your personal productivity ecosystem - combining task management, knowledge hub, and achievement tracking in one unified platform.</p>
            </div>

            <div class="footer-links">
                <h4>Product</h4>
                <ul>
                    <li><router-link to="/features">Features</router-link></li>
                    <li><router-link to="/pricing">Pricing</router-link></li>
                    <li><router-link to="/about">About</router-link></li>
                </ul>
            </div>

            <div class="footer-links">
                <h4>Support</h4>
                <ul>
                    <li><router-link to="/contact">Contact</router-link></li>
                    <li><a href="#">Terms of Service</a></li>
                    <li><a href="#">Privacy Policy</a></li>
                </ul>
            </div>
        </div>

        <div class="footer-bottom">
            <p>&copy; 2025 Zero Inertia. All rights reserved.</p>
        </div>
    </footer>
</template>

<script setup lang="ts">
// No script needed for static footer
</script>

<style scoped>
.public-footer {
    background: var(--p-content-background);
    border-top: 1px solid var(--p-content-border-color);
    padding: 3rem 2rem;
    margin-top: 6rem;
}

.footer-container {
    max-width: var(--landing-max-width);
    margin: 0 auto;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 3rem;
}

.footer-brand h3 {
    font-size: 1.25rem;
    margin-bottom: 0.5rem;
    background: var(--landing-gradient-primary);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.footer-brand p {
    color: var(--p-text-muted-color);
    font-size: 0.9rem;
    line-height: 1.6;
}

.footer-links h4 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: var(--p-text-color);
}

.footer-links ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.footer-links li {
    margin-bottom: 0.75rem;
}

.footer-links a {
    color: var(--p-text-muted-color);
    text-decoration: none;
    font-size: 0.9rem;
    transition: color 0.2s ease;
}

.footer-links a:hover {
    color: var(--p-primary-color);
}

.footer-bottom {
    max-width: var(--landing-max-width);
    margin: 2rem auto 0;
    padding-top: 2rem;
    border-top: 1px solid var(--p-content-border-color);
    text-align: center;
    color: var(--p-text-muted-color);
    font-size: 0.875rem;
}

@media (max-width: 1024px) {
    .footer-container {
        grid-template-columns: 1fr 1fr;
    }

    .footer-brand {
        grid-column: 1 / -1;
    }
}

@media (max-width: 768px) {
    .footer-container {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
}
</style>
