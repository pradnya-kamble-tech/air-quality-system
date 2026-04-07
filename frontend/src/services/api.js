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

export async function fetchHistory(city, pollutant, hours = 72) {
    const params = {};
    if (city) params.city = city;
    if (pollutant) params.pollutant = pollutant;
    if (hours) params.hours = hours;
    const response = await api.get("/api/history", { params });
    return response.data;
}
