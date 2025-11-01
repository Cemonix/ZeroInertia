import type { Label } from "./label";

export interface Task {
    id: string;
    title: string;
    description: string | null;
    completed: boolean;
    order_index: number;
    archived: boolean;
    project_id: string;
    section_id: string;
    priority_id: string | null;
    due_datetime: string | null;
    created_at: string;
    updated_at: string;
    archived_at: string | null;
    labels?: Label[];
    label_ids?: string[];
}

export interface TaskCreateInput {
    title: string;
    description: string | null;
    project_id: string;
    section_id: string;
    priority_id?: string | null;
    due_datetime?: string | null;
    label_ids?: string[] | null;
}

export interface TaskReorderItem {
    id: string;
    section_id: string;
    order_index: number;
}