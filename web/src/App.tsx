import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Sidebar } from './components/Sidebar';
import { ActivityView } from './components/ActivityView';
import { LayersView } from './components/LayersView';
import { AssetsView } from './components/AssetsView';
import { MissionDesigner } from './components/MissionDesigner';
import { AssetHUD } from './components/AssetHUD';
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

interface Asset {
  id: string;
  type: string;
  location: [number, number];
  status: string;
  domain: string;
  battery: number;
  signal: number;
  last_heartbeat?: string;
}

type ViewType = 'map' | 'activity' | 'layers' | 'assets' | 'terminal';

function App() {
  const [tracks, setTracks] = useState<Track[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [activeView, setActiveView] = useState<ViewType>('map');
  const [selectedAssetId, setSelectedAssetId] = useState<string | null>(null);

  // Derive selected asset from the list to ensure it's always up to date
  const selectedAsset = assets.find(a => a.id === selectedAssetId) || null;

  useEffect(() => {
    // Fetch initial assets
    fetch('http://localhost:8000/assets')
      .then(res => res.json())
      .then(data => setAssets(data));

    let ws: WebSocket;
    let reconnectTimeout: NodeJS.Timeout;

    const connect = () => {
      ws = new WebSocket('ws://localhost:8000/ws/tracks');

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        // Handle track updates
        if (data.entityId) {
          setTracks(prev => {
            const index = prev.findIndex(t => t.entityId === data.entityId);
            if (index >= 0) {
              const newTracks = [...prev];
              newTracks[index] = data;
              return newTracks;
            }
            return [data, ...prev];
          });
        }

        // Handle asset telemetry
        if (data.type === 'asset_telemetry' || (data.id && data.battery !== undefined)) {
          setAssets(prev => {
            const assetId = data.id || data.entityId || data.entity_id;
            const index = prev.findIndex(a => a.id === assetId);
            const updatedAsset = { ...data, id: assetId }; // Ensure ID is mapped correctly
            if (index >= 0) {
              const newAssets = [...prev];
              newAssets[index] = updatedAsset;
              return newAssets;
            }
            return [...prev, updatedAsset];
          });
        }
      };

      ws.onclose = () => {
        console.log("WebSocket connection closed. Reconnecting...");
        reconnectTimeout = setTimeout(connect, 2000);
      };

      ws.onerror = (err) => {
        console.error("WebSocket error", err);
        ws.close();
      };
    };

    connect();
    return () => {
      if (ws) ws.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, []);

  const handleSaveMission = async (name: string, geometries: any[]) => {
    try {
      const response = await fetch('http://localhost:8000/missions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, geometries }),
      });
      if (response.ok) {
        alert('Mission baseline persisted successfully.');
      } else {
        const err = await response.json();
        alert(`Failed to save mission: ${err.message || response.statusText}`);
      }
    } catch (err) {
      console.error("Failed to save mission", err);
      alert('Network error while saving mission.');
    }
  };


  const renderActiveView = () => {
    switch (activeView) {
      case 'map':
        return (
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
              {/* Tactical Tracks */}
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

              {/* Friendly Assets */}
              {assets.map((asset) => (
                <Marker
                  key={asset.id}
                  position={asset.location}
                  eventHandlers={{
                    click: () => setSelectedAssetId(asset.id),
                  }}
                  icon={L.divIcon({
                    className: 'custom-div-icon',
                    html: `<div style="background-color: #2dd4bf; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px #2dd4bf;"></div>`,
                    iconSize: [12, 12],
                    iconAnchor: [6, 6]
                  })}
                />
              ))}
            </MapContainer>

            {/* Tactical HUD Overlays */}
            {selectedAsset && (
              <AssetHUD
                asset={selectedAsset}
                onClose={() => setSelectedAssetId(null)}
              />
            )}

            <MissionDesigner onSave={handleSaveMission} />

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
        );
      case 'activity':
        return <ActivityView />;
      case 'layers':
        return <LayersView />;
      case 'assets':
        return <AssetsView />;
      case 'terminal':
        return (
          <div className="flex-1 flex items-center justify-center bg-lattice-bg opacity-30 italic">
            Command Terminal Offline - Awaiting Secure Link
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-lattice-bg text-white font-mono">
      {/* Tactical Sidebar Navigation */}
      <aside className="w-16 flex flex-col items-center py-6 border-r border-lattice-border space-y-8 bg-lattice-panel">
        <div className="p-2 rounded-lg bg-lattice-primary/20 text-lattice-primary">
          <Shield size={24} />
        </div>
        <nav className="flex-1 flex flex-col space-y-6 text-gray-400">
          <MapIcon
            size={20}
            onClick={() => setActiveView('map')}
            className={`cursor-pointer transition-colors ${activeView === 'map' ? 'text-lattice-primary' : 'hover:text-white'}`}
          />
          <Activity
            size={20}
            onClick={() => setActiveView('activity')}
            className={`cursor-pointer transition-colors ${activeView === 'activity' ? 'text-lattice-primary' : 'hover:text-white'}`}
          />
          <Layers
            size={20}
            onClick={() => setActiveView('layers')}
            className={`cursor-pointer transition-colors ${activeView === 'layers' ? 'text-lattice-primary' : 'hover:text-white'}`}
          />
          <Terminal
            size={20}
            onClick={() => setActiveView('assets')}
            className={`cursor-pointer transition-colors ${activeView === 'assets' ? 'text-lattice-primary' : 'hover:text-white'}`}
          />
        </nav>
        <div className="flex flex-col space-y-6 text-gray-400 pb-2">
          <Settings size={20} className="hover:text-white cursor-pointer" />
          <LogOut size={20} className="hover:text-white cursor-pointer" />
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex overflow-hidden">
        {/* Active View Panel */}
        {renderActiveView()}

        {/* Intelligence Sidebar */}
        <Sidebar tracks={tracks} />
      </main>
    </div>
  );
}

export default App;
