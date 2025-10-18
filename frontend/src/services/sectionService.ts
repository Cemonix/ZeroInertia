import type { Section, SectionReorderItem } from "@/models/section";
import apiClient from "./apiClient";


const API_URL = "/api/v1/sections";

export const sectionService = {
    async getSections(project_id: string | null): Promise<Section[]> {
        const response = await apiClient.get(API_URL, {
            ...(project_id && { params: { project_id } })
        });
        return response.data;
    },

    async getSectionById(sectionId: string): Promise<Section | null> {
        const response = await apiClient.get(`${API_URL}/${sectionId}`);
        return response.data;
    },

    async createSection(section: Section): Promise<Section> {
        const response = await apiClient.post(API_URL, section);
        return response.data;
    },

    async updateSection(sectionId: string, updates: Partial<Omit<Section, 'id' | 'created_at'>>): Promise<Section> {
        const response = await apiClient.patch(`${API_URL}/${sectionId}`, updates);
        return response.data;
    },

    async deleteSection(sectionId: string): Promise<void> {
        await apiClient.delete(`${API_URL}/${sectionId}`);
    },

    async reorderSections(reorderedSections: SectionReorderItem[]): Promise<void> {
        await apiClient.patch(`${API_URL}/reorder`, reorderedSections);
    }
}