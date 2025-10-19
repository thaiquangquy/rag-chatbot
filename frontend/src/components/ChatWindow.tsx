import { useState } from "react";

import { MessageInput } from "./MessageInput";
import { MessageList } from "./MessageList";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const handleSend = () => {
    if (!input.trim()) {
      return;
    }
    setMessages((prevMessages) => [
      ...prevMessages,
      { id: crypto.randomUUID(), role: "user", content: input },
      { id: crypto.randomUUID(), role: "assistant", content: "Coming soon" },
    ]);
    setInput("");
  };

  return (
    <div>
      <MessageList messages={messages} />
      <MessageInput value={input} onChange={setInput} onSend={handleSend} />
    </div>
  );
}
