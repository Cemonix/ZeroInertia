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

            <div
                v-if="form.media_type === 'manga'"
                class="form-field"
            >
                <label for="author">Author</label>
                <InputText
                    id="author"
                    v-model="form.author"
                    placeholder="Author name (optional)"
                />
            </div>

            <div class="details-section">
                <div class="form-row">
                <div class="form-field">
                    <label for="genres">Genres</label>
                    <MultiSelect
                        id="genres"
                        v-model="form.genres"
                        :options="genreOptions"
                        optionLabel="name"
                        optionValue="id"
                        placeholder="Select genres"
                        :filter="true"
                        display="chip"
                    />
                </div>
                <div
                    v-if="form.media_type === 'book'"
                    class="form-field checkbox-field"
                >
                    <label class="checkbox-label" for="is_audiobook">
                        <input
                            id="is_audiobook"
                            type="checkbox"
                            v-model="form.is_audiobook"
                        />
                        <span>Audiobook</span>
                    </label>
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
                    <div
                        v-else-if="form.media_type === 'anime'"
                        class="form-field"
                    >
                        <label for="episodes">Episodes</label>
                        <input
                            id="episodes"
                            v-model.number="form.episodes"
                            type="number"
                            min="1"
                            class="number-input"
                            placeholder="Episode count (optional)"
                        />
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-field">
                        <label for="started_at">Started</label>
                        <DatePicker
                            id="started_at"
                            v-model="startedDate"
                            placeholder="Start date"
                            dateFormat="yy-mm-dd"
                            :showIcon="true"
                            iconDisplay="input"
                            :yearNavigator="true"
                            :monthNavigator="true"
                            :yearRange="yearRange"
                            :showClear="true"
                        >
                            <template #dropdownicon>
                                <font-awesome-icon icon="calendar" />
                            </template>
                        </DatePicker>
                    </div>
                    <div class="form-field">
                        <label for="completed_at">Completed</label>
                        <DatePicker
                            id="completed_at"
                            v-model="completedDate"
                            placeholder="Completion date"
                            dateFormat="yy-mm-dd"
                            :showIcon="true"
                            iconDisplay="input"
                            :yearNavigator="true"
                            :monthNavigator="true"
                            :yearRange="yearRange"
                            :showClear="true"
                        >
                            <template #dropdownicon>
                                <font-awesome-icon icon="calendar" />
                            </template>
                        </DatePicker>
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
import MultiSelect from "primevue/multiselect";
import DatePicker from "primevue/datepicker";
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
    return activeCategory.value;
};

interface InternalFormState {
    media_type: MediaType;
    title: string;
    status: MediaStatus;
    creator: string;
    author: string | null;
    is_audiobook: boolean;
    genres: string[]; // genre IDs
    platform: string | null;
    season_number: number | null;
    episodes: number | null;
    started_at: string | null;
    completed_at: string | null;
    notes: string | null;
}

const form = reactive<InternalFormState>({
    media_type: getDefaultMediaType(),
    title: "",
    status: "planned",
    creator: "",
    author: null,
    is_audiobook: false,
    genres: [],
    platform: null,
    season_number: null,
    episodes: null,
    started_at: null,
    completed_at: null,
    notes: null,
});

const duplicateMatches = ref<DuplicateMatch[]>([]);
const platformSuggestions = ref<string[]>([]);

const startedDate = ref<Date | null>(null);
const completedDate = ref<Date | null>(null);

const yearRange = computed(() => {
    const currentYear = new Date().getFullYear();
    const minYear = 1900;
    const maxYear = currentYear + 10;
    return `${minYear}:${maxYear}`;
});

const genreOptions = computed(() =>
    availableGenres.value.map((genre) => ({
        name: genre.name,
        id: genre.id,
    })),
);

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

const dateToString = (date: Date | null): string | null => {
    if (!date) return null;
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
};

