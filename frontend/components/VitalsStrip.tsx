import type { Vitals } from "@/lib/types";

function Cell({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-[4.5rem]">
      <p className="text-[10px] uppercase tracking-wide text-ink-muted">{label}</p>
      <p className="font-medium tabular-nums">{value}</p>
    </div>
  );
}

export function VitalsStrip({ vitals }: { vitals: Vitals }) {
  return (
    <div className="flex flex-wrap gap-5 rounded-xl border border-black/10 bg-clinic-soft/50 px-4 py-3">
      <Cell label="Temp" value={`${vitals.temperature_c.toFixed(1)} °C`} />
      <Cell label="HR" value={`${vitals.heart_rate} bpm`} />
      <Cell label="BP" value={vitals.blood_pressure} />
      <Cell label="RR" value={`${vitals.respiratory_rate}`} />
      <Cell label="SpO2" value={`${vitals.spo2}%`} />
      {vitals.pain_score !== null && <Cell label="Pain" value={`${vitals.pain_score}/10`} />}
    </div>
  );
}
