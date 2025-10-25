'use client';

interface QuickResponsesProps {
  options: string[];
  onSelect: (option: string) => void;
  disabled?: boolean;
}

export default function QuickResponses({ options, onSelect, disabled = false }: QuickResponsesProps) {
  if (!options || options.length === 0) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {options.map((option, index) => (
        <button
          key={index}
          onClick={() => onSelect(option)}
          disabled={disabled}
          className="group relative px-6 py-4 bg-gradient-to-br from-pastel-300 via-pastel-400 to-pastel-500 hover:from-pastel-400 hover:via-pastel-500 hover:to-pastel-600 text-navy-900 rounded-2xl text-sm font-bold transition-all duration-300 hover:scale-[1.02] hover:shadow-2xl disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100 border-2 border-navy-800/30 hover:border-navy-900 shadow-lg overflow-hidden"
        >
          {/* Efecto de brillo */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></div>
          
          {/* Número de opción */}
          <span className="absolute top-2 left-2 text-xs font-bold text-navy-700/50">
            {String.fromCharCode(65 + index)}
          </span>
          
          {/* Texto */}
          <span className="relative block text-left pl-4">
            {option}
          </span>
        </button>
      ))}
    </div>
  );
}
