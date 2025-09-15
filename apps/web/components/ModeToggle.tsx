"use client";

import { usePathname, useRouter } from "next/navigation";

export function ModeToggle() {
  const pathname = usePathname();
  const router = useRouter();
  const mode = pathname?.startsWith("/ingest") ? "ingest" : "ask";

  return (
    <div className="seg" role="tablist" aria-label="Mode toggle">
      <button
        role="tab"
        aria-selected={mode === "ask"}
        className={mode === "ask" ? "active" : ""}
        onClick={() => router.push("/")}
      >
        Ask
      </button>
      <button
        role="tab"
        aria-selected={mode === "ingest"}
        className={mode === "ingest" ? "active" : ""}
        onClick={() => router.push("/ingest")}
      >
        RAG
      </button>
    </div>
  );
}
