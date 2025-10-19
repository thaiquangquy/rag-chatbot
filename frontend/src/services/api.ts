export async function chat(query: string, sessionId: string) {
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
