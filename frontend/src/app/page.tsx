'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Bot, User, Send, Shield, AlertTriangle, Info, Clock, Loader2 } from 'lucide-react'
import { ThemeToggle } from '@/components/theme-toggle'
import ChatInput, { ChatInputHandle } from '@/components/chat-input'

// Configure API base URL - use same domain for production, localhost for dev
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
    ? ''  // Use same domain for production (served by FastAPI)
    : 'http://localhost:8000')

interface Message {
  type: 'user' | 'agent' | 'system'
  content: string
  data?: {
    support_advice: string
    block_card: boolean
    risk: number
    risk_explanation: string
    risk_category: string
    risk_signals: string[]
  }
  timestamp: string
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([])
  const [customerName, setCustomerName] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [showNameInput, setShowNameInput] = useState(true)
  const [isClient, setIsClient] = useState(false)

  // Fix hydration mismatch by only rendering timestamps on client
  useEffect(() => {
    setIsClient(true)
  }, [])

  const getTimestamp = () => {
    if (!isClient) return ''
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const chatInputRef = useRef<ChatInputHandle>(null)
  const nameInputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Focus after initial mount to chat
  useEffect(() => {
    if (!showNameInput) {
      chatInputRef.current?.focus()
    }
  }, [showNameInput])

  // Focus as soon as streaming ends (assistant finished)
  useEffect(() => {
    if (!isStreaming && !showNameInput) {
      chatInputRef.current?.focus()
    }
  }, [isStreaming, showNameInput])

  // Also focus after new assistant message appended (belt & braces)
  useEffect(() => {
    const last = messages[messages.length - 1]
    if (last?.type === 'agent' && !showNameInput) {
      chatInputRef.current?.focus()
    }
  }, [messages, showNameInput])


  useEffect(() => {
    // Focus the name input when app first loads
    if (nameInputRef.current) {
      setTimeout(() => {
        nameInputRef.current?.focus()
      }, 100)
    }
  }, [])

  const getRiskBadgeVariant = (risk: number) => {
    if (risk <= 2) return 'success'
    if (risk <= 5) return 'warning'
    if (risk <= 8) return 'destructive'
    return 'destructive'
  }

  const getRiskIcon = (category: string) => {
    switch (category) {
      case 'routine': return <Info className="w-4 h-4" />
      case 'concerning': return <Clock className="w-4 h-4" />
      case 'urgent': return <AlertTriangle className="w-4 h-4" />
      case 'critical': return <Shield className="w-4 h-4" />
      default: return <Info className="w-4 h-4" />
    }
  }

  const handleNameSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (customerName.trim()) {
      setShowNameInput(false)
      setMessages([{
        type: 'system',
        content: `Welcome ${customerName}! I'm your AI banking assistant powered by Pydantic AI and Logfire. I can help you with account inquiries, security concerns, and other banking needs. How can I assist you today?`,
        timestamp: getTimestamp()
      }])
    }
  }

