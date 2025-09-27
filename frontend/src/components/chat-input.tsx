"use client";

import React, {
  forwardRef,
  useImperativeHandle,
  useRef,
  useState,
  KeyboardEvent,
} from "react";
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Send } from 'lucide-react'

export type ChatInputHandle = {
  focus: () => void;
  blur: () => void;
};

type Props = {
  onSubmit: (text: string) => Promise<void> | void;
  placeholder?: string;
  disabled?: boolean;
};

const ChatInput = forwardRef<ChatInputHandle, Props>(
  ({ onSubmit, placeholder = "Type your message…", disabled }, ref) => {
    const inputRef = useRef<HTMLInputElement | null>(null);
    const [text, setText] = useState("");

    useImperativeHandle(ref, () => ({
      focus: () => {
        const el = inputRef.current;
        if (!el) return;
        // Put cursor at end and avoid unexpected scroll jumps
        el.focus({ preventScroll: true });
        const len = el.value.length;
        el.setSelectionRange(len, len);
        // Keep view anchored if needed
        el.scrollIntoView({ block: "nearest" });
      },
      blur: () => inputRef.current?.blur(),
    }));

    const submit = async () => {
      const trimmed = text.trim();
      if (!trimmed || disabled) return;
      setText("");               // clear quickly (good UX)
      await onSubmit(trimmed);   // let parent handle network/stream
    };

    const onKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        submit();
      }
    };

    return (
      <div className="max-w-4xl mx-auto">
        <form onSubmit={(e) => { e.preventDefault(); submit(); }} className="flex gap-3 max-w-[70%] mx-auto">
          <Input
            ref={inputRef}
            className="flex-1 border-2"
            placeholder={placeholder}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={disabled}
            aria-label="Chat message"
          />
          <Button type="submit" disabled={disabled || !text.trim()}>
            <Send className="h-4 w-4" />
          </Button>
        </form>
      </div>
    );
  }
);

ChatInput.displayName = "ChatInput";
export default ChatInput;