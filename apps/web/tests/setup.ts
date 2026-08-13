import "@testing-library/jest-dom/vitest";
import { beforeEach } from "vitest";

const storage = new Map<string, string>();

Object.defineProperty(window, "localStorage", {
  configurable: true,
  value: {
    clear: () => storage.clear(),
    getItem: (key: string) => storage.get(key) ?? null,
    key: (index: number) => [...storage.keys()][index] ?? null,
    removeItem: (key: string) => storage.delete(key),
    setItem: (key: string, value: string) => storage.set(key, String(value)),
    get length() { return storage.size; },
  },
});

beforeEach(() => {
  window.localStorage.clear();
});
