"use client";

import { usePathname, useRouter } from "next/navigation";

export function ModeToggle() {
  const pathname = usePathname();
  const router = useRouter();
  const mode = pathname?.startsWith("/agent") ? "agent" : "rag";

  return (
    <div className="seg" role="tablist" aria-label="Mode toggle">
      <button
        role="tab"
        aria-selected={mode === "agent"}
        className={mode === "agent" ? "active" : ""}
        onClick={() => router.push("/agent")}
      >
        Agent
      </button>
      <button
        role="tab"
        aria-selected={mode === "rag"}
        className={mode === "rag" ? "active" : ""}
        onClick={() => router.push("/rag")}
      >
        RAG
      </button>
    </div>
  );
}
