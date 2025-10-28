export interface Source {
  document_id: string;
  section_id: string;
  snippet: string;
  url: string;
}

export interface ChatResponse {
  response_id: string;
  generated_text: string;
  sources: Source[];
}

export async function chat(
  query: string,
  sessionId: string
): Promise<ChatResponse> {
  const response = await fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query, session_id: sessionId }),
  });
  if (!response.ok) {
    throw new Error("Chat request failed");
  }
  return response.json();
}
