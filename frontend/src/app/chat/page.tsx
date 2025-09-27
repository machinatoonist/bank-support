'use client'

import { useEffect, useRef, useState } from 'react'
import { FloatingComposer, FloatingComposerRef } from '@/components/FloatingComposer'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: 'Hello! How can I help you today?' }
  ])
  const [isStreaming, setIsStreaming] = useState(false)
  const composerRef = useRef<FloatingComposerRef>(null)

  // Focus composer on mount and when streaming ends
  useEffect(() => {
    if (composerRef.current) {
      composerRef.current.focus()
    }
  }, [])

  useEffect(() => {
    if (!isStreaming && composerRef.current) {
      // Small delay to ensure the streaming message is fully rendered
      setTimeout(() => {
        composerRef.current?.focus()
      }, 100)
    }
  }, [isStreaming])

  // Simulate sending to model
  const sendToModel = async (text: string) => {
    // Add user message immediately
    const userMessage: Message = { role: 'user', content: text }
    setMessages(prev => [...prev, userMessage])

    // Start streaming simulation
    setIsStreaming(true)

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))

    // Simulate assistant response
    const responses = [
      "That's an interesting question! Let me think about that for a moment.",
      "I understand what you're asking. Here's what I think about that topic.",
      "Thanks for sharing that with me. Here's my perspective on your question.",
      "That's a great point! Let me provide you with some helpful information.",
      "I can help you with that. Here's what you need to know:"
    ]

    const randomResponse = responses[Math.floor(Math.random() * responses.length)]
    const assistantMessage: Message = { role: 'assistant', content: randomResponse }

    setMessages(prev => [...prev, assistantMessage])
    setIsStreaming(false)
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="flex-none border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-4">
        <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
          Chat Interface Demo
        </h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Test the floating composer with auto-resize and focus management
        </p>
      </div>

      {/* Messages Container */}
      <div
        id="chat-scroll"
        className="flex-1 overflow-y-auto px-6 py-4 space-y-4"
      >
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
              }`}
            >
              <p className="text-sm">{message.content}</p>
            </div>
          </div>
        ))}

        {/* Streaming indicator */}
        {isStreaming && (
          <div className="flex justify-start">
            <div className="bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 px-4 py-2 rounded-2xl">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        {messages.length === 1 && (
          <div className="text-center py-8">
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 max-w-md mx-auto">
              <h3 className="text-lg font-medium text-blue-900 dark:text-blue-100 mb-2">
                Try the floating composer!
              </h3>
              <div className="text-sm text-blue-700 dark:text-blue-200 space-y-2">
                <p>• Type a message in the floating input at the bottom</p>
                <p>• Press Enter to send, Shift+Enter for new line</p>
                <p>• The input auto-resizes up to 4 rows</p>
                <p>• Focus returns automatically after streaming</p>
                <p>• Scroll to test the fixed positioning</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Floating Composer */}
      <FloatingComposer
        ref={composerRef}
        onSubmit={sendToModel}
        disabled={isStreaming}
        placeholder={isStreaming ? "Assistant is typing..." : "Type your message..."}
        maxRows={4}
        scrollContainerId="chat-scroll"
      />
    </div>
  )
}