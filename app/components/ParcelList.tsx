'use client';

import React from 'react';
import { Ruler, Zap, Droplets, ArrowRight } from 'lucide-react';

interface ParcelListProps {
  parcels: any[];
  onParcelSelect: (parcel: any) => void;
}

const ParcelList = ({ parcels, onParcelSelect }: ParcelListProps) => {
  return (
    <div className="p-8 max-w-6xl mx-auto h-full overflow-y-auto custom-scrollbar">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Viable Opportunities</h2>
          <p className="text-zinc-500 mt-2">Showing top {parcels.length} parcels sorted by viability score.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {parcels.map((parcel) => (
          <div 
            key={parcel.id}
            onClick={() => onParcelSelect(parcel)}
            className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5 hover:border-zinc-600 transition-all cursor-pointer group flex items-center justify-between"
          >
            <div className="flex items-center gap-6">
              {/* Score Circle */}
              <div className={`w-14 h-14 rounded-full border-2 flex flex-col items-center justify-center ${parcel.score > 0.7 ? 'border-green-500 text-green-500' : 'border-yellow-500 text-yellow-500'}`}>
                <span className="text-lg font-black leading-none">{Math.round(parcel.score * 100)}</span>
                <span className="text-[8px] font-bold uppercase tracking-tighter">%</span>
              </div>

              <div>
                <div className="font-bold text-lg group-hover:text-yellow-500 transition-colors">{parcel.address || 'Unnamed Parcel'}</div>
                <div className="flex items-center gap-4 mt-2">
                  <div className="flex items-center gap-1.5 text-xs text-zinc-500">
                    <Ruler size={14} />
                    {parcel.lot_size ? `${parcel.lot_size} ac` : 'N/A'}
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-zinc-500">
                    <Zap size={14} />
                    {parcel.grid?.capacity_mw ? `${parcel.grid.capacity_mw} MW` : 'No Capacity'}
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-zinc-500">
                    <Droplets size={14} />
                    {parcel.enviro?.wetlands_overlap_pct ? `${(parcel.enviro.wetlands_overlap_pct * 100).toFixed(0)}% Impact` : '0% Impact'}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest ${
                parcel.rank === 'EXCELLENT' ? 'bg-green-500/10 text-green-500 border border-green-500/20' : 
                parcel.rank === 'GOOD' ? 'bg-yellow-500/10 text-yellow-500 border border-yellow-500/20' : 
                'bg-zinc-800 text-zinc-500'
              }`}>
                {parcel.rank}
              </div>
              <ArrowRight size={20} className="text-zinc-700 group-hover:text-yellow-500 group-hover:translate-x-1 transition-all" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ParcelList;
