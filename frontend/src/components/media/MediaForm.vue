<template>
    <Dialog
        :visible="visible"
        @update:visible="visible = $event"
        modal
        :header="item ? 'Edit Media' : 'Add Media'"
        :style="{ width: '520px' }"
    >
        <div class="media-form">
            <div class="form-row">
                <div class="form-field">
                    <label for="media-type">Media Type</label>
                    <Select
                        id="media-type"
                        v-model="form.media_type"
                        :options="MEDIA_TYPES"
                        optionLabel="label"
                        optionValue="value"
                    />
                </div>
                <div class="form-field">
                    <label for="status">Status</label>
                    <Select
                        id="status"
                        v-model="form.status"
                        :options="MEDIA_STATUSES"
                        optionLabel="label"
                        optionValue="value"
                    />
                </div>
            </div>

            <div class="form-field">
                <label for="title">Title</label>
                <InputText
                    id="title"
                    v-model="form.title"
                    placeholder="Title"
                    autofocus
                />
            </div>

            <div
                v-if="form.media_type === 'book'"
                class="form-field"
            >
                <label for="creator">Author <span class="required">*</span></label>
                <InputText
                    id="creator"
                    v-model="form.creator"
                    placeholder="Author name"
                    required
                />
            </div>

            <div class="details-section">
                <div class="form-row">
                    <div class="form-field">
                        <label for="genre">Genre</label>
                        <AutoComplete
                            id="genre"
                            v-model="form.genre"
                            :suggestions="genreSuggestions"
                            @complete="searchGenre"
                            placeholder="Genre (optional)"
                            dropdown
                            :completeOnFocus="true"
                        />
                    </div>
                    <div
                        v-if="form.media_type === 'game'"
                        class="form-field"
                    >
                        <label for="platform">Platform</label>
                        <AutoComplete
                            id="platform"
                            v-model="form.platform"
                            :suggestions="platformSuggestions"
                            @complete="searchPlatform"
                            placeholder="Platform (optional)"
                            dropdown
                            :completeOnFocus="true"
                        />
                    </div>
                    <div
                        v-else-if="form.media_type === 'show'"
                        class="form-field"
                    >
                        <label for="season">Season</label>
                        <input
                            id="season"
                            v-model.number="form.season_number"
                            type="number"
                            min="1"
                            class="number-input"
                            placeholder="Season #"
                        />
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-field">
                        <label for="started_at">Started</label>
                        <input
                            id="started_at"
                            v-model="form.started_at"
                            type="date"
                            class="date-input"
                        />
                    </div>
                    <div class="form-field">
                        <label for="completed_at">Completed</label>
                        <input
                            id="completed_at"
                            v-model="form.completed_at"
                            type="date"
                            class="date-input"
                        />
                    </div>
                </div>

                <div class="form-field">
                    <label for="notes">Notes</label>
                    <Textarea
                        id="notes"
                        v-model="form.notes"
                        rows="3"
                        placeholder="Notes (optional)"
                    />
                </div>
            </div>

            <div v-if="duplicateMatches.length > 0" class="duplicate-warning">
                <span class="duplicate-title">
                    Possible duplicates found for this title:
                </span>
                <ul class="duplicate-list">
                    <li
                        v-for="match in duplicateMatches"
                        :key="match.media_type + match.title + (match.completed_at || '')"
                    >
                        <strong>{{ formatMediaType(match.media_type) }}</strong> —
                        {{ match.title }}
                        <span v-if="match.status === 'completed' && match.completed_at">
                            (completed {{ match.completed_at }})
                        </span>
                    </li>
                </ul>
            </div>

            <div class="actions">
                <Button
                    label="Cancel"
                    text
                    @click="visible = false"
                />
                <Button
                    label="Save"
                    :disabled="!canSave"
                    @click="handleSave"
                />
            </div>
        </div>
    </Dialog>
</template>

<script setup lang="ts">
import { computed, onUnmounted, reactive, watch, ref } from "vue";
import Dialog from "primevue/dialog";
import Select from "primevue/select";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import Button from "primevue/button";
import AutoComplete from "primevue/autocomplete";
import {
    MEDIA_STATUSES,
    MEDIA_TYPES,
    type DuplicateMatch,
    type MediaFormValues,
    type MediaItem,
    type MediaStatus,
    type MediaType,
} from "@/models/media";
import { useMediaStore } from "@/stores/media";
import { mediaService } from "@/services/mediaService";
import { storeToRefs } from "pinia";

