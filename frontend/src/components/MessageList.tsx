interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div>
      {messages.map((message) => (
        <p key={message.id}>
          <strong>{message.role}:</strong> {message.content}
        </p>
      ))}
    </div>
  );
}