  const sendMessage = async (userText: string) => {
    if (!userText.trim() || isStreaming) return

    // 1) Push user message
    const userMessage: Message = {
      type: 'user',
      content: userText,
      timestamp: getTimestamp()
    }
    setMessages(prev => [...prev, userMessage])

    // 2) Start streaming
    setIsStreaming(true)

    try {
      const response = await fetch(`${API_BASE_URL}/support`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userText,
          customer_name: customerName,
          customer_id: 123,
          include_pending: true
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      // 3) Push assistant message
      const agentMessage: Message = {
        type: 'agent',
        content: data.support_advice,
        data,
        timestamp: getTimestamp()
      }
      setMessages(prev => [...prev, agentMessage])

    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        type: 'system',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: getTimestamp()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      // 4) Mark streaming done (triggers focus)
      setIsStreaming(false)
    }
  }

  const resetChat = () => {
    setMessages([])
    setCustomerName('')
    setShowNameInput(true)
  }

  if (showNameInput) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50">
          <ThemeToggle />
        </div>
        <Card className="w-full max-w-2xl mx-auto">
          <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
              <Bot className="h-12 w-12 text-primary" />
            </div>
            <CardTitle className="text-3xl">Bank Support AI Agent</CardTitle>
            <CardDescription className="text-lg">
              Powered by <strong>Pydantic AI</strong> and <strong>Logfire</strong>
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold mb-3">AI-Powered Risk Assessment</h2>
              <p className="text-muted-foreground mb-6">
                This demonstration showcases an intelligent banking support system that uses
                advanced AI to assess customer inquiries, evaluate risk levels, and make
                automated decisions about account security measures.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                <Bot className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">AI-Powered Analysis</span>
              </div>
              <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                <Shield className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">Risk Assessment</span>
              </div>
              <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                <AlertTriangle className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">Automated Decisions</span>
              </div>
              <div className="flex items-center gap-2 p-3 bg-secondary rounded-lg">
                <Info className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">Real-time Monitoring</span>
              </div>
            </div>

            <form onSubmit={handleNameSubmit} className="space-y-4">
              <div>
                <label htmlFor="customerName" className="block text-sm font-medium mb-2">
                  Enter your name to begin:
                </label>
                <Input
                  ref={nameInputRef}
                  id="customerName"
                  type="text"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  placeholder="Your name"
                  required
                />
              </div>
              <Button type="submit" className="w-full">
                Start Chat
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-4">
      <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50">
        <ThemeToggle />
      </div>
      <div className="max-w-4xl mx-auto h-[calc(100vh-2rem)] flex flex-col pt-12 sm:pt-4">
        <Card className="flex-1 flex flex-col">
          <CardHeader className="bg-gradient-to-r from-primary to-primary/80 text-primary-foreground">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Bot className="h-8 w-8" />
                <div>
                  <CardTitle className="text-xl">Bank Support AI Agent</CardTitle>
                  <CardDescription className="text-primary-foreground/80">
                    Customer: {customerName}
                  </CardDescription>
                </div>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={resetChat}
                className="bg-white/10 border-white/20 text-white hover:bg-white/20"
              >
                New Session
              </Button>
            </div>
          </CardHeader>

          <CardContent className="flex-1 flex flex-col p-0">
            <div className="flex-1 overflow-y-auto p-6 space-y-5">
              {messages.map((message, index) => (
                <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {message.type === 'user' && (
                    <div className="max-w-[85%] sm:max-w-[80%] bg-slate-300 dark:bg-slate-600 rounded-2xl border-0 shadow-lg">
                      <div className="p-5 text-lg">
                        <div className="flex items-center gap-3 mb-3">
                          <User className="h-5 w-5 text-slate-800 dark:text-slate-200" />
                          <span className="text-sm font-semibold text-slate-900 dark:text-slate-100">{customerName}</span>
                          <span className="text-xs text-slate-700 dark:text-slate-300 ml-auto">{message.timestamp}</span>
                        </div>
                        <p className="text-slate-900 dark:text-slate-50 leading-relaxed font-medium">{message.content}</p>
                      </div>
                    </div>
                  )}

                  {message.type === 'agent' && (
                    <div className="max-w-[85%] sm:max-w-[80%] bg-white dark:bg-slate-800 rounded-2xl border-0 shadow-md">
                      <div className="p-5 text-lg">
                        <div className="flex items-center gap-3 mb-3">
                          <Bot className="h-5 w-5 text-primary" />
                          <span className="text-sm font-semibold">AI Agent</span>
                          <span className="text-xs text-muted-foreground ml-auto">{message.timestamp}</span>
                        </div>
                        <p className="mb-4 leading-relaxed">{message.content}</p>

                        {message.data && (
                          <div className="space-y-3 pt-3 border-t">
                            <div className="flex flex-wrap gap-2 sm:gap-3">
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-medium">Risk Level:</span>
                                <Badge variant={getRiskBadgeVariant(message.data.risk)} className="flex items-center gap-1">
                                  {getRiskIcon(message.data.risk_category)}
                                  {message.data.risk}/10 ({message.data.risk_category})
                                </Badge>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className="text-sm font-medium">Card Status:</span>
                                <Badge variant={message.data.block_card ? 'destructive' : 'success'}>
                                  {message.data.block_card ? 'BLOCKED' : 'ACTIVE'}
                                </Badge>
                              </div>
                            </div>

                            <div>
                              <span className="text-sm font-medium">Risk Analysis:</span>
                              <p className="text-sm text-muted-foreground mt-1">{message.data.risk_explanation}</p>
                            </div>

                            {message.data.risk_signals && message.data.risk_signals.length > 0 && (
                              <div>
                                <span className="text-sm font-medium">Risk Signals:</span>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {message.data.risk_signals.map((signal, i) => (
                                    <Badge key={i} variant="secondary" className="text-xs">
                                      {signal}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {message.type === 'system' && (
                    <div className="max-w-[95%] sm:max-w-[90%] bg-blue-100 dark:bg-blue-900 rounded-2xl border-0 shadow-md">
                      <div className="p-5 text-center">
                        <p className="text-base text-blue-900 dark:text-blue-100 font-medium leading-relaxed">{message.content}</p>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {isStreaming && (
                <div className="flex justify-start">
                  <div className="max-w-[85%] sm:max-w-[80%] bg-white dark:bg-slate-800 rounded-2xl border-0 shadow-md">
                    <div className="p-5 text-lg">
                      <div className="flex items-center gap-3 mb-3">
                        <Bot className="h-5 w-5 text-primary" />
                        <span className="text-sm font-semibold">AI Agent</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <Loader2 className="h-5 w-5 animate-spin" />
                        <span className="text-base text-muted-foreground">Analyzing your request...</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            <div className="border-t p-6 sm:p-8">
              <ChatInput
                ref={chatInputRef}
                onSubmit={sendMessage}
                disabled={isStreaming}
                placeholder="Type your message..."
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
