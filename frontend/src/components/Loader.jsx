export default function Loader() {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-6 animate-fade-in">
      {/* Animated rings */}
      <div className="relative w-20 h-20 flex items-center justify-center">
        <span
          className="absolute inset-0 rounded-full border-2 border-indigo-500/30"
          style={{ animation: 'pulse-ring 1.6s ease-out infinite' }}
        />
        <span
          className="absolute inset-0 rounded-full border-2 border-indigo-400/20"
          style={{ animation: 'pulse-ring 1.6s ease-out infinite 0.5s' }}
        />
        <div className="spinner" />
      </div>

      <div className="text-center">
        <p className="text-lg font-semibold text-slate-200">
          Analyzing your profile…
        </p>
        <p className="text-sm text-slate-500 mt-1">
          Our AI is finding the best policies for you
        </p>
      </div>

      {/* Animated dots */}
      <div className="flex gap-1.5">
        {[0, 1, 2, 3].map((i) => (
          <span
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-indigo-500"
            style={{
              animation: `pulse 1.4s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
      </div>
    </div>
  )
}
