const API_BASE = "https://fireriskgroup02.com/api/v1";

// Generic fetch that includes Bearer token and parses JSON/text
export async function apiFetch(path, { method = "GET", token, body } = {}) {
  const headers = {};

  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers["Content-Type"] = "application/json";

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  let data;
  try {
    data = JSON.parse(text);
  } catch {
    data = text;
  }

  if (!res.ok) {
    const msg = typeof data === "string" ? data : JSON.stringify(data);
    throw new Error(`HTTP ${res.status}: ${msg}`);
  }

  return data;
}