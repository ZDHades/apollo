'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Map from '../components/Map';
import ParcelList from '../components/ParcelList';
import SiteReport from '../components/SiteReport';
import { Sun, Filter, Layers, List, MapPin, Zap, Droplets, Ruler, ShieldAlert, X, Truck, BarChart3, Loader2, ExternalLink } from 'lucide-react';

export default function Home() {
  const [view, setView] = useState<'map' | 'list'>('map');
  const [selectedParcel, setSelectedParcel] = useState<any>(null);
  const [loadingParcel, setLoadingParcel] = useState(false);
  const [showReport, setShowReport] = useState(false);
  const [parcels, setParcels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    minAcreage: 0,
    gridViable: false,
    lowWetland: false,
  });

  // 1. Initial Summary Load (Fast)
  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('/api/parcels');
        const data = await res.json();
        if (data.features) {
          setParcels(data.features.map((f: any) => f.properties));
        }
      } catch (err) {
        console.error('Fetch error:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // 2. Lazy Detail Fetch (Triggered on Select)
  const handleParcelSelect = useCallback(async (id: string) => {
    if (!id) return;
    
    setLoadingParcel(true);
    setSelectedParcel(null); 
    
    try {
      const res = await fetch(`/api/parcels?id=${id}`);
      if (!res.ok) throw new Error('API request failed');
      
      const detail = await res.json();
      if (detail.error) throw new Error(detail.error);
      
      setSelectedParcel(detail);
    } catch (err) {
      console.error('Detail fetch error:', err);
      setSelectedParcel({ id, address: 'Error loading details', error: true });
    } finally {
      setLoadingParcel(false);
    }
  }, []);

  const resetFilters = () => {
    setFilters({
      minAcreage: 0,
      gridViable: false,
      lowWetland: false,
    });
  };

  const filteredParcels = parcels.filter(p => p.lot_size >= filters.minAcreage);

  return (
    <div className="flex h-screen w-full bg-zinc-950 overflow-hidden text-zinc-100 font-sans">
      {/* Sidebar */}
      <aside className="w-80 border-r border-zinc-800 flex flex-col shrink-0">
        <div className="p-6 border-b border-zinc-800 flex items-center gap-3">
          <div className="p-2 bg-yellow-500 rounded-lg text-zinc-950 shadow-lg shadow-yellow-500/20">
            <Sun size={20} fill="currentColor" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">Apollo</h1>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          <div className="px-3 py-2 text-xs font-semibold text-zinc-500 uppercase tracking-wider">
            Exploration
          </div>
          <button 
            onClick={() => setView('map')}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${view === 'map' ? 'bg-zinc-800 text-yellow-500' : 'hover:bg-zinc-900 text-zinc-400'}`}
          >
            <Layers size={18} />
            Map View
          </button>
          <button 
            onClick={() => setView('list')}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors ${view === 'list' ? 'bg-zinc-800 text-yellow-500' : 'hover:bg-zinc-900 text-zinc-400'}`}
          >
            <List size={18} />
            Parcel List
          </button>
          
          <div className="pt-6 px-3 py-2 text-xs font-semibold text-zinc-500 uppercase tracking-wider">
            Filters
          </div>
          <div className="px-3 py-2 space-y-6">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs text-zinc-400 font-bold uppercase tracking-tight">Min Acreage</label>
                <span className="text-xs font-mono text-yellow-500">{filters.minAcreage} ac</span>
              </div>
              <input 
                type="range" min="0" max="50" step="1"
                value={filters.minAcreage}
                onChange={(e) => setFilters(prev => ({ ...prev, minAcreage: parseInt(e.target.value) }))}
                className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-yellow-500" 
              />
            </div>
          </div>
        </nav>

        <div className="p-4 border-t border-zinc-800 bg-zinc-900/50 backdrop-blur-md text-center">
          <div className="text-[10px] text-zinc-500 uppercase tracking-widest mb-4 font-semibold">
            Optimized Engine v2.1
          </div>
          <button 
            onClick={resetFilters}
            className="w-full py-2.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-sm font-bold rounded-md transition-all flex items-center justify-center gap-2"
          >
            <Filter size={16} />
            Reset All
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 relative flex">
        <div className="flex-1 relative overflow-hidden">
          {loading ? (
            <div className="flex h-full w-full items-center justify-center bg-zinc-950">
              <div className="flex flex-col items-center gap-4">
                <Loader2 className="animate-spin text-yellow-500" size={32} />
                <span className="text-xs font-bold uppercase tracking-widest text-zinc-500">Optimizing Geospatial Engine...</span>
              </div>
            </div>
          ) : view === 'map' ? (
            <Map filters={filters} onParcelSelect={handleParcelSelect} />
          ) : (
            <ParcelList parcels={filteredParcels} onParcelSelect={handleParcelSelect} />
          )}
        </div>

        {/* Details Sidebar (Lazy Loaded) */}
        {(selectedParcel || loadingParcel) && (
          <div className="w-96 border-l border-zinc-800 bg-zinc-950 flex flex-col slide-in-right overflow-hidden shadow-2xl relative z-20">
            <div className="p-6 border-b border-zinc-800 flex justify-between items-center bg-zinc-900/50">
              <div className="flex items-center gap-2">
                <BarChart3 size={18} className="text-yellow-500" />
                <h2 className="font-bold text-lg tracking-tight">Parcel Intel</h2>
              </div>
              <button onClick={() => setSelectedParcel(null)} className="p-1.5 hover:bg-zinc-800 rounded-md text-zinc-500 hover:text-zinc-100 transition-colors">
                <X size={20} />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar">
              {loadingParcel ? (
                <div className="h-full flex items-center justify-center">
                  <div className="flex flex-col items-center gap-3">
                    <Loader2 className="animate-spin text-yellow-500" size={32} />
                    <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-600">Querying Database...</span>
                  </div>
                </div>
              ) : selectedParcel && (
                <>
                  {/* Score Header */}
                  <div className="text-center p-6 bg-zinc-900/80 rounded-2xl border border-zinc-800 shadow-inner relative overflow-hidden">
                    <div className="relative z-10">
                       <div className="text-[10px] text-zinc-500 uppercase font-bold tracking-widest mb-1">Viability Score</div>
                       <div className={`text-5xl font-black ${(selectedParcel.score || 0) > 0.7 ? 'text-green-500' : 'text-yellow-500'}`}>
                        {Math.round((selectedParcel.score || 0) * 100)}%
                       </div>
                       <div className="text-xs text-zinc-400 font-medium mt-2 bg-zinc-800 inline-block px-3 py-1 rounded-full border border-zinc-700">
                        Rank: <span className="text-zinc-100 font-bold uppercase tracking-tight ml-1">{selectedParcel.rank || 'POOR'}</span>
                       </div>
                    </div>
                  </div>

                  {/* Header Info */}
                  <div>
                    <div className="flex items-center gap-2 text-yellow-500 mb-1">
                      <MapPin size={16} />
                      <span className="text-xs font-bold uppercase tracking-wider">Location</span>
                    </div>
                    <div className="text-xl font-bold">{selectedParcel.address || 'Unknown Address'}</div>
                    <div className="text-xs text-zinc-500 font-mono mt-1 opacity-60">ID: {selectedParcel.id}</div>
                    
                    {selectedParcel.satellite_url && (
                      <a href={selectedParcel.satellite_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-xs font-bold text-blue-400 hover:text-blue-300 transition-colors mt-3">
                        <Layers size={14} /> Open in Google Satellite <ExternalLink size={12} />
                      </a>
                    )}
                  </div>

                  {/* Status Summary */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
                      <div className="text-[10px] text-zinc-500 uppercase font-bold mb-1">Grid</div>
                      <div className={`text-sm font-bold ${selectedParcel.grid?.status === 'VIABLE' ? 'text-green-500' : 'text-red-500'}`}>{selectedParcel.grid?.status || 'N/A'}</div>
                    </div>
                    <div className="bg-zinc-900/50 p-4 rounded-xl border border-zinc-800">
                      <div className="text-[10px] text-zinc-500 uppercase font-bold mb-1">Wetlands</div>
                      <div className={`text-sm font-bold ${selectedParcel.enviro?.status === 'VIABLE' ? 'text-green-500' : 'text-red-500'}`}>{selectedParcel.enviro?.status || 'N/A'}</div>
                    </div>
                  </div>

                  <section className="space-y-4 bg-zinc-900/30 p-4 rounded-xl border border-zinc-800/50">
                    <div className="flex items-center gap-2 border-b border-zinc-800 pb-2">
                      <Zap size={16} className="text-yellow-500" />
                      <h3 className="font-bold text-xs uppercase tracking-widest text-zinc-400">Grid Connectivity</h3>
                    </div>
                    <div className="space-y-3">
                      <DetailItem label="Utility" value={selectedParcel.grid?.utility} />
                      <DetailItem label="Circuit ID" value={selectedParcel.grid?.circuit_id} />
                      <DetailItem label="Capacity" value={selectedParcel.grid?.capacity_mw ? `${selectedParcel.grid.capacity_mw} MW` : 'Unknown'} />
                    </div>
                  </section>

                  <section className="space-y-4 bg-zinc-900/30 p-4 rounded-xl border border-zinc-800/50">
                    <div className="flex items-center gap-2 border-b border-zinc-800 pb-2">
                      <ShieldAlert size={16} className="text-orange-500" />
                      <h3 className="font-bold text-xs uppercase tracking-widest text-zinc-400">Risk Factors</h3>
                    </div>
                    <div className="space-y-3">
                      <DetailItem label="Owner Type" value={selectedParcel.legal?.owner_type} />
                      <DetailItem label="Social Risk" value={selectedParcel.legal?.social_risk_score ? `${selectedParcel.legal.social_risk_score}/10` : 'N/A'} />
                    </div>
                  </section>
                </>
              )}
            </div>
            
            {!loadingParcel && selectedParcel && !selectedParcel.error && (
              <div className="p-6 border-t border-zinc-800 bg-zinc-900/50">
                <button 
                  onClick={() => setShowReport(true)}
                  className="w-full py-3 bg-zinc-100 text-zinc-950 hover:bg-white font-bold rounded-lg transition-all shadow-lg active:scale-[0.98]"
                >
                  Generate Site Report
                </button>
              </div>
            )}
          </div>
        )}

        {showReport && selectedParcel && (
          <SiteReport parcel={selectedParcel} onClose={() => setShowReport(false)} />
        )}
      </main>
    </div>
  );
}

function DetailItem({ label, value }: { label: string, value: any }) {
  return (
    <div className="flex justify-between text-xs items-center">
      <span className="text-zinc-500 font-medium">{label}</span>
      <span className="font-bold text-zinc-200">{value !== undefined && value !== null ? String(value) : 'N/A'}</span>
    </div>
  );
}
