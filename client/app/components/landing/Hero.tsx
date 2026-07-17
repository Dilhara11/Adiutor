type HeroProps = {
  title: string;
  subtitle: string;
};

export default function Hero({ title, subtitle }: HeroProps) {
  return (
    <section className="mt-6 text-center sm:text-left">
      <h1 className="text-3xl font-semibold tracking-tight text-zinc-100 sm:text-4xl">
        {title}
      </h1>
      <p className="mt-2 text-base text-zinc-400 sm:text-lg">{subtitle}</p>
    </section>
  );
}
