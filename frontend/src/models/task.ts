import type { Label } from "./label";

export type TaskRecurrenceType = "daily" | "alternate_days" | "weekly";

export interface TaskRecurrence {
    type: TaskRecurrenceType;
    time: string; // HH:mm in 24h format
    // IMPORTANT: days_of_week uses JavaScript's convention (0=Sunday, 1=Monday, ..., 6=Saturday)
    // for UI display. Must be converted to Python's convention (0=Monday, ..., 6=Sunday)
    // before sending to backend using jsDaysToPythonDays() from recurrenceUtils.
    days_of_week?: number[]; // Required when type === "weekly"
}

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
    recurrence?: TaskRecurrence | null;
    recurring_task_id?: string | null;
}

export interface TaskCreateInput {
    title: string;
    description: string | null;
    project_id: string;
    section_id: string;
    priority_id?: string | null;
    due_datetime?: string | null;
    label_ids?: string[] | null;
    recurrence?: TaskRecurrence | null;
}

export interface TaskReorderItem {
    id: string;
    section_id: string;
    order_index: number;
}