const stringToDate = (dateStr: string | null): Date | null => {
    if (!dateStr) return null;
    const normalized = normalizeDate(dateStr);
    if (!normalized) return null;
    return new Date(normalized + 'T00:00:00');
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
        form.author = null;
        form.is_audiobook = false;
        form.genres = [];
        form.platform = null;
        form.season_number = null;
        form.episodes = null;
        form.started_at = null;
        form.completed_at = null;
        form.notes = null;
        startedDate.value = null;
        completedDate.value = null;
        duplicateMatches.value = [];
        return;
    }

    form.media_type = item.media_type;
    form.title = item.title;
    form.status = item.status;
    form.is_audiobook = "is_audiobook" in item ? item.is_audiobook : false;
    form.genres = item.genres.map((genre) => genre.id);
    form.started_at = normalizeDate(item.started_at);
    form.completed_at = normalizeDate(item.completed_at);
    form.notes = item.notes ?? null;

    startedDate.value = stringToDate(item.started_at);
    completedDate.value = stringToDate(item.completed_at);

    if (item.media_type === "book") {
        form.creator = item.creator;
        form.author = null;
        form.platform = null;
        form.season_number = null;
        form.episodes = null;
    } else if (item.media_type === "game") {
        form.creator = "";
        form.author = null;
        form.platform = item.platform ?? null;
        form.season_number = null;
        form.episodes = null;
    } else if (item.media_type === "show") {
        form.creator = "";
        form.author = null;
        form.platform = null;
        form.season_number = item.season_number ?? null;
        form.episodes = null;
    } else if (item.media_type === "anime") {
        form.creator = "";
        form.author = null;
        form.platform = null;
        form.season_number = null;
        form.episodes = item.episodes ?? null;
    } else if (item.media_type === "manga") {
        form.creator = "";
        form.author = item.author ?? null;
        form.platform = null;
        form.season_number = null;
        form.episodes = null;
    } else {
        form.creator = "";
        form.author = null;
        form.platform = null;
        form.season_number = null;
        form.episodes = null;
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

watch(startedDate, (date) => {
    form.started_at = dateToString(date);
});

watch(completedDate, (date) => {
    form.completed_at = dateToString(date);
});

let duplicateTimeout: ReturnType<typeof setTimeout> | null = null;

const scheduleDuplicateCheck = () => {
    duplicateMatches.value = [];
    if (duplicateTimeout) {
        clearTimeout(duplicateTimeout);
        duplicateTimeout = null;
    }

    const trimmed = form.title.trim();
    if (trimmed.length < 3) {
        return;
    }

    duplicateTimeout = setTimeout(async () => {
        try {
            const results = await mediaService.checkDuplicateTitle(trimmed, form.media_type);
            if (props.item) {
                duplicateMatches.value = results.filter(
                    (match) =>
                        !(
                            match.media_type === props.item!.media_type &&
                            match.title === props.item!.title
                        ),
                );
            } else {
                duplicateMatches.value = results;
            }
        } catch {
            duplicateMatches.value = [];
        }
    }, 400);
};

watch(
    () => form.title,
    () => {
        scheduleDuplicateCheck();
    },
);

watch(
    () => form.media_type,
    () => {
        scheduleDuplicateCheck();
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
        case "manga":
            return "Manga";
        case "anime":
            return "Anime";
    }
    return "";
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
    const genreIds = [...form.genres];

    switch (form.media_type) {
        case "book":
            formValues = {
                media_type: "book",
                title: form.title,
                status: form.status,
                creator: form.creator,
                is_audiobook: form.is_audiobook,
                genre_ids: genreIds,
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
                genre_ids: genreIds,
                platform: normalizeOptionalString(form.platform),
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
                genre_ids: genreIds,
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
                genre_ids: genreIds,
                started_at: normalizeDate(form.started_at),
                completed_at: normalizeDate(form.completed_at),
                notes: normalizeOptionalString(form.notes),
            };
            break;
        case "anime":
            formValues = {
                media_type: "anime",
                title: form.title,
                status: form.status,
                episodes: form.episodes,
                genre_ids: genreIds,
                started_at: normalizeDate(form.started_at),
                completed_at: normalizeDate(form.completed_at),
                notes: normalizeOptionalString(form.notes),
            };
            break;
        case "manga":
            formValues = {
                media_type: "manga",
                title: form.title,
                status: form.status,
                author: normalizeOptionalString(form.author),
                genre_ids: genreIds,
                started_at: normalizeDate(form.started_at),
                completed_at: normalizeDate(form.completed_at),
                notes: normalizeOptionalString(form.notes),
            };
            break;
        default:
            return;
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

.checkbox-field {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding-top: 1.25rem;
}

.checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-weight: 500;
}

.checkbox-label input {
    width: 1.2rem;
    height: 1.2rem;
    accent-color: var(--p-primary-color, #6366f1);
    cursor: pointer;
}

.details-section {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 0.5rem;
}

.form-field :deep(.p-datepicker) {
    width: 100%;
}

.form-field :deep(.p-datepicker-input) {
    width: 100%;
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