interface Props {
    item: MediaItem | null;
}

interface Emits {
    (e: "saved"): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const visible = defineModel<boolean>("visible", {
    required: true,
});

const mediaStore = useMediaStore();
const { availableGenres, availablePlatforms, activeCategory } =
    storeToRefs(mediaStore);

const getDefaultMediaType = (): MediaType => {
    const category = activeCategory.value;
    return category === "all" ? "book" : category;
};

interface InternalFormState {
    media_type: MediaType;
    title: string;
    status: MediaStatus;
    creator: string;
    genre: string | null;
    platform: string | null;
    season_number: number | null;
    started_at: string | null;
    completed_at: string | null;
    notes: string | null;
}

const form = reactive<InternalFormState>({
    media_type: getDefaultMediaType(),
    title: "",
    status: "planned",
    creator: "",
    genre: null,
    platform: null,
    season_number: null,
    started_at: null,
    completed_at: null,
    notes: null,
});

const duplicateMatches = ref<DuplicateMatch[]>([]);
const genreSuggestions = ref<string[]>([]);
const platformSuggestions = ref<string[]>([]);

const canSave = computed(() => {
    if (!form.title.trim()) {
        return false;
    }
    if (form.media_type === "book" && !form.creator.trim()) {
        return false;
    }
    return true;
});

const normalizeDate = (value: string | null): string | null => {
    if (!value || value.trim() === "") return null;
    if (value.length >= 10) {
        return value.slice(0, 10);
    }
    return value;
};

const normalizeOptionalString = (value: string | null): string | null => {
    if (value === null || value === undefined || value.trim() === "") {
        return null;
    }
    return value;
};

const populateFormFromItem = (item: MediaItem | null) => {
    if (!item) {
        const defaultType = getDefaultMediaType();
        form.media_type = defaultType;
        form.title = "";
        form.status = "planned";
        form.creator = "";
        form.genre = null;
        form.platform = null;
        form.season_number = null;
        form.started_at = null;
        form.completed_at = null;
        form.notes = null;
        duplicateMatches.value = [];
        return;
    }

    form.media_type = item.media_type;
    form.title = item.title;
    form.status = item.status;
    form.genre = item.genre ?? null;
    form.started_at = normalizeDate(item.started_at);
    form.completed_at = normalizeDate(item.completed_at);
    form.notes = item.notes ?? null;

    if (item.media_type === "book") {
        form.creator = item.creator;
        form.platform = null;
        form.season_number = null;
    } else if (item.media_type === "game") {
        form.creator = "";
        form.platform = item.platform ?? null;
        form.season_number = null;
    } else if (item.media_type === "show") {
        form.creator = "";
        form.platform = null;
        form.season_number = item.season_number ?? null;
    } else {
        form.creator = "";
        form.platform = null;
        form.season_number = null;
    }

    duplicateMatches.value = [];
};

watch(
    () => props.item,
    (item) => {
        populateFormFromItem(item);
    },
    { immediate: true },
);

watch(
    () => visible.value,
    (isVisible) => {
        if (isVisible && !props.item) {
            populateFormFromItem(null);
        }
    },
);

watch(
    () => activeCategory.value,
    () => {
        if (!props.item) {
            form.media_type = getDefaultMediaType();
        }
    },
);

let duplicateTimeout: ReturnType<typeof setTimeout> | null = null;

watch(
    () => form.title,
    (title) => {
        duplicateMatches.value = [];
        if (duplicateTimeout) {
            clearTimeout(duplicateTimeout);
            duplicateTimeout = null;
        }

        const trimmed = title.trim();
        if (trimmed.length < 3) {
            return;
        }

        duplicateTimeout = setTimeout(async () => {
            try {
                const results = await mediaService.checkDuplicateTitle(trimmed);
                // When editing, filter out the current item from duplicates
                if (props.item) {
                    duplicateMatches.value = results.filter(
                        match => !(match.media_type === props.item!.media_type && match.title === props.item!.title)
                    );
                } else {
                    duplicateMatches.value = results;
                }
            } catch {
                duplicateMatches.value = [];
            }
        }, 400);
    },
);

onUnmounted(() => {
    if (duplicateTimeout) {
        clearTimeout(duplicateTimeout);
    }
});

const formatMediaType = (type: MediaType): string => {
    switch (type) {
        case "book":
            return "Book";
        case "game":
            return "Game";
        case "movie":
            return "Movie";
        case "show":
            return "Show";
    }
};

const searchGenre = (event: { query: string }) => {
    const query = event.query.toLowerCase();
    const allGenres = availableGenres.value;

    if (!query) {
        genreSuggestions.value = allGenres;
    } else {
        genreSuggestions.value = allGenres.filter((genre: string) =>
            genre.toLowerCase().includes(query)
        );
    }

    if (event.query && !genreSuggestions.value.includes(event.query)) {
        genreSuggestions.value.unshift(event.query);
    }
};

const searchPlatform = (event: { query: string }) => {
    const query = event.query.toLowerCase();
    const allPlatforms = availablePlatforms.value;

    if (!query) {
        platformSuggestions.value = allPlatforms;
    } else {
        platformSuggestions.value = allPlatforms.filter((platform: string) =>
            platform.toLowerCase().includes(query)
        );
    }

    if (event.query && !platformSuggestions.value.includes(event.query)) {
        platformSuggestions.value.unshift(event.query);
    }
};

const handleSave = async () => {
    let formValues: MediaFormValues;

    switch (form.media_type) {
        case "book":
            formValues = {
                media_type: "book",
                title: form.title,
                status: form.status,
                creator: form.creator,
                genre: normalizeOptionalString(form.genre),
                started_at: normalizeDate(form.started_at),
                completed_at: normalizeDate(form.completed_at),
                notes: normalizeOptionalString(form.notes),
            };
            break;
        case "game":
            formValues = {
                media_type: "game",
                title: form.title,
                status: form.status,
                platform: normalizeOptionalString(form.platform),
                genre: normalizeOptionalString(form.genre),
                started_at: normalizeDate(form.started_at),
                completed_at: normalizeDate(form.completed_at),
                notes: normalizeOptionalString(form.notes),
            };
            break;
        case "movie":
            formValues = {
                media_type: "movie",
                title: form.title,
                status: form.status,
                genre: normalizeOptionalString(form.genre),
                started_at: normalizeDate(form.started_at),
                completed_at: normalizeDate(form.completed_at),
                notes: normalizeOptionalString(form.notes),
            };
            break;
        case "show":
            formValues = {
                media_type: "show",
                title: form.title,
                status: form.status,
                season_number: form.season_number,
                genre: normalizeOptionalString(form.genre),
                started_at: normalizeDate(form.started_at),
                completed_at: normalizeDate(form.completed_at),
                notes: normalizeOptionalString(form.notes),
            };
            break;
    }

    await mediaStore.save(formValues);
    emit("saved");
};
</script>

<style scoped>
.media-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-row {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
}

.form-field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-field label {
    font-weight: 500;
    font-size: 0.9rem;
}

.form-field label .required {
    color: var(--p-red-500, #ef4444);
}

.details-section {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 0.5rem;
}

.date-input {
    width: 100%;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    border: 1px solid var(--p-content-border-color);
    background: var(--p-content-background);
    color: var(--p-text-color);
}

.duplicate-warning {
    border-radius: 6px;
    border: 1px solid var(--p-yellow-400, #facc15);
    background: rgba(250, 204, 21, 0.06);
    padding: 0.75rem 0.9rem;
    font-size: 0.85rem;
}

.duplicate-title {
    font-weight: 600;
    display: block;
    margin-bottom: 0.25rem;
}

.duplicate-list {
    margin: 0;
    padding-left: 1.1rem;
}

.number-input {
    width: 100%;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    border: 1px solid var(--p-content-border-color);
    background: var(--p-content-background);
    color: var(--p-text-color);
}

.actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

@media (max-width: 480px) {
    .form-row {
        grid-template-columns: 1fr;
    }
}
</style>
