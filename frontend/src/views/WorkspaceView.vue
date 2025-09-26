<template>
  <div class="workspace">
    <!-- Header -->
    <header class="workspace-header">
      <div class="header-content">
        <div class="header-left">
          <div class="logo-section">
            <div class="logo-icon">
              <span>ZI</span>
            </div>
            <h1 class="workspace-title">Zero Inertia</h1>
          </div>
        </div>

        <div class="header-right">
          <Button
            icon="pi pi-sign-out"
            label="Logout"
            @click="handleLogout"
            class="logout-btn"
            text
          />
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="workspace-main">
      <div class="workspace-container">
        <!-- Welcome Section -->
        <section class="welcome-section">
          <div class="welcome-content">
            <h2 class="welcome-title">Welcome back!</h2>
            <p class="welcome-subtitle">Ready to tackle your tasks with zero inertia?</p>
          </div>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">
                <i class="pi pi-check-circle"></i>
              </div>
              <div class="stat-content">
                <span class="stat-number">0</span>
                <span class="stat-label">Tasks Completed</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <i class="pi pi-clock"></i>
              </div>
              <div class="stat-content">
                <span class="stat-number">0h</span>
                <span class="stat-label">Time Tracked</span>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">
                <i class="pi pi-bolt"></i>
              </div>
              <div class="stat-content">
                <span class="stat-number">0</span>
                <span class="stat-label">Active Streak</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Quick Actions -->
        <section class="quick-actions">
          <h3 class="section-title">Quick Actions</h3>
          <div class="actions-grid">
            <Card class="action-card">
              <template #content>
                <div class="action-content">
                  <i class="pi pi-plus action-icon"></i>
                  <h4>Create Task</h4>
                  <p>Add a new task to your list</p>
                  <Button label="Create" class="action-button" />
                </div>
              </template>
            </Card>

            <Card class="action-card">
              <template #content>
                <div class="action-content">
                  <i class="pi pi-play action-icon"></i>
                  <h4>Start Timer</h4>
                  <p>Begin tracking time on a task</p>
                  <Button label="Start" class="action-button" />
                </div>
              </template>
            </Card>

            <Card class="action-card">
              <template #content>
                <div class="action-content">
                  <i class="pi pi-chart-line action-icon"></i>
                  <h4>View Analytics</h4>
                  <p>See your productivity insights</p>
                  <Button label="View" class="action-button" />
                </div>
              </template>
            </Card>
          </div>
        </section>

        <!-- Recent Tasks Placeholder -->
        <section class="recent-tasks">
          <div class="section-header">
            <h3 class="section-title">Recent Tasks</h3>
            <Button label="View All" text />
          </div>
          <Card class="empty-state">
            <template #content>
              <div class="empty-content">
                <i class="pi pi-inbox empty-icon"></i>
                <h4>No tasks yet</h4>
                <p>Create your first task to get started with Zero Inertia</p>
                <Button label="Create Your First Task" />
              </div>
            </template>
          </Card>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { AuthService } from '@/services/authService'
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogout = async () => {
  try {
    await AuthService.logout()
    router.push('/')
  } catch (error) {
    console.error('Logout failed:', error)
    // Still redirect even if logout fails
    router.push('/')
  }
}
</script>

<style scoped>
.workspace {
  min-height: 100vh;
  background: var(--surface-ground);
  display: flex;
  flex-direction: column;
}

/* Header */
.workspace-header {
  background: white;
  border-bottom: 1px solid var(--surface-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 4rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-icon {
  width: 2rem;
  height: 2rem;
  background: linear-gradient(135deg, var(--blue-500), var(--purple-600));
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon span {
  color: white;
  font-weight: bold;
  font-size: 0.875rem;
}

.workspace-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

:deep(.logout-btn) {
  color: var(--text-color-secondary) !important;
}

/* Main Content */
.workspace-main {
  flex: 1;
  padding: 2rem 0;
}

.workspace-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

/* Welcome Section */
.welcome-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.welcome-content {
  text-align: center;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
  background: linear-gradient(135deg, var(--blue-500), var(--purple-600));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-subtitle {
  font-size: 1.125rem;
  color: var(--text-color-secondary);
  margin: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  background: white;
  border: 1px solid var(--surface-border);
  border-radius: 0.75rem;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s;
}

.stat-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 3rem;
  height: 3rem;
  background: linear-gradient(135deg, var(--blue-100), var(--purple-100));
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--blue-600);
  font-size: 1.25rem;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-color);
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-color-secondary);
  margin-top: 0.25rem;
}

/* Quick Actions */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.action-card {
  transition: all 0.2s;
}

.action-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.action-content {
  text-align: center;
  padding: 1rem;
}

.action-icon {
  font-size: 2.5rem;
  color: var(--blue-500);
  margin-bottom: 1rem;
}

.action-content h4 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.action-content p {
  color: var(--text-color-secondary);
  margin: 0 0 1.5rem 0;
  line-height: 1.5;
}

.action-button {
  width: 100%;
}

/* Recent Tasks */
.recent-tasks {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-state {
  border: 2px dashed var(--surface-border);
  background: var(--surface-50);
}

.empty-content {
  text-align: center;
  padding: 3rem 2rem;
}

.empty-icon {
  font-size: 3rem;
  color: var(--text-color-secondary);
  margin-bottom: 1rem;
}

.empty-content h4 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 0.5rem 0;
}

.empty-content p {
  color: var(--text-color-secondary);
  margin: 0 0 2rem 0;
  line-height: 1.5;
}

/* Responsive */
@media (max-width: 768px) {
  .workspace-container {
    padding: 0 1rem;
    gap: 2rem;
  }

  .welcome-title {
    font-size: 2rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .actions-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>