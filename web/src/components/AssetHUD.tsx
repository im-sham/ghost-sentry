import React from 'react';
import { Battery, Signal, Navigation, Activity } from 'lucide-react';

interface Asset {
    id: string;
    type: string;
    status: string;
    battery: number;
    signal: number;
    last_heartbeat?: string;
}

interface AssetHUDProps {
    asset: Asset;
    onClose: () => void;
}

export const AssetHUD: React.FC<AssetHUDProps> = ({ asset, onClose }) => {
    return (
        <div className="absolute top-24 right-4 z-[1000] w-64 bg-black/90 border border-lattice-border p-4 rounded-lg backdrop-blur-md shadow-2xl animate-in slide-in-from-right duration-300">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-lattice-primary/10 rounded-lg text-lattice-primary">
                        <Navigation size={18} />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-white leading-none">{asset.id}</h3>
                        <p className="text-[9px] text-gray-500 uppercase tracking-widest mt-1">{asset.type} • {asset.status}</p>
                    </div>
                </div>
                <button onClick={onClose} className="text-gray-500 hover:text-white">&times;</button>
            </div>

            <div className="space-y-4">
                <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-[8px] text-gray-500 uppercase font-bold tracking-tighter">
                        <div className="flex items-center gap-1">
                            <Battery size={10} className={asset.battery < 0.2 ? 'text-red-500' : 'text-lattice-primary'} />
                            <span>Power Reserve</span>
                        </div>
                        <span className={asset.battery < 0.2 ? 'text-red-400' : 'text-white'}>{(asset.battery * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <div
                            className={`h-full transition-all duration-500 ${asset.battery < 0.2 ? 'bg-red-500' : 'bg-lattice-primary'}`}
                            style={{ width: `${asset.battery * 100}%` }}
                        />
                    </div>
                </div>

                <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-[8px] text-gray-500 uppercase font-bold tracking-tighter">
                        <div className="flex items-center gap-1">
                            <Signal size={10} className="text-lattice-primary" />
                            <span>Comms Link</span>
                        </div>
                        <span className="text-white">{(asset.signal * 100).toFixed(0)}%</span>
                    </div>
                    <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
                        <div
                            className="bg-lattice-primary h-full transition-all duration-500"
                            style={{ width: `${asset.signal * 100}%` }}
                        />
                    </div>
                </div>

                <div className="pt-3 border-t border-white/10">
                    <div className="flex items-center justify-between text-[8px] text-gray-500 uppercase font-bold mb-2">
                        <span>Telemetry Stream</span>
                        <div className="flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-lattice-primary animate-pulse" />
                            <span className="text-lattice-primary">Active</span>
                        </div>
                    </div>
                    <div className="bg-white/5 rounded p-2 font-mono text-[8px] text-gray-400 space-y-1">
                        <p>LAT: {asset.location?.[0].toFixed(5)}</p>
                        <p>LON: {asset.location?.[1].toFixed(5)}</p>
                        <p>LAST: {asset.last_heartbeat ? new Date(asset.last_heartbeat).toLocaleTimeString() : 'N/A'}</p>
                    </div>
                </div>
            </div>

            <button className="w-full mt-4 py-2 bg-lattice-primary text-[9px] font-bold uppercase tracking-widest text-black rounded hover:bg-white transition-colors">
                Initiate Command Link
            </button>
        </div>
    );
};
