type PageShellProps = {
  children: React.ReactNode;
};

export default function PageShell({ children }: PageShellProps) {
  return (
    <div className="min-h-screen bg-background text-zinc-100">
      <div className="relative">{children}</div>
    </div>
  );
}
