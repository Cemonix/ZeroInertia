import axios from "axios";
import { env } from "@/config/env";
import { handleApiError } from "../core/errorHandler";

const apiClient = axios.create({
    baseURL: env.API_BASE_URL,
    timeout: 10000,
    headers: { "Content-Type": "application/json" },
    withCredentials: true,
});

apiClient.interceptors.request.use(function (config) {
    return config;
}, function (error) {
    return Promise.reject(error);
});

apiClient.interceptors.response.use(
    res => res,
    err => handleApiError(err, 'API request failed')
);


export default apiClient;
