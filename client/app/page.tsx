"use client";

import { useEffect, useRef, useState } from "react";
import Hero from "./components/landing/Hero";
import OutputArea from "./components/landing/OutputArea";
import PageShell from "./components/landing/PageShell";
import PromptInput from "./components/landing/PromptInput";
import TopBar from "./components/landing/TopBar";
import { sendChatPrompt } from "./lib/chatApi";

const formatTwoDigits = (value: number) => value.toString().padStart(2, "0");

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<
    Array<{ id: string; role: "user" | "assistant" | "error"; body: string }>
  >([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasChatStarted, setHasChatStarted] = useState(false);
  const messageCounter = useRef(0);
  const [now, setNow] = useState(() => new Date());
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      setNow(new Date());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!hasChatStarted) {
      return;
    }

    chatEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [hasChatStarted, messages, isLoading]);

  const clockTime = `${formatTwoDigits(now.getHours())}:${formatTwoDigits(
    now.getMinutes()
  )}`;
  const clockSeconds = formatTwoDigits(now.getSeconds());
  const clockDate = now.toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  const handleSend = async () => {
    const originalPrompt = prompt;
    const trimmed = originalPrompt.trim();
    if (!trimmed) {
      return;
    }

    setHasChatStarted(true);
    setIsLoading(true);
    messageCounter.current += 1;
    setMessages((prev) => [
      ...prev,
      {
        id: `user-${messageCounter.current}`,
        role: "user",
        body: trimmed,
      },
    ]);
    setPrompt("");

    try {
      const text = await sendChatPrompt(trimmed);
      messageCounter.current += 1;
      setMessages((prev) => [
        ...prev,
        {
          id: `assistant-${messageCounter.current}`,
          role: "assistant",
          body: text,
        },
      ]);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Request failed.";
      messageCounter.current += 1;
      setMessages((prev) => [
        ...prev,
        {
          id: `error-${messageCounter.current}`,
          role: "error",
          body: message,
        },
      ]);
      setPrompt(originalPrompt);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageShell>
      <OutputArea>
        <TopBar
          brand="Adiutor"
          showClock={hasChatStarted}
          time={`${clockTime}:${clockSeconds}`}
        />
        {!hasChatStarted ? (
          <Hero title="Hello, User." subtitle="What are we exploring today?" />
        ) : null}
        {!hasChatStarted ? (
          <section className="mt-10 flex items-center justify-center">
            <div className="w-full max-w-xl rounded-[32px] border border-white/10 bg-white/5 px-10 py-12 text-center ">
              <p className="text-xs uppercase tracking-[0.4em] text-zinc-500">
                Local time
              </p>
              <div className="mt-4 flex items-end justify-center gap-2 font-mono text-5xl tracking-tight text-zinc-50 sm:text-6xl">
                <span>{clockTime}</span>
                <span className="pb-1 text-2xl text-zinc-400">
                  {clockSeconds}
                </span>
              </div>
              <p className="mt-4 text-sm text-zinc-400">{clockDate}</p>
            </div>
          </section>
        ) : null}
        {hasChatStarted ? (
          <div className="relative mt-6">
            <div className="max-h-[calc(100vh-260px)] pr-2">
              <div className="flex flex-col gap-6 pb-24">
                {messages.map((message) => {
                  const isUser = message.role === "user";
                  const isError = message.role === "error";

                  return (
                    <div
                      key={message.id}
                      className={`flex items-start gap-3 ${
                        isUser ? "justify-end" : "justify-start"
                      }`}
                    >
                      {isUser ? null : (
                        <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/5 text-xs text-zinc-200">
                          🔆
                        </div>
                      )}
                      <div
                        className={
                          isUser
                            ? "max-w-[75%] rounded-2xl bg-zinc-800/90 px-4 py-3 text-base text-zinc-100"
                            : "max-w-[75%] rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-base text-zinc-200"
                        }
                      >
                        <p
                          className={
                            isError
                              ? "whitespace-pre-wrap text-red-300"
                              : "whitespace-pre-wrap"
                          }
                        >
                          {message.body}
                        </p>
                      </div>
                    </div>
                  );
                })}
                {isLoading ? (
                  <div className="flex items-start gap-3">
                    <div className="mt-1 flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/5 text-xs text-zinc-200">
                      🔆
                    </div>
                    <div className="max-w-[75%] rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-zinc-300">
                      Adiutor is thinking...
                    </div>
                  </div>
                ) : null}
                <div ref={chatEndRef} />
              </div>
            </div>
          </div>
        ) : null}
      </OutputArea>
      <PromptInput
        placeholder="Ask me anything..."
        helperText="AI can make mistakes. Consider verifying important information."
        value={prompt}
        onChange={setPrompt}
        onSend={handleSend}
        isLoading={isLoading}
      />
    </PageShell>
  );
}
