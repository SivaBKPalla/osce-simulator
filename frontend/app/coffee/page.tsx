export default function CoffeePage() {
  return (
    <article className="mx-auto max-w-xl rounded-2xl border border-black/10 bg-paper-card p-8 text-center shadow-station">
      <p className="text-xs uppercase tracking-[0.28em] text-clinic-dark">Support</p>
      <h1 className="mt-2 font-serif text-4xl leading-tight">Buy me a coffee</h1>
      <p className="mt-4 text-ink-muted">
        If the simulator helped you practice a station, a coffee keeps the circuit running.
      </p>
      <a
        href="https://www.buymeacoffee.com/sivapalla"
        target="_blank"
        rel="noreferrer"
        className="mt-8 inline-flex items-center justify-center rounded-full bg-[#FFDD00] px-6 py-3 text-sm font-semibold text-[#0D0C22] shadow-station hover:brightness-95"
      >
        Buy me a coffee
      </a>
    </article>
  );
}
