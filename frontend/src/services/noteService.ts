import type { Note, NoteInput, NoteReorderItem, NoteUpdateInput } from "@/models/note";
import apiClient from "./apiClient";

const API_URL = "/api/v1/notes";

const serializeCreatePayload = (payload: NoteInput) => {
    const body: Record<string, unknown> = {
        title: payload.title,
        content: payload.content ?? "",
        parent_id: payload.parent_id,
    };
    if (payload.order_index !== undefined && payload.order_index !== null) {
        body.order_index = payload.order_index;
    }
    return body;
};

const serializeUpdatePayload = (payload: NoteUpdateInput) => {
    const body: Record<string, unknown> = {};
    if (payload.title !== undefined) {
        body.title = payload.title;
    }
    if (payload.content !== undefined) {
        body.content = payload.content;
    }
    if (payload.parent_id !== undefined) {
        body.parent_id = payload.parent_id;
    }
    if (payload.order_index !== undefined) {
        body.order_index = payload.order_index;
    }
    return body;
};

export const noteService = {
    async getNotes(): Promise<Note[]> {
        const response = await apiClient.get<Note[]>(API_URL);
        return response.data;
    },

    async getNoteById(noteId: string): Promise<Note> {
        const response = await apiClient.get<Note>(`${API_URL}/${noteId}`);
        return response.data;
    },

    async createNote(payload: NoteInput): Promise<Note> {
        const response = await apiClient.post<Note>(API_URL, serializeCreatePayload(payload));
        return response.data;
    },

    async updateNote(noteId: string, payload: NoteUpdateInput): Promise<Note> {
        const response = await apiClient.patch<Note>(
            `${API_URL}/${noteId}`,
            serializeUpdatePayload(payload),
        );
        return response.data;
    },

    async deleteNote(noteId: string): Promise<void> {
        await apiClient.delete(`${API_URL}/${noteId}`);
    },

    async reorderNotes(reorderedNotes: NoteReorderItem[]): Promise<void> {
        await apiClient.post(`${API_URL}/reorder`, reorderedNotes);
    },
};
