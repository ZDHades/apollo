import Map from '../components/Map';
import { Sun, Filter, Layers, List } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex h-screen w-full bg-zinc-950 overflow-hidden text-zinc-100">
      {/* Sidebar */}
      <aside className="w-80 border-r border-zinc-800 flex flex-col">
        <div className="p-6 border-b border-zinc-800 flex items-center gap-3">
          <div className="p-2 bg-yellow-500 rounded-lg text-zinc-950">
            <Sun size={20} fill="currentColor" />
          </div>
          <h1 className="text-xl font-bold tracking-tight">Apollo</h1>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <div className="px-3 py-2 text-xs font-semibold text-zinc-500 uppercase tracking-wider">
            Exploration
          </div>
          <a href="#" className="flex items-center gap-3 px-3 py-2 bg-zinc-800 rounded-md text-sm font-medium">
            <Layers size={18} />
            Map View
          </a>
          <a href="#" className="flex items-center gap-3 px-3 py-2 hover:bg-zinc-900 rounded-md text-sm font-medium text-zinc-400">
            <List size={18} />
            Parcel List
          </a>
          
          <div className="pt-6 px-3 py-2 text-xs font-semibold text-zinc-500 uppercase tracking-wider">
            Filters
          </div>
          <div className="px-3 py-2 space-y-4">
            <div>
              <label className="text-xs text-zinc-400">Min Acreage</label>
              <input type="range" className="w-full h-1.5 bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-yellow-500" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Grid Viable</span>
              <input type="checkbox" className="w-4 h-4 rounded bg-zinc-800 border-zinc-700 text-yellow-500 focus:ring-yellow-500 focus:ring-offset-zinc-900" />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Low Wetland Impact</span>
              <input type="checkbox" className="w-4 h-4 rounded bg-zinc-800 border-zinc-700 text-yellow-500 focus:ring-yellow-500 focus:ring-offset-zinc-900" />
            </div>
          </div>
        </nav>

        <div className="p-4 border-t border-zinc-800">
          <button className="w-full py-2 bg-yellow-500 hover:bg-yellow-600 text-zinc-950 text-sm font-bold rounded-md transition-colors flex items-center justify-center gap-2">
            <Filter size={16} />
            Apply Filters
          </button>
        </div>
      </aside>

      {/* Main Content (Map) */}
      <main className="flex-1 relative">
        <Map />
      </main>
    </div>
  );
}
