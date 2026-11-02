export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:5000";

export type ChatTurn = { role: "user" | "assistant"; text: string };

export type ChatEvent =
  | { type: "text"; delta: string }
  | { type: "tool"; name: string; label: string }
  | { type: "data_changed" }
  | { type: "error"; message: string }
  | { type: "done" };

export type Employee = {
  employee_id: number;
  first_name: string | null;
  last_name: string | null;
  email: string | null;
  hire_date: string | null;
  salary: number | null;
  job_id: string | null;
  job_title: string | null;
  department_id: number | null;
  department_name: string | null;
};

export type Department = {
  department_id: number;
  department_name: string;
  headcount: number;
  average_salary: number | null;
};

export type WorkforceSummary = {
  total_employees: number;
  average_salary: number | null;
  total_payroll: number | null;
  department_count: number;
  departments: Department[];
  recent_hires: Employee[];
};

async function readError(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (body && typeof body.detail === "string") return body.detail;
  } catch {
    /* not JSON */
  }
  return `Request failed (${response.status})`;
}

export async function getSummary(signal?: AbortSignal): Promise<WorkforceSummary> {
  const response = await fetch(`${API_BASE_URL}/summary`, { signal, cache: "no-store" });
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

/**
 * Sends a message and calls `onEvent` for every piece of the answer as it
 * arrives (text, tool activity, data changes). The server sends one JSON
 * object per line.
 */
export async function streamChat(
  prompt: string,
  history: ChatTurn[],
  onEvent: (event: ChatEvent) => void,
  signal?: AbortSignal
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, history }),
      signal,
    });
  } catch (error) {
    if (signal?.aborted) throw error;
    throw new Error(
      "Can't reach the Adiutor server. Make sure it is running and try again."
    );
  }

  if (!response.ok || !response.body) {
    throw new Error(await readError(response));
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let newline = buffer.indexOf("\n");
    while (newline !== -1) {
      const line = buffer.slice(0, newline).trim();
      buffer = buffer.slice(newline + 1);
      if (line) {
        const event = JSON.parse(line) as ChatEvent;
        if (event.type === "error") throw new Error(event.message);
        onEvent(event);
      }
      newline = buffer.indexOf("\n");
    }
  }
}

const currency = new Intl.NumberFormat(undefined, {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

export function formatMoney(value: number | null | undefined): string {
  return value == null ? "—" : currency.format(value);
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}
