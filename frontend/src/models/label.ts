export interface Label {
    id: string;
    name: string;
    color: string;
    description: string | null;
    created_at: string;
    updated_at: string;
}

export interface LabelCreateInput {
    name: string;
    color: string;
    description?: string | null;
}

export interface LabelUpdateInput {
    name?: string;
    color?: string;
    description?: string | null;
}
