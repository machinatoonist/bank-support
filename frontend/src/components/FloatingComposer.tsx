'use client'

import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react'
import { createPortal } from 'react-dom'

export interface FloatingComposerRef {
  focus(): void
  blur(): void
}

export interface FloatingComposerProps {
  onSubmit: (text: string) => void
  disabled?: boolean
  placeholder?: string
  maxRows?: number
  scrollContainerId?: string
}

export const FloatingComposer = forwardRef<FloatingComposerRef, FloatingComposerProps>(
  ({ onSubmit, disabled = false, placeholder = "Type a message...", maxRows = 4, scrollContainerId = "chat-scroll" }, ref) => {
    const [text, setText] = useState('')
    const [composerHeight, setComposerHeight] = useState(0)
    const [mounted, setMounted] = useState(false)
    const textareaRef = useRef<HTMLTextAreaElement>(null)
    const composerRef = useRef<HTMLDivElement>(null)
    const resizeObserverRef = useRef<ResizeObserver | null>(null)

    useImperativeHandle(ref, () => ({
      focus: () => {
        if (textareaRef.current) {
          textareaRef.current.focus({ preventScroll: true })
          // Set caret to end
          textareaRef.current.setSelectionRange(textareaRef.current.value.length, textareaRef.current.value.length)
          textareaRef.current.scrollIntoView({ block: "nearest" })
        }
      },
      blur: () => {
        if (textareaRef.current) {
          textareaRef.current.blur()
        }
      }
    }))

    // Auto-resize textarea logic
    const adjustTextareaHeight = () => {
      const textarea = textareaRef.current
      if (!textarea) return

      // Reset height to calculate scrollHeight accurately
      textarea.style.height = 'auto'

      // Calculate line height and max height
      const lineHeight = 24 // Approximate line height in pixels
      const maxHeight = lineHeight * maxRows

      // Set height based on content, capped at maxRows
      const newHeight = Math.min(textarea.scrollHeight, maxHeight)
      textarea.style.height = `${newHeight}px`
    }

    // Update bottom spacer in scroll container
    const updateBottomSpacer = (height: number) => {
      if (typeof document === 'undefined') return

      const scrollContainer = document.getElementById(scrollContainerId)
      if (!scrollContainer) return

      let spacer = document.getElementById('chat-bottom-spacer')
      if (!spacer) {
        spacer = document.createElement('div')
        spacer.id = 'chat-bottom-spacer'
        spacer.style.flexShrink = '0' // Prevent spacer from shrinking
        scrollContainer.appendChild(spacer)
      }

      // Ensure minimum height and add padding for safe area + spacing
      const minHeight = 100 // Minimum spacer height
      const spacerHeight = Math.max(height + 80, minHeight)
      spacer.style.height = `${spacerHeight}px`
    }

    // Handle textarea input
    const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setText(e.target.value)
      adjustTextareaHeight()
    }

    // Handle form submission
    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault()
      if (text.trim() && !disabled) {
        onSubmit(text.trim())
        setText('')
        // Reset textarea height after submit
        if (textareaRef.current) {
          textareaRef.current.style.height = 'auto'
        }
      }
    }

    // Handle keyboard events
    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        handleSubmit(e)
      }
    }

    // Set up ResizeObserver for composer height tracking
    useEffect(() => {
      if (!composerRef.current) return

      resizeObserverRef.current = new ResizeObserver((entries) => {
        for (const entry of entries) {
          const height = entry.contentRect.height
          setComposerHeight(height)
          updateBottomSpacer(height)
        }
      })

      resizeObserverRef.current.observe(composerRef.current)

      // Set initial spacer with default height
      const initialHeight = composerRef.current.offsetHeight
      updateBottomSpacer(initialHeight || 60) // Default fallback

      return () => {
        if (resizeObserverRef.current) {
          resizeObserverRef.current.disconnect()
        }
      }
    }, [scrollContainerId])

    // Handle window resize to recalculate spacer
    useEffect(() => {
      const handleResize = () => {
        if (composerRef.current) {
          // Small delay to ensure DOM updates are complete
          setTimeout(() => {
            const height = composerRef.current?.offsetHeight || 60
            updateBottomSpacer(height)
          }, 50)
        }
      }

      window.addEventListener('resize', handleResize)
      return () => window.removeEventListener('resize', handleResize)
    }, [scrollContainerId])

    // Auto-focus on mount
    useEffect(() => {
      if (textareaRef.current) {
        textareaRef.current.focus()
      }
    }, [])

    // Handle client-side mounting
    useEffect(() => {
      setMounted(true)
    }, [])

    // Adjust textarea height when text changes
    useEffect(() => {
      adjustTextareaHeight()
    }, [text, maxRows])

    if (!mounted) return null

    const composer = (
      <div
        ref={composerRef}
        className="fixed left-1/2 -translate-x-1/2 w-full max-w-[920px] px-4"
        style={{
          bottom: 'max(12px, calc(env(safe-area-inset-bottom) + 8px))',
          width: 'min(920px, 92vw)',
          zIndex: 9999, // Highest z-index to ensure it's always on top
          pointerEvents: 'auto' // Ensure interaction works
        }}
      >
        <form onSubmit={handleSubmit} className="w-full">
          <div className="relative bg-white rounded-2xl shadow-md p-3 dark:bg-gray-900">
            <textarea
              ref={textareaRef}
              value={text}
              onChange={handleInput}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              disabled={disabled}
              rows={1}
              className="w-full pr-12 bg-transparent border-0 outline-none resize-none placeholder:text-gray-500 dark:text-white dark:placeholder:text-gray-400 focus:ring-2 focus:ring-blue-500 rounded-lg px-2 py-1"
              style={{
                minHeight: '24px',
                lineHeight: '24px'
              }}
            />
            <button
              type="submit"
              disabled={disabled || !text.trim()}
              className="absolute right-2 bottom-2 w-8 h-8 rounded-lg bg-blue-600 text-white disabled:bg-gray-300 disabled:text-gray-500 hover:bg-blue-700 transition-colors flex items-center justify-center text-sm font-semibold"
              style={{ minWidth: '44px', minHeight: '44px' }}
            >
              ↑
            </button>
          </div>
        </form>
      </div>
    )

    return createPortal(composer, document.body)
  }
)

FloatingComposer.displayName = 'FloatingComposer'