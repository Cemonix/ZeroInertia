import { ref } from 'vue';

const isDarkMode = ref(false);

export function useTheme() {
    const toggleTheme = () => {
        const nextDarkMode = !isDarkMode.value;
        isDarkMode.value = nextDarkMode;

        if (typeof document !== 'undefined') {
            const html = document.documentElement;

            if (nextDarkMode) {
                html.classList.add('dark-mode');
            } else {
                html.classList.remove('dark-mode');
            }
        }

        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('theme.mode', nextDarkMode ? 'dark' : 'light');
        }
    };

    const initializeTheme = () => {
        if (typeof window !== 'undefined') {
            const storedTheme = localStorage.getItem('theme.mode');
            if (storedTheme === 'dark') {
                isDarkMode.value = true;
                document.documentElement.classList.add('dark-mode');
            } else if (storedTheme === 'light') {
                isDarkMode.value = false;
                document.documentElement.classList.remove('dark-mode');
            } else {
                isDarkMode.value = document.documentElement.classList.contains('dark-mode');
            }
        }
    };

    return {
        isDarkMode,
        toggleTheme,
        initializeTheme,
    };
}
