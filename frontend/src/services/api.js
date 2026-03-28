import axios from "axios";

const api = axios.create({
    baseURL: "/",
    timeout: 10000,
});

export async function fetchAirQuality() {
    const response = await api.get("/api/air-quality");
    return response.data;
}

export async function fetchPredictions() {
    const response = await api.get("/api/predictions");
    return response.data;
}

export async function fetchAlerts() {
    const response = await api.get("/api/alerts");
    return response.data;
}
