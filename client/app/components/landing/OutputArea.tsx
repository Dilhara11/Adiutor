type OutputAreaProps = {
  children: React.ReactNode;
};

export default function OutputArea({ children }: OutputAreaProps) {
  return (
    <main className="mx-auto flex w-full max-w-4xl flex-col gap-10 px-5 pb-56 pt-24">
      {children}
    </main>
  );
}
