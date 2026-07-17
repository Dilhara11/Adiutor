type PromptInputProps = {
  placeholder: string;
  helperText?: string;
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isLoading?: boolean;
};

export default function PromptInput({
  placeholder,
  helperText,
  value,
  onChange,
  onSend,
  isLoading = false,
}: PromptInputProps) {
  const isDisabled = isLoading || !value.trim();

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isDisabled) {
      return;
    }
    onSend();
  };

  return (
    <div className="fixed inset-x-0 bottom-0 z-50 px-4 pb-6">
      <div className="mx-auto w-full max-w-4xl">
        <form
          className="flex items-center gap-3 rounded-full border border-white/10 bg-zinc-900/80 px-4 py-3 shadow-[0_20px_50px_rgba(0,0,0,0.45)] backdrop-blur"
          onSubmit={handleSubmit}
        >
          <input
            className="flex-1 bg-transparent text-lg text-zinc-100 placeholder:text-zinc-500 focus:outline-none"
            placeholder={placeholder}
            value={value}
            onChange={(event) => onChange(event.target.value)}
          />
          <div className="flex items-center gap-2">
            <button
              className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-black transition hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-60"
              type="submit"
              aria-label="Send"
              disabled={isDisabled}
            >
              <svg
                viewBox="0 0 24 24"
                className="h-4 w-4"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
              >
                <path d="M5 12h14" />
                <path d="M13 5l6 7-6 7" />
              </svg>
            </button>
          </div>
        </form>
        {helperText ? (
          <p className="mt-3 text-center text-xs text-zinc-500">{helperText}</p>
        ) : null}
      </div>
    </div>
  );
}
