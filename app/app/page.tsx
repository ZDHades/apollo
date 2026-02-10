'use client';

import React, { useState } from 'react';
import Map from '../components/Map';
import { Sun, Filter, Layers, List } from 'lucide-react';

export default function Home() {
  const [view, setView] = useState<'map' | 'list'>('map');
  const [filters, setFilters] = useState({
    minAcreage: 0,
    gridViable: false,
    lowWetland: false,
  });

  return (
    <div className="flex h-screen w-full bg-zinc-950 overflow-hidden text-zinc-100 font-sans">
      {/* Sidebar */}
      <aside className="w-80 border-r border-zinc-800 flex flex-col shrink-0">
        <div className="p-6 border-b border-zinc-800 flex items-center gap-3">
          <div className="p-2 bg-yellow-500 rounded-lg text-zinc-950">
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
                <label className="text-xs text-zinc-400">Min Acreage</label>
                <span className="text-xs font-mono text-yellow-500">{filters.minAcreage} ac</span>
              </div>
              <input 
                type="range" 
                min="0"
                max="50"
                step="1"
                value={filters.minAcreage}
                onChange={(e) => setFilters(prev => ({ ...prev, minAcreage: parseInt(e.target.value) }))}
                className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-yellow-500" 
              />
            </div>
            
            <div className="space-y-4">
              <label className="flex items-center justify-between cursor-pointer group">
                <span className="text-sm text-zinc-300 group-hover:text-zinc-100 transition-colors">Grid Viable Only</span>
                <div className="relative inline-flex items-center">
                  <input 
                    type="checkbox" 
                    checked={filters.gridViable}
                    onChange={(e) => setFilters(prev => ({ ...prev, gridViable: e.target.checked }))}
                    className="sr-only peer" 
                  />
                  <div className="w-9 h-5 bg-zinc-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-zinc-400 after:border-zinc-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-yellow-500 peer-checked:after:bg-zinc-950"></div>
                </div>
              </label>

              <label className="flex items-center justify-between cursor-pointer group">
                <span className="text-sm text-zinc-300 group-hover:text-zinc-100 transition-colors">Low Wetland Impact</span>
                <div className="relative inline-flex items-center">
                  <input 
                    type="checkbox" 
                    checked={filters.lowWetland}
                    onChange={(e) => setFilters(prev => ({ ...prev, lowWetland: e.target.checked }))}
                    className="sr-only peer" 
                  />
                  <div className="w-9 h-5 bg-zinc-800 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-zinc-400 after:border-zinc-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-yellow-500 peer-checked:after:bg-zinc-950"></div>
                </div>
              </label>
            </div>
          </div>
        </nav>

        <div className="p-4 border-t border-zinc-800 bg-zinc-900/50 backdrop-blur-md">
          <div className="text-[10px] text-zinc-500 text-center uppercase tracking-widest mb-2 font-semibold">
            Status: Production WIP
          </div>
          <button className="w-full py-2.5 bg-yellow-500 hover:bg-yellow-600 active:bg-yellow-700 text-zinc-950 text-sm font-bold rounded-md transition-all shadow-lg shadow-yellow-500/10 flex items-center justify-center gap-2">
            <Filter size={16} />
            Reset All Filters
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 relative">
        {view === 'map' ? (
          <Map filters={filters} />
        ) : (
          <div className="p-8 max-w-4xl mx-auto">
            <h2 className="text-2xl font-bold mb-6">Viable Parcel List</h2>
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-2xl">
              <div className="p-12 text-center text-zinc-500">
                <List size={48} className="mx-auto mb-4 opacity-20" />
                <p>Parcel list view is under construction.</p>
                <p className="text-sm mt-2">Switch back to Map View to explore current data.</p>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
