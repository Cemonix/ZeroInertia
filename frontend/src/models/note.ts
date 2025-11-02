export interface Note {
    id: string;
    title: string;
    parent_id: string | null;
    content: string;
    order_index: number;
    created_at: string;
    updated_at: string;
}

export interface NoteTreeSelection {
    [key: string]: boolean;
}

export interface NoteInput {
    title: string;
    parent_id: string | null;
    content?: string;
    order_index?: number | null;
}

export interface NoteUpdateInput {
    title?: string;
    parent_id?: string | null;
    content?: string;
    order_index?: number;
}

export interface NoteReorderItem {
    id: string;
    parent_id: string | null;
    order_index: number;
}
