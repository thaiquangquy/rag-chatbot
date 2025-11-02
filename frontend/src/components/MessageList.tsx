import { SourceList, Source } from "./SourceList";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  isFallback?: boolean;
  relatedTopics?: string[];
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
          {message.role === "assistant" &&
            message.isFallback &&
            message.relatedTopics &&
            message.relatedTopics.length > 0 && (
              <div className="related-topics">
                <p>Related topics you can explore:</p>
                <ul>
                  {message.relatedTopics.map((topic) => (
                    <li key={topic}>{topic}</li>
                  ))}
                </ul>
              </div>
            )}
        </div>
      ))}
    </div>
  );
}
