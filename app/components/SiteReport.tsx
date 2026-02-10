'use client';

import React from 'react';
import { FileText, MapPin, Zap, Droplets, Ruler, ShieldAlert, Truck, BarChart3, Download, ExternalLink, Sun, X } from 'lucide-react';

interface SiteReportProps {
  parcel: any;
  onClose: () => void;
}

const SiteReport = ({ parcel, onClose }: SiteReportProps) => {
  const printReport = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 print:p-0 print:bg-white print:static">
      <div className="bg-zinc-950 border border-zinc-800 w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-2xl shadow-2xl flex flex-col print:max-h-none print:border-none print:shadow-none print:w-full">
        {/* Header */}
        <div className="p-8 border-b border-zinc-800 flex justify-between items-start print:text-black">
          <div>
            <div className="flex items-center gap-2 text-yellow-500 mb-2 print:text-yellow-600">
              <BarChart3 size={24} />
              <span className="font-black uppercase tracking-[0.2em] text-sm">Apollo Site Intel</span>
            </div>
            <h1 className="text-4xl font-black tracking-tight">{parcel.address || 'Unnamed Parcel'}</h1>
            <p className="text-zinc-500 mt-2 font-mono text-sm uppercase">Record ID: {parcel.id} • Generated: {new Date().toLocaleDateString()}</p>
            
            <a 
              href={parcel.satellite_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-xs font-bold text-blue-400 hover:text-blue-300 transition-colors mt-4 print:hidden"
            >
              <ExternalLink size={14} />
              View on Google Maps Satellite
            </a>
          </div>
          <div className="flex gap-3 print:hidden">
            <button 
              onClick={printReport}
              className="flex items-center gap-2 bg-white text-black px-4 py-2 rounded-lg font-bold hover:bg-zinc-200 transition-colors"
            >
              <Download size={18} />
              Export PDF
            </button>
            <button 
              onClick={onClose}
              className="p-2 hover:bg-zinc-900 rounded-lg text-zinc-500"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 grid grid-cols-1 md:grid-cols-3 gap-8 print:text-black">
          {/* Main Score Column */}
          <div className="md:col-span-1 space-y-6">
            <div className="p-8 bg-zinc-900/50 rounded-3xl border border-zinc-800 text-center">
              <div className="text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2">Composite Viability</div>
              <div className={`text-7xl font-black mb-2 ${parcel.score > 0.7 ? 'text-green-500' : 'text-yellow-500'}`}>
                {Math.round(parcel.score * 100)}%
              </div>
              <div className="inline-block px-4 py-1 bg-zinc-800 rounded-full text-sm font-bold border border-zinc-700">
                RANK: {parcel.rank}
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-bold text-sm uppercase tracking-wider text-zinc-500 px-2">Key Metrics</h3>
              <div className="grid grid-cols-1 gap-2">
                <MetricBox label="Lot Size" value={`${parcel.lot_size} ac`} icon={<Ruler size={16}/>} />
                <MetricBox label="Solar Irr." value="4.2 kWh/m²/d" icon={<Sun size={16}/>} />
                <MetricBox label="Grid Cap" value={`${parcel.grid?.capacity_mw || 0} MW`} icon={<Zap size={16}/>} />
                <MetricBox label="Wetlands" value={`${((parcel.enviro?.wetlands_overlap_pct || 0) * 100).toFixed(1)}%`} icon={<Droplets size={16}/>} />
              </div>
            </div>
          </div>

          {/* Detailed Analysis Column */}
          <div className="md:col-span-2 space-y-8">
             <Section title="Implementation Friction Analysis" icon={<ShieldAlert className="text-orange-500"/>}>
                <div className="space-y-4">
                  <AnalysisItem 
                    title="Zoning Compliance" 
                    status={parcel.zoning?.status} 
                    desc={`This parcel is located in the ${parcel.zoning?.zone_code} district. Solar development is currently ${parcel.zoning?.use_type?.replace('_', ' ')}.`} 
                  />
                  <AnalysisItem 
                    title="Environmental Impact" 
                    status={parcel.enviro?.status} 
                    desc={`Wetland overlap is ${((parcel.enviro?.wetlands_overlap_pct || 0) * 100).toFixed(1)}%. Permitting friction is ${parcel.enviro?.status === 'VIABLE' ? 'Low' : 'Critical'}.`} 
                  />
                  <AnalysisItem 
                    title="Grid Connectivity" 
                    status={parcel.grid?.status} 
                    desc={`Connected to ${parcel.grid?.utility} circuit ${parcel.grid?.circuit_id}. Available capacity is ${parcel.grid?.capacity_mw} MW.`} 
                  />
                  <AnalysisItem 
                    title="Physical Access" 
                    status={parcel.infra?.status} 
                    desc={`Site has ${parcel.infra?.frontage_ft || 0} ft of frontage on ${parcel.infra?.access_roads?.join(', ') || 'unnamed public way'}.`} 
                  />
                </div>
             </Section>

             <Section title="Engineering & Topography" icon={<Ruler className="text-purple-500"/>}>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-zinc-900/30 rounded-xl border border-zinc-800">
                    <div className="text-[10px] text-zinc-500 uppercase font-bold">Mean Slope</div>
                    <div className="text-xl font-bold">{parcel.physical?.mean_slope_pct}%</div>
                  </div>
                  <div className="p-4 bg-zinc-900/30 rounded-xl border border-zinc-800">
                    <div className="text-[10px] text-zinc-500 uppercase font-bold">Land Cover</div>
                    <div className="text-xl font-bold">{parcel.physical?.land_cover}</div>
                  </div>
                </div>
             </Section>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-auto p-8 border-t border-zinc-800 text-center text-[10px] text-zinc-600 uppercase tracking-widest font-bold">
          © 2026 Apollo Solar Intelligence Systems • Internal Use Only
        </div>
      </div>
    </div>
  );
};

function MetricBox({ label, value, icon }: { label: string, value: string, icon: any }) {
  return (
    <div className="flex items-center justify-between p-3 bg-zinc-900/30 rounded-xl border border-zinc-800/50">
      <div className="flex items-center gap-3 text-zinc-400">
        {icon}
        <span className="text-xs font-medium">{label}</span>
      </div>
      <span className="text-sm font-bold">{value}</span>
    </div>
  );
}

function Section({ title, icon, children }: { title: string, icon: any, children: React.ReactNode }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 border-b border-zinc-800 pb-2">
        {icon}
        <h3 className="font-bold text-xs uppercase tracking-widest text-zinc-300">{title}</h3>
      </div>
      {children}
    </div>
  );
}

function AnalysisItem({ title, status, desc }: { title: string, status: string, desc: string }) {
  const getStatusColor = (s: string) => {
    if (s === 'VIABLE' || s === 'BY_RIGHT' || s === 'HIGH_POTENTIAL') return 'bg-green-500';
    if (s === 'REVIEW' || s === 'SPECIAL_PERMIT') return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2">
        <div className={`w-1.5 h-1.5 rounded-full ${getStatusColor(status)}`}></div>
        <span className="font-bold text-sm">{title}</span>
        <span className="text-[10px] text-zinc-500 uppercase ml-auto font-mono">{status}</span>
      </div>
      <p className="text-xs text-zinc-400 leading-relaxed">{desc}</p>
    </div>
  );
}

export default SiteReport;
