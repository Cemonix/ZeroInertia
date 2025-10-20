export interface Task {
    id: string;
    title: string;
    description: string | null;
    completed: boolean;
    order_index: number;
    archived: boolean;
    project_id: string;
    section_id: string;
    created_at: string;
    updated_at: string;
    archived_at: string | null;
}
