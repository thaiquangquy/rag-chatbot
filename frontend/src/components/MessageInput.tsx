import { ChangeEvent } from "react";

interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
}

export function MessageInput({ value, onChange, onSend }: MessageInputProps) {
  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    onChange(event.target.value);
  };

  return (
    <div>
      <input value={value} onChange={handleChange} />
      <button type="button" onClick={onSend}>
        Send
      </button>
    </div>
  );
}
