"use client";
import { apiFetch } from "@/lib/api";
import { queueOperation, type OfflineOperationType } from "@/lib/offline-queue";

export async function submitRegistration<T>(operationType: OfflineOperationType, payload: Record<string, unknown>, entityPath: (id: number) => string): Promise<{ kind: "central"; entity: T } | { kind: "queued" }> {
  const clientOperationId = crypto.randomUUID();
  try {
    const [result] = await apiFetch<Array<{ client_operation_id: string; status: string; entity_id?: number; error?: string }>>("/sync/operations", { method: "POST", cache: "no-store", body: JSON.stringify({ operations: [{ client_operation_id: clientOperationId, operation_type: operationType, payload }] }) });
    if (result?.status !== "synced" || !result.entity_id) {
      const queued = await queueOperation(operationType, payload, clientOperationId);
      const { offlineDb } = await import("@/lib/offline-queue");
      await offlineDb.operations.put({ ...queued, status: "needs_review", last_error: result?.error ?? "Server validation requires review" });
      return { kind: "queued" };
    }
    return { kind: "central", entity: await apiFetch<T>(entityPath(result.entity_id), { cache: "no-store" }) };
  } catch {
    await queueOperation(operationType, payload, clientOperationId);
    return { kind: "queued" };
  }
}
