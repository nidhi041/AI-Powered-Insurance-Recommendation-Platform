import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { fetchChatResponse } from '../api/api'
import { MessageCircle, X, Send } from 'lucide-react'

export default function ChatExplainer({ userProfile }) {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const scrollRef = useRef(null)

  useEffect(() => {
    if (userProfile?.full_name && messages.length === 0) {
      setMessages([{
        role: 'assistant',
        content: `Hi ${userProfile.full_name}! How can I help you today?`
      }])
    }
  }, [userProfile])

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await fetchChatResponse({
        question: userMessage,
        user_profile: userProfile,
        session_id: sessionId
      })

      setMessages(prev => [...prev, { role: 'assistant', content: response.answer }])
      setSessionId(response.session_id)
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error communicating with assistant.' }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {isOpen ? (
        <div className="w-80 h-96 bg-white border border-slate-300 shadow-lg flex flex-col">
          <div className="p-3 bg-slate-100 border-b border-slate-300 flex justify-between items-center">
            <span className="font-bold text-sm">Assistant</span>
            <button onClick={() => setIsOpen(false)}><X size={16} /></button>
          </div>
          
          <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-3">
            {messages.map((msg, idx) => (
              <div key={idx} className={`text-sm ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                <div className={`inline-block p-2 rounded ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-200'}`}>
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>
              </div>
            ))}
            {isLoading && <div className="text-xs text-slate-400">Thinking...</div>}
          </div>

          <form onSubmit={handleSendMessage} className="p-3 border-t border-slate-300">
            <div className="flex gap-2">
              <input 
                type="text" 
                className="input text-sm py-1" 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask..."
              />
              <button type="submit" className="p-1 text-blue-600"><Send size={18} /></button>
            </div>
          </form>
        </div>
      ) : (
        <button 
          onClick={() => setIsOpen(true)}
          className="btn rounded-full w-12 h-12 flex items-center justify-center"
        >
          <MessageCircle size={24} />
        </button>
      )}
    </div>
  )
}
