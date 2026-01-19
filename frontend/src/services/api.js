const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

export async function* streamChat(messages, mode = "chat", signal = null) {
    const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ messages, mode }),
        signal, // AbortController signal for cancellation
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Network error");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n\n");
            buffer = lines.pop(); // Keep incomplete line in buffer

            for (const line of lines) {
                if (line.startsWith("data: ")) {
                    const rawData = line.slice(6);
                    if (rawData === "[DONE]") return;

                    try {
                        const parsed = JSON.parse(rawData);
                        if (parsed.content) yield parsed.content;
                    } catch (e) {
                        console.error("Failed to parse SSE data:", rawData);
                        // Fallback for non-JSON or legacy data
                        yield rawData;
                    }
                }
            }
        }
    } finally {
        // Ensure reader is released if aborted
        reader.releaseLock();
    }
}

export async function sendFeedback(payload) {
    const response = await fetch(`${API_URL}/feedback/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new Error("Failed to submit feedback");
    }
    return await response.json();
}

// Get auth token from localStorage
function getAuthToken() {
    return localStorage.getItem('pstral_auth_token');
}

// Execute SQL query
export async function executeSQL(query, maxRows = 100) {
    const token = getAuthToken();
    
    const response = await fetch(`${API_URL}/sql/execute`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...(token && { "Authorization": `Bearer ${token}` })
        },
        body: JSON.stringify({ query, max_rows: maxRows }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Échec de l'exécution SQL");
    }
    
    return await response.json();
}

// Validate SQL query
export async function validateSQL(query) {
    const token = getAuthToken();
    
    const response = await fetch(`${API_URL}/sql/validate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...(token && { "Authorization": `Bearer ${token}` })
        },
        body: JSON.stringify({ query }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Échec de la validation");
    }
    
    return await response.json();
}

// ============================================
// Conversations API (Centralized History)
// ============================================

// Get all user conversations
export async function getConversations(limit = 50) {
    const token = getAuthToken();
    
    const response = await fetch(`${API_URL}/conversations/?limit=${limit}`, {
        headers: {
            ...(token && { "Authorization": `Bearer ${token}` })
        }
    });

    if (!response.ok) {
        throw new Error("Échec du chargement des conversations");
    }
    
    return await response.json();
}

// Create a new conversation
export async function createConversation(id, mode, title = "Nouvelle discussion") {
    const token = getAuthToken();
    
    const response = await fetch(`${API_URL}/conversations/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...(token && { "Authorization": `Bearer ${token}` })
        },
        body: JSON.stringify({ id, mode, title }),
    });

    if (!response.ok) {
        throw new Error("Échec de la création de la conversation");
    }
    
    return await response.json();
}

// Get a single conversation
export async function getConversation(conversationId) {
    const token = getAuthToken();
    
    const response = await fetch(`${API_URL}/conversations/${conversationId}`, {
        headers: {
            ...(token && { "Authorization": `Bearer ${token}` })
        }
    });

    if (!response.ok) {
        if (response.status === 404) {
            return null;
        }
        throw new Error("Échec du chargement de la conversation");
    }
    
    return await response.json();
}

// Update a conversation
export async function updateConversation(conversationId, messages, title = null) {
    const token = getAuthToken();
    
    const body = { messages };
    if (title) body.title = title;
    
    const response = await fetch(`${API_URL}/conversations/${conversationId}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            ...(token && { "Authorization": `Bearer ${token}` })
        },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        throw new Error("Échec de la mise à jour de la conversation");
    }
    
    return await response.json();
}

// Delete a conversation
export async function deleteConversation(conversationId) {
    const token = getAuthToken();
    
    const response = await fetch(`${API_URL}/conversations/${conversationId}`, {
        method: "DELETE",
        headers: {
            ...(token && { "Authorization": `Bearer ${token}` })
        }
    });

    if (!response.ok && response.status !== 204) {
        throw new Error("Échec de la suppression de la conversation");
    }
    
    return true;
}

// Search conversations
export async function searchConversations(query, limit = 20) {
    const token = getAuthToken();
    
    const response = await fetch(`${API_URL}/conversations/search/query?q=${encodeURIComponent(query)}&limit=${limit}`, {
        headers: {
            ...(token && { "Authorization": `Bearer ${token}` })
        }
    });

    if (!response.ok) {
        throw new Error("Échec de la recherche");
    }
    
    return await response.json();
}
