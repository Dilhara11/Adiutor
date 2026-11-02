"use client";

import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import { SendIcon, StopIcon } from "./icons";

type ComposerProps = {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  onStop: () => void;
  isBusy: boolean;
};

export type ComposerHandle = { focus: () => void };

const Composer = forwardRef<ComposerHandle, ComposerProps>(function Composer(
  { value, onChange, onSend, onStop, isBusy },
  ref
) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useImperativeHandle(ref, () => ({
    focus: () => {
      const el = textareaRef.current;
      if (!el) return;
      el.focus();
      el.setSelectionRange(el.value.length, el.value.length);
    },
  }));

  // Grow the box with its content, up to a limit.
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, [value]);

  const canSend = !isBusy && value.trim().length > 0;

  return (
    <div className="border-t border-slate-200 bg-white/80 px-4 pb-4 pt-3 backdrop-blur">
      <form
        className="mx-auto flex w-full max-w-3xl items-end gap-2 rounded-2xl border border-slate-300 bg-white px-3 py-2 shadow-sm focus-within:border-indigo-400 focus-within:ring-4 focus-within:ring-indigo-100"
        onSubmit={(event) => {
          event.preventDefault();
          if (canSend) onSend();
        }}
      >
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) {
              event.preventDefault();
              if (canSend) onSend();
            }
          }}
          placeholder="Ask about employees, teams or records…"
          className="max-h-[200px] flex-1 resize-none bg-transparent py-1.5 text-[15px] text-slate-900 placeholder:text-slate-400 focus:outline-none"
          aria-label="Message"
        />
        {isBusy ? (
          <button
            type="button"
            onClick={onStop}
            className="flex h-9 shrink-0 items-center gap-1.5 rounded-xl bg-slate-800 px-3 text-sm font-medium text-white hover:bg-slate-900"
            aria-label="Stop"
          >
            <StopIcon /> Stop
          </button>
        ) : (
          <button
            type="submit"
            disabled={!canSend}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-indigo-600 text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-400"
            aria-label="Send"
          >
            <SendIcon />
          </button>
        )}
      </form>
      <p className="mx-auto mt-2 max-w-3xl text-center text-xs text-slate-400">
        Press Enter to send · Shift + Enter for a new line · AI can make mistakes, so double-check
        important details.
      </p>
    </div>
  );
});

export default Composer;
