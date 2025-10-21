export interface CheckListItem {
    id: string;
    checklist_id: string;
    text: string;
    completed: boolean;
    order_index: number;
    created_at: string;
    updated_at: string;
}

export interface CheckList {
    id: string;
    task_id: string;
    title: string;
    order_index: number;
    created_at: string;
    updated_at: string;
    items?: CheckListItem[];  // Optional, populated when fetching checklist details
}
