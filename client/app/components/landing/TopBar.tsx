type TopBarProps = {
  brand: string;
  showClock?: boolean;
  time?: string;
};

export default function TopBar({ brand, showClock = false, time }: TopBarProps) {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-zinc-950/90 px-6 py-4 text-base text-zinc-300 backdrop-blur">
      <div className="grid w-full grid-cols-[1fr_auto_1fr] items-center">
        <span className="text-base font-semibold tracking-wide text-zinc-200">
          {brand}
        </span>
        {showClock && time ? (
          <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-sm text-zinc-200">
            {time}
          </div>
        ) : (
          <div />
        )}
        <div />
      </div>
    </header>
  );
}
