import type { TaskRecurrenceType } from "./task";

export interface RecurringTask {
    id: string;
    title: string;
    description: string | null;
    project_id: string;
    section_id: string;
    priority_id: string | null;
    label_ids: string[] | null;
    recurrence_type: TaskRecurrenceType;
    recurrence_days: number[] | null;
    recurrence_time: string;
    start_date: string;
    end_date: string | null;
    last_generated_date: string | null;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface RecurringTaskCreateInput {
    title: string;
    description?: string | null;
    project_id: string;
    section_id: string;
    priority_id?: string | null;
    label_ids?: string[] | null;
    recurrence_type: TaskRecurrenceType;
    recurrence_days?: number[] | null;
    recurrence_time: string;
    start_date: string;
    end_date?: string | null;
    is_active?: boolean;
}

export interface RecurringTaskUpdateInput {
    title?: string;
    description?: string | null;
    priority_id?: string | null;
    label_ids?: string[] | null;
    recurrence_type?: TaskRecurrenceType;
    recurrence_days?: number[] | null;
    recurrence_time?: string;
    start_date?: string;
    end_date?: string | null;
    is_active?: boolean;
}
