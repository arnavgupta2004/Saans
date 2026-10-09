export const getBandColor = (band: string) => {
  switch (band.toLowerCase()) {
    case 'good':
      return 'bg-[#50CCAA] text-white';
    case 'satisfactory':
      return 'bg-[#CEE59B] text-slate-800';
    case 'moderate':
      return 'bg-[#FFD666] text-slate-800';
    case 'poor':
      return 'bg-[#FF9933] text-white';
    case 'very poor':
      return 'bg-[#FF3333] text-white';
    case 'severe':
      return 'bg-[#CC0000] text-white';
    default:
      return 'bg-slate-200 text-slate-800';
  }
};

export const getBandTextColor = (band: string) => {
  switch (band.toLowerCase()) {
    case 'good':
      return 'text-[#50CCAA]';
    case 'satisfactory':
      return 'text-[#8DB600]';
    case 'moderate':
      return 'text-[#E6B800]';
    case 'poor':
      return 'text-[#FF9933]';
    case 'very poor':
      return 'text-[#FF3333]';
    case 'severe':
      return 'text-[#CC0000]';
    default:
      return 'text-slate-500';
  }
};

export const getActionColor = (level: string) => {
  switch (level) {
    case 'go': return 'bg-green-50 border-green-200 text-green-800';
    case 'caution': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
    case 'indoors': return 'bg-red-50 border-red-200 text-red-800';
    default: return 'bg-slate-50 border-slate-200 text-slate-800';
  }
};
