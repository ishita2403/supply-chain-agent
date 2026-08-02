import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export async function fetchEvents() {
  const response = await api.get("/events");
  return response.data;
}

export async function runAgent(eventId, weights) {
  const response = await api.post(
    `/events/${eventId}/run`,
    weights
  );
  return response.data;
}