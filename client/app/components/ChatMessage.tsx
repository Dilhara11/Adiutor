"use client";

import { memo, useState } from "react";
import Markdown from "./Markdown";
import { CheckIcon, CopyIcon } from "./icons";

export type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  tools: string[];
  status: "streaming" | "done" | "error" | "stopped";
  error?: string;
};

function ToolChips({ tools }: { tools: string[] }) {
  if (tools.length === 0) return null;
  return (
    <div className="mb-2 flex flex-wrap gap-1.5">
      {tools.map((label, index) => (
        <span
          key={`${label}-${index}`}
          className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-xs text-emerald-700"
        >
          <CheckIcon className="h-3 w-3" />
          {label}
        </span>
      ))}
    </div>
  );
}

function ChatMessage({ message, onRetry }: { message: Message; onRetry?: () => void }) {
  const [copied, setCopied] = useState(false);

  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] whitespace-pre-wrap rounded-2xl rounded-br-md bg-indigo-600 px-4 py-2.5 text-[15px] text-white shadow-sm">
          {message.text}
        </div>
      </div>
    );
  }

  const isStreaming = message.status === "streaming";
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(message.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard not available */
    }
  };

  return (
    <div className="flex items-start gap-3">
      <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white">
        A
      </span>
      <div className="min-w-0 flex-1">
        <ToolChips tools={message.tools} />

        {message.text ? (
          <div
            className={`answer rounded-2xl rounded-tl-md border border-slate-200 bg-white px-4 py-3 text-[15px] text-slate-700 shadow-sm ${
              isStreaming ? "cursor" : ""
            }`}
          >
            <Markdown text={message.text} />
          </div>
        ) : isStreaming ? (
          <div className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
            <span className="flex gap-1">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-indigo-400 [animation-delay:-0.3s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-indigo-400 [animation-delay:-0.15s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-indigo-400" />
            </span>
            {message.tools.length ? "Working on it…" : "Thinking…"}
          </div>
        ) : null}

        {message.status === "error" ? (
          <div className="mt-2 flex flex-wrap items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            <span>{message.error}</span>
            {onRetry ? (
              <button onClick={onRetry} className="font-medium underline hover:text-red-900">
                Try again
              </button>
            ) : null}
          </div>
        ) : null}

        {message.status === "stopped" ? (
          <p className="mt-1.5 text-xs text-slate-400">Stopped.</p>
        ) : null}

        {message.status === "done" && message.text ? (
          <button
            onClick={copy}
            className="mt-1.5 inline-flex items-center gap-1 rounded-md px-1.5 py-1 text-xs text-slate-400 hover:bg-slate-100 hover:text-slate-600"
          >
            {copied ? <CheckIcon className="h-3.5 w-3.5" /> : <CopyIcon className="h-3.5 w-3.5" />}
            {copied ? "Copied" : "Copy"}
          </button>
        ) : null}
      </div>
    </div>
  );
}

export default memo(ChatMessage);
