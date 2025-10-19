export interface Task {
    id: string;
    title: string;
    description: string | null;
    completed: boolean;
    project_id: string;
    section_id: string;
    created_at: string;
    updated_at: string;
}
