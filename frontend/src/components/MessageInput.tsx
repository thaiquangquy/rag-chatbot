import { ChangeEvent } from "react";

interface MessageInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
}

export function MessageInput({
  value,
  onChange,
  onSend,
  disabled = false,
}: MessageInputProps) {
  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    onChange(event.target.value);
  };

  return (
    <div>
      <input value={value} onChange={handleChange} disabled={disabled} />
      <button type="button" onClick={onSend} disabled={disabled}>
        Send
      </button>
    </div>
  );
}
