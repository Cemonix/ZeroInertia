export interface Section {
    id: string;
    title: string;
    project_id: string;
    order_index: number;
    created_at: string;
    updated_at: string;
}

export interface SectionReorderItem {
    id: string;
    project_id: string;
    order_index: number;
}
