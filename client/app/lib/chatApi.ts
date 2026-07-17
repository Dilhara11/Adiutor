const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:5000";

type ChatResponse = {
  text: string;
};

export async function sendChatPrompt(prompt: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt }),
  });

  let payload: ChatResponse | { detail?: string } | null = null;
  try {
    payload = (await response.json()) as ChatResponse | { detail?: string };
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const detail = payload && "detail" in payload ? payload.detail : "";
    throw new Error(detail || `Request failed with ${response.status}`);
  }

  if (!payload || !("text" in payload)) {
    return "";
  }

  return payload.text || "";
}
