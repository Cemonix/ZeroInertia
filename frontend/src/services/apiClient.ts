import axios from "axios";
import { env } from "@/config/env";
import { handleApiError } from "./errorHandler";

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
    function onFulfilled(response) {
        return response;
    },
    function onRejected(error) {
        return handleApiError(error, 'API request failed');
    }
);


export default apiClient;
