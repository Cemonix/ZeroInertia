import { createApp } from "vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import Aura from "@primeuix/themes/aura";
import ToastService from "primevue/toastservice";
import ConfirmationService from "primevue/confirmationservice";
import "./styles/main.css";
import "highlight.js/styles/github-dark.css";
import App from "./App.vue";
import router from "./router";
import { useAuthStore } from "@/stores/auth";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { registerIcons } from "@/config/icons";

// PrimeVue components
import Button from "primevue/button";
import Toast from "primevue/toast";
import InputText from "primevue/inputtext";
import Checkbox from "primevue/checkbox";
import Dialog from "primevue/dialog";
import ConfirmDialog from "primevue/confirmdialog";
import Menu from "primevue/menu";
import Avatar from "primevue/avatar";
import Tag from "primevue/tag";
import Drawer from "primevue/drawer";

registerIcons();

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            prefix: "p",
            darkModeSelector: ".dark-mode",
            cssLayer: {
                name: "primevue",
                order: "reset, primevue, components",
            },
        },
    },
    zIndex: {
        modal: 1100,    // dialog, drawer
        overlay: 1000,  // select, autocomplete, etc.
        menu: 1000,     // overlay menus
        tooltip: 1200   // tooltip (above modals)
    }
});
app.use(ToastService);
app.use(ConfirmationService);

app.component("FontAwesomeIcon", FontAwesomeIcon);
app.component("Button", Button);
app.component("Toast", Toast);
app.component("InputText", InputText);
app.component("Checkbox", Checkbox);
app.component("Dialog", Dialog);
app.component("ConfirmDialog", ConfirmDialog);
app.component("Menu", Menu);
app.component("Avatar", Avatar);
app.component("Tag", Tag);
app.component("Drawer", Drawer);

app.mount("#app");

const authStore = useAuthStore();
authStore.initialize();

// Register Firebase Cloud Messaging Service Worker
if ("serviceWorker" in navigator) {
    navigator.serviceWorker
        .register("/firebase-messaging-sw.js")
        .then((registration) => {
            console.log(
                "Service Worker registered successfully:",
                registration.scope
            );
        })
        .catch((error) => {
            console.error("Service Worker registration failed:", error);
        });
}
