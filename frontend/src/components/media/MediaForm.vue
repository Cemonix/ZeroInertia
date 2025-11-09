<template>
    <Dialog
        v-model:visible="internalVisible"
        modal
        :header="dialogTitle"
        :style="{ width: '640px', maxWidth: '95vw' }"
        @hide="onHide"
    >
        <form class="media-form" @submit.prevent="onSubmit">
            <div class="form-row">
                <div class="field">
                    <label>Type</label>
                    <Select
                        v-model="form.media_type"
                        :options="MEDIA_TYPES"
                        optionLabel="label"
                        optionValue="value"
                        :disabled="isEditing"
                        placeholder="Select type"
                    />
                </div>
                <div class="field flex-1">
                    <label>Title</label>
                    <InputText
                        v-model.trim="form.title"
                        placeholder="Title"
                        required
                    />
                </div>
            </div>

            <div class="form-row">
                <div class="field">
                    <label>Status</label>
                    <Select
                        v-model="form.status"
                        :options="MEDIA_STATUSES"
                        optionLabel="label"
                        optionValue="value"
                    />
                </div>
                <div class="field rating-field">
                    <label>Rating</label>
                    <div class="rating-control">
                        <InputText
                            v-model="ratingText"
                            inputmode="numeric"
                            class="rating-inputtext"
                        />
                        <Slider
                            v-model="ratingValue"
                            :min="0"
                            :max="100"
                            :step="1"
                            class="rating-slider"
                        />
                    </div>
                </div>
                
            </div>

            <div class="form-row">
                <div class="field">
                    <label>Started</label>
                    <DatePicker
                        v-model="startedDate"
                        dateFormat="yy-mm-dd"
                        :showIcon="true"
                    />
                </div>
                <div class="field">
                    <label>Completed</label>
                    <DatePicker
                        v-model="completedDate"
                        dateFormat="yy-mm-dd"
                        :showIcon="true"
                    />
                </div>
            </div>

            <!-- Type-specific fields -->
            <div v-if="form.media_type === 'book'" class="type-grid">
                <div class="field">
                    <label>Author</label>
                    <InputText v-model.trim="ensureBook.author" />
                </div>
                <div class="field">
                    <label>Pages</label>
                    <InputNumber
                        v-model="ensureBook.pages"
                        :min="0"
                        :step="1"
                    />
                </div>
                <div class="field">
                    <label>ISBN</label>
                    <InputText v-model.trim="ensureBook.isbn" />
                </div>
                <div class="field">
                    <label>Publisher</label>
                    <InputText v-model.trim="ensureBook.publisher" />
                </div>
            </div>

            <div v-else-if="form.media_type === 'movie'" class="type-grid">
                <div class="field">
                    <label>Director</label>
                    <InputText v-model.trim="ensureMovie.director" />
                </div>
                <div class="field">
                    <label>Duration (min)</label>
                    <InputNumber
                        v-model="ensureMovie.duration_minutes"
                        :min="0"
                        :step="1"
                    />
                </div>
                <div class="field">
                    <label>Release Year</label>
                    <InputNumber
                        v-model="ensureMovie.release_year"
                        :min="1800"
                        :max="3000"
                        :step="1"
                    />
                </div>
                <div class="field">
                    <label>Genre</label>
                    <InputText v-model.trim="ensureMovie.genre" />
                </div>
            </div>

            <div v-else-if="form.media_type === 'game'" class="type-grid">
                <div class="field">
                    <label>Platform</label>
                    <InputText v-model.trim="ensureGame.platform" />
                </div>
                <div class="field">
                    <label>Developer</label>
                    <InputText v-model.trim="ensureGame.developer" />
                </div>
                <div class="field">
                    <label>Playtime (hours)</label>
                    <InputNumber
                        v-model="ensureGame.playtime_hours"
                        :min="0"
                        :step="1"
                    />
                </div>
                <div class="field">
                    <label>Genre</label>
                    <InputText v-model.trim="ensureGame.genre" />
                </div>
            </div>

            <div v-else-if="form.media_type === 'show'" class="type-grid">
                <div class="field">
                    <label>Season</label>
                    <InputNumber
                        v-model="ensureShow.season_number"
                        :min="1"
                        :step="1"
                    />
                </div>
                <div class="field">
                    <label>Episodes</label>
                    <InputNumber
                        v-model="ensureShow.episodes"
                        :min="0"
                        :step="1"
                    />
                </div>
                <div class="field">
                    <label>Creator</label>
                    <InputText v-model.trim="ensureShow.creator" />
                </div>
                <div class="field">
                    <label>Release Year</label>
                    <InputNumber
                        v-model="ensureShow.release_year"
                        :min="1800"
                        :max="3000"
                        :step="1"
                    />
                </div>
            </div>

            <!-- Notes at the bottom -->
            <div class="field">
                <label>Notes</label>
                <Textarea
                    v-model="form.notes"
                    rows="4"
                    autoResize
                    placeholder="Notes (optional)"
                />
            </div>

            <div class="form-actions">
                <Button type="button" text @click="cancel">Cancel</Button>
                <Button
                    type="submit"
                    :disabled="submitting || !form.title"
                    :loading="submitting"
                >
                    {{ isEditing ? "Update" : "Create" }}
                </Button>
            </div>
        </form>
    </Dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import Select from "primevue/select";
