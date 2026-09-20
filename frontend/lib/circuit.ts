import { api } from "./api";
import type { VisibleCase } from "./types";

let cached: VisibleCase[] | null = null;
let inflight: Promise<VisibleCase[]> | null = null;

export function loadCircuit(force = false): Promise<VisibleCase[]> {
  if (!force && cached) {
    return Promise.resolve(cached);
  }
  if (!force && inflight) {
    return inflight;
  }
  inflight = api
    .freshCircuit(force)
    .then((items) => {
      cached = items;
      return items;
    })
    .finally(() => {
      inflight = null;
    });
  return inflight;
}

export function clearCircuitCache() {
  cached = null;
}
