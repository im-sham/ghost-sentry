import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Sidebar } from './components/Sidebar';
import { Activity, Shield, Map as MapIcon, Layers, Settings, LogOut, Terminal } from 'lucide-react';

// Fix for default marker icon in Leaflet + React
// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface Track {
  entityId: string;
  description: string;
  ontology: { platform_type: string };
  location: { position: { latitudeDegrees: number; longitudeDegrees: number } };
  confidence: number;
}

function App() {
  const [tracks, setTracks] = useState<Track[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch('http://localhost:8000/tracks');
        const data = await res.json();
        setTracks(data);
      } catch (err) {
        console.error("Failed to fetch tracks", err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-lattice-bg text-white font-mono">
      {/* Tactical Sidebar Navigation */}
      <aside className="w-16 flex flex-col items-center py-6 border-r border-lattice-border space-y-8 bg-lattice-panel">
        <div className="p-2 rounded-lg bg-lattice-primary/20 text-lattice-primary">
          <Shield size={24} />
        </div>
        <nav className="flex-1 flex flex-col space-y-6 text-gray-400">
          <MapIcon size={20} className="text-lattice-primary cursor-pointer" />
          <Activity size={20} className="hover:text-white cursor-pointer" />
          <Layers size={20} className="hover:text-white cursor-pointer" />
          <Terminal size={20} className="hover:text-white cursor-pointer" />
        </nav>
        <div className="flex flex-col space-y-6 text-gray-400 pb-2">
          <Settings size={20} className="hover:text-white cursor-pointer" />
          <LogOut size={20} className="hover:text-white cursor-pointer" />
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex overflow-hidden">
        {/* Map Panel */}
        <div className="flex-1 relative border-r border-lattice-border">
          <MapContainer
            center={[33.9425, -118.4081]}
            zoom={13}
            className="h-full w-full"
            zoomControl={false}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            {tracks.map((track) => (
              <Marker
                key={track.entityId}
                position={[track.location.position.latitudeDegrees, track.location.position.longitudeDegrees]}
              >
                <Popup className="tactical-popup">
                  <div className="text-gray-900 font-mono text-xs">
                    <p className="font-bold border-b mb-1 pb-1">{track.ontology.platform_type}</p>
                    <p>ID: {track.entityId.slice(0, 8)}</p>
                    <p>CONF: {(track.confidence * 100).toFixed(1)}%</p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>

          {/* Overlay HUD */}
          <div className="absolute top-4 left-4 z-[1000] pointer-events-none">
            <div className="bg-black/80 border border-lattice-border p-4 rounded backdrop-blur-sm">
              <h1 className="text-lattice-primary font-bold tracking-tighter text-lg flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-lattice-primary animate-pulse" />
                GHOST SENTRY v0.1.0
              </h1>
              <p className="text-[10px] text-gray-500 mt-1 uppercase tracking-widest">Autonomous ISR & Cueing Engine</p>
            </div>
          </div>
        </div>

        {/* Intelligence Sidebar */}
        <Sidebar tracks={tracks} />
      </main>
    </div>
  );
}

export default App;
