// frontend/src/api/client.js

import axios from "axios";

const API_BASE = "http://localhost:8000";

export async function fetchEvents() {
  const res = await axios.get(`${API_BASE}/events`);
  return res.data;
}

export async function runAgent(eventId, weights) {
  const res = await axios.post(`${API_BASE}/events/${eventId}/run`, weights);
  return res.data;
}