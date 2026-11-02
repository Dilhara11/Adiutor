"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import ChatMessage, { type Message } from "./components/ChatMessage";
import Composer, { type ComposerHandle } from "./components/Composer";
import Sidebar from "./components/Sidebar";
import Welcome, { type QuickAction } from "./components/Welcome";
import { MenuIcon, PlusIcon } from "./components/icons";
import { getSummary, streamChat, type ChatTurn, type WorkforceSummary } from "./lib/api";

let idCounter = 0;
const nextId = () => `m${++idCounter}`;

/** Earlier finished messages, sent with each request so follow-ups ("yes, do it") work. */
function toHistory(messages: Message[]): ChatTurn[] {
  return messages
    .filter((m) => m.text.trim() && (m.role === "user" || m.status === "done"))
    .map((m) => ({ role: m.role, text: m.text }));
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [isBusy, setIsBusy] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [summary, setSummary] = useState<WorkforceSummary | null>(null);
  const [summaryError, setSummaryError] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const abortRef = useRef<AbortController | null>(null);
  const composerRef = useRef<ComposerHandle>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const stickToBottom = useRef(true);

  const refreshSummary = useCallback(async () => {
    setIsRefreshing(true);
    try {
      setSummary(await getSummary());
      setSummaryError(null);
    } catch {
      setSummaryError("Can't load the overview. Is the Adiutor server running on port 5000?");
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    // Load the dashboard numbers once when the page opens.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refreshSummary();
  }, [refreshSummary]);

  // Keep the newest message in view, unless the user scrolled up to read.
  useEffect(() => {
    const el = scrollRef.current;
    if (el && messages.length > 0 && stickToBottom.current) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const updateMessage = (id: string, change: (m: Message) => Message) =>
    setMessages((prev) => prev.map((m) => (m.id === id ? change(m) : m)));

  const send = useCallback(
    async (rawPrompt: string, previous: Message[]) => {
      const prompt = rawPrompt.trim();
      if (!prompt || abortRef.current) return;

      const userMessage: Message = { id: nextId(), role: "user", text: prompt, tools: [], status: "done" };
      const reply: Message = { id: nextId(), role: "assistant", text: "", tools: [], status: "streaming" };
      setMessages([...previous, userMessage, reply]);
      setDraft("");
      setIsBusy(true);
      stickToBottom.current = true;

      const controller = new AbortController();
      abortRef.current = controller;
      let changedData = false;

      try {
        await streamChat(
          prompt,
          toHistory(previous),
          (event) => {
            if (event.type === "text") {
              updateMessage(reply.id, (m) => ({ ...m, text: m.text + event.delta }));
            } else if (event.type === "tool") {
              updateMessage(reply.id, (m) => ({ ...m, tools: [...m.tools, event.label] }));
            } else if (event.type === "data_changed") {
              changedData = true;
            }
          },
          controller.signal
        );
        updateMessage(reply.id, (m) => ({ ...m, status: "done" }));
      } catch (error) {
        if (controller.signal.aborted) {
          updateMessage(reply.id, (m) => ({ ...m, status: "stopped" }));
        } else {
          const text = error instanceof Error ? error.message : "Something went wrong.";
          updateMessage(reply.id, (m) => ({ ...m, status: "error", error: text }));
        }
      } finally {
        abortRef.current = null;
        setIsBusy(false);
        if (changedData) void refreshSummary();
        composerRef.current?.focus();
      }
    },
    [refreshSummary]
  );

  const sendDraft = () => void send(draft, messages);

  const ask = (prompt: string) => {
    setSidebarOpen(false);
    void send(prompt, messages);
  };

  const retry = (assistantId: string) => {
    const index = messages.findIndex((m) => m.id === assistantId);
    const userMessage = messages[index - 1];
    if (userMessage?.role === "user") void send(userMessage.text, messages.slice(0, index - 1));
  };

  const handleQuickAction = (action: QuickAction) => {
    if (action.mode === "send") {
      ask(action.prompt);
    } else {
      setDraft(action.prompt);
      requestAnimationFrame(() => composerRef.current?.focus());
    }
  };

  const newChat = () => {
    abortRef.current?.abort();
    setMessages([]);
    setDraft("");
    setSidebarOpen(false);
  };

  const hasMessages = messages.length > 0;

  return (
    <div className="flex h-dvh w-full overflow-hidden">
      <Sidebar
        summary={summary}
        summaryError={summaryError}
        isRefreshing={isRefreshing}
        onRefresh={() => void refreshSummary()}
        onNewChat={newChat}
        onAsk={ask}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white/80 px-4 py-3 backdrop-blur lg:px-6">
          <div className="flex items-center gap-2">
            <button
              className="rounded-lg p-1.5 text-slate-600 hover:bg-slate-100 lg:hidden"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open sidebar"
            >
              <MenuIcon />
            </button>
            <h2 className="text-sm font-semibold text-slate-800">
              {hasMessages ? "Conversation" : "Home"}
            </h2>
          </div>
          {hasMessages ? (
            <button
              onClick={newChat}
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50"
            >
              <PlusIcon /> New
            </button>
          ) : null}
        </header>

        <div
          ref={scrollRef}
          className="flex-1 overflow-y-auto"
          onScroll={(event) => {
            const el = event.currentTarget;
            stickToBottom.current = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
          }}
        >
          {hasMessages ? (
            <div className="mx-auto flex w-full max-w-3xl flex-col gap-5 px-4 py-6">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  onRetry={message.status === "error" ? () => retry(message.id) : undefined}
                />
              ))}
            </div>
          ) : (
            <Welcome onAction={handleQuickAction} />
          )}
        </div>

        <Composer
          ref={composerRef}
          value={draft}
          onChange={setDraft}
          onSend={sendDraft}
          onStop={() => abortRef.current?.abort()}
          isBusy={isBusy}
        />
      </div>
    </div>
  );
}
