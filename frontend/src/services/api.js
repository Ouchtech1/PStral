const API_URL = import.meta.env.VITE_API_URL || "/api/v1";

/** Stream server-sent events from the authenticated demo chat endpoint. */
export async function* streamChat(messages, mode, token, signal) {
    const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({ messages, mode }),
        signal,
    });

    if (!response.ok) {
        let detail = "Le service est indisponible.";
        try {
            detail = (await response.json()).detail || detail;
        } catch {
            // Keep a safe generic message when the proxy returns non-JSON.
        }
        throw new Error(detail);
    }

    if (!response.body) throw new Error("Le serveur n'a pas ouvert de flux.");
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const frames = buffer.split("\n\n");
            buffer = frames.pop() || "";
            for (const frame of frames) {
                const dataLine = frame.split("\n").find((line) => line.startsWith("data: "));
                if (!dataLine) continue;
                try {
                    yield JSON.parse(dataLine.slice(6));
                } catch {
                    throw new Error("Réponse de démonstration illisible.");
                }
            }
        }
        if (buffer.trim()) {
            const dataLine = buffer.split("\n").find((line) => line.startsWith("data: "));
            if (dataLine) yield JSON.parse(dataLine.slice(6));
        }
    } finally {
        reader.releaseLock();
    }
}