import InputText from "primevue/inputtext";
import Textarea from "primevue/textarea";
import InputNumber from "primevue/inputnumber";
import DatePicker from "primevue/datepicker";
import { useToast } from "primevue/usetoast";
import Slider from "primevue/slider";
import type {
    MediaCreateInput,
    MediaItem,
    MediaStatus,
    BookDetails,
    MovieDetails,
    GameDetails,
    ShowDetails,
} from "@/models/media";
import { MEDIA_STATUSES, MEDIA_TYPES } from "@/models/media";
import { useMediaStore } from "@/stores/media";

const props = defineProps<{
    visible: boolean;
    item?: MediaItem | null;
}>();

const emit = defineEmits<{
    (e: "update:visible", value: boolean): void;
    (e: "saved"): void;
}>();

const mediaStore = useMediaStore();
const toast = useToast();

const internalVisible = ref<boolean>(props.visible);
watch(
    () => props.visible,
    (v) => (internalVisible.value = v)
);
watch(internalVisible, (v) => emit("update:visible", v));

const isEditing = computed(() => !!props.item);
const dialogTitle = computed(() =>
    isEditing.value ? "Edit Media" : "Add Media"
);

type FormState = Required<
    Pick<MediaCreateInput, "media_type" | "title" | "status">
> & {
    rating: number | null;
    started_at: string | null;
    completed_at: string | null;
    notes: string | null;
    book?: BookDetails;
    movie?: MovieDetails;
    game?: GameDetails;
    show?: ShowDetails;
};

const defaultState = (): FormState => ({
    media_type: "book",
    title: "",
    status: "planned",
    rating: null,
    started_at: null,
    completed_at: null,
    notes: null,
});

const form = reactive<FormState>(defaultState());

const startedDate = ref<Date | null>(null);
const completedDate = ref<Date | null>(null);

const toDateString = (d: Date | null): string | null =>
    d
        ? new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))
              .toISOString()
              .slice(0, 10)
        : null;
const fromDateString = (s: string | null): Date | null =>
    s ? new Date(`${s}T00:00:00Z`) : null;

// Rating bindings: slider uses number; input uses string (allows blank=null)
const clampRating = (n: number) => Math.max(0, Math.min(100, Math.round(n)));
const ratingValue = computed<number>({
    get: () => form.rating ?? 0,
    set: (v: number) => {
        form.rating = clampRating(v);
    },
});
const ratingText = computed<string>({
    get: () => (form.rating == null ? "" : String(form.rating)),
    set: (val: string) => {
        const trimmed = val.trim();
        if (trimmed === "") {
            form.rating = null;
            return;
        }
        const n = Number(trimmed);
        if (Number.isNaN(n)) {
            form.rating = null;
        } else {
            form.rating = clampRating(n);
        }
    },
});

