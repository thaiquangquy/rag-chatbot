import { SourceList, Source } from "./SourceList";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div>
      {messages.map((message) => (
        <div key={message.id}>
          <p>
            <strong>{message.role}:</strong> {message.content}
          </p>
          {message.role === "assistant" && message.sources && (
            <SourceList sources={message.sources} />
          )}
        </div>
      ))}
    </div>
  );
}
