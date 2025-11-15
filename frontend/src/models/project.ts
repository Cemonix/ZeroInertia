export interface Project {
    id: string;
    parent_id: string | null;
    title: string;
    order_index: number;
    is_inbox: boolean;
    created_at: string;
    updated_at: string;
}

export interface ProjectReorderItem {
    id: string;
    parent_id: string | null;
    order_index: number;
}