watch(
    () => props.item,
    (item) => {
        resetForm();
        if (item) {
            form.media_type = item.media_type;
            form.title = item.title;
            form.status = item.status as MediaStatus;
            form.rating = item.rating;
            form.notes = item.notes;
            form.started_at = item.started_at;
            form.completed_at = item.completed_at;
            startedDate.value = fromDateString(item.started_at);
            completedDate.value = fromDateString(item.completed_at);
            if (item.media_type === "book") {
                form.book = {
                    author: (item as any).author ?? "",
                    pages: (item as any).pages ?? null,
                    isbn: (item as any).isbn ?? null,
                    publisher: (item as any).publisher ?? null,
                };
            } else if (item.media_type === "movie") {
                form.movie = {
                    director: (item as any).director ?? null,
                    duration_minutes: (item as any).duration_minutes ?? null,
                    release_year: (item as any).release_year ?? null,
                    genre: (item as any).genre ?? null,
                };
            } else if (item.media_type === "game") {
                form.game = {
                    platform: (item as any).platform ?? null,
                    developer: (item as any).developer ?? null,
                    playtime_hours: (item as any).playtime_hours ?? null,
                    genre: (item as any).genre ?? null,
                    is_100_percent: (item as any).is_100_percent ?? null,
                };
            } else if (item.media_type === "show") {
                form.show = {
                    season_number: (item as any).season_number ?? null,
                    episodes: (item as any).episodes ?? null,
                    creator: (item as any).creator ?? null,
                    release_year: (item as any).release_year ?? null,
                    genre: (item as any).genre ?? null,
                };
            }
        }
    },
    { immediate: true }
);

watch([startedDate, completedDate], () => {
    form.started_at = toDateString(startedDate.value);
    form.completed_at = toDateString(completedDate.value);
});

const ensureBook = computed(() => {
    if (!form.book)
        form.book = { author: "", pages: null, isbn: null, publisher: null };
    return form.book;
});
const ensureMovie = computed(() => {
    if (!form.movie)
        form.movie = {
            director: null,
            duration_minutes: null,
            release_year: null,
            genre: null,
        };
    return form.movie;
});
const ensureGame = computed(() => {
    if (!form.game)
        form.game = {
            platform: null,
            developer: null,
            playtime_hours: null,
            genre: null,
            is_100_percent: null,
        };
    return form.game;
});
const ensureShow = computed(() => {
    if (!form.show)
        form.show = {
            season_number: null,
            episodes: null,
            creator: null,
            release_year: null,
            genre: null,
        };
    return form.show;
});

const submitting = ref(false);

async function onSubmit() {
    submitting.value = true;
    try {
        if (isEditing.value && props.item) {
            await mediaStore.update(props.item.id, props.item.media_type, form);
            toast.add({ severity: "success", summary: "Updated", life: 1800 });
        } else {
            await mediaStore.create(form);
            toast.add({ severity: "success", summary: "Created", life: 1800 });
        }
        emit("saved");
        close();
    } catch (e) {
        toast.add({
            severity: "error",
            summary: "Failed to save",
            detail: e instanceof Error ? e.message : "Unknown error",
            life: 3500,
        });
    } finally {
        submitting.value = false;
    }
}

function cancel() {
    close();
}

function close() {
    internalVisible.value = false;
}

function onHide() {
    // reset after closing
    resetForm();
}

function resetForm() {
    Object.assign(form, defaultState());
    startedDate.value = null;
    completedDate.value = null;
}
</script>

<style scoped>
.media-form {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}
.form-row {
    display: flex;
    gap: 0.75rem;
    align-items: flex-end;
}
.field {
    display: flex;
    flex-direction: column;
    gap: 0.375rem;
    min-width: 160px;
}
.field > label {
    font-size: 0.85rem;
    color: var(--p-text-muted-color);
}
.flex-1 {
    flex: 1;
}

.type-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.75rem;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

.rating-field {
    flex: 1;
}

.rating-control {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.rating-inputtext {
    width: 4rem;
    text-align: center;
}

.rating-slider {
    margin: 0 0.5rem;
    flex: 1;
}
</style>
