import React, { useEffect, useState } from 'react';
import { Shield, Battery, Signal, Activity, Navigation, Zap } from 'lucide-react';

interface Asset {
    id: string;
    type: string;
    location: [number, number];
    status: string;
    domain: string;
}

export const AssetsView: React.FC = () => {
    const [assets, setAssets] = useState<Asset[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAssets = async () => {
            try {
                const response = await fetch('http://localhost:8000/assets');
                const data = await response.json();
                setAssets(data);
            } catch (err) {
                console.error("Failed to fetch assets", err);
            } finally {
                setLoading(false);
            }
        };
        fetchAssets();
    }, []);

    return (
        <div className="flex-1 flex flex-col bg-lattice-bg p-6 overflow-y-auto">
            <div className="flex items-center justify-between mb-8">
                <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
                    <Activity className="text-lattice-primary" size={20} />
                    ASSET UTILIZATION
                </h1>
                <span className="text-[10px] font-bold bg-lattice-primary/10 text-lattice-primary px-3 py-1 rounded-full border border-lattice-primary/20 uppercase tracking-widest">
                    {assets.length} PLATFORMS ONLINE
                </span>
            </div>

            <div className="grid grid-cols-1 gap-6">
                {assets.map((asset) => (
                    <div key={asset.id} className="bg-lattice-panel/30 border border-lattice-border rounded-xl p-6 backdrop-blur-md">
                        <div className="flex items-start justify-between mb-6">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-lg bg-lattice-bg border border-lattice-border flex items-center justify-center text-lattice-primary shadow-lg">
                                    <Navigation size={24} />
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold tracking-tight">{asset.id}</h3>
                                    <p className="text-[10px] text-gray-500 uppercase tracking-widest">{asset.type} • {asset.domain}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className={`w-2 h-2 rounded-full ${asset.status === 'idle' ? 'bg-lattice-primary shadow-[0_0_8px_rgba(45,212,191,0.5)]' : 'bg-lattice-warning animate-pulse'} `} />
                                <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400">{asset.status}</span>
                            </div>
                        </div>

                        <div className="grid grid-cols-3 gap-8">
                            <div className="space-y-2">
                                <div className="flex items-center justify-between text-[9px] text-gray-500 uppercase font-bold tracking-tighter">
                                    <span>Battery</span>
                                    <span>84%</span>
                                </div>
                                <div className="h-1.5 w-full bg-lattice-border rounded-full overflow-hidden">
                                    <div className="bg-lattice-primary h-full w-[84%]" />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <div className="flex items-center justify-between text-[9px] text-gray-500 uppercase font-bold tracking-tighter">
                                    <span>Signal</span>
                                    <Signal size={12} className="text-lattice-primary" />
                                </div>
                                <div className="flex gap-0.5 h-1.5 items-end">
                                    {[...Array(5)].map((_, i) => (
                                        <div key={i} className={`flex-1 rounded-t-sm ${i < 4 ? 'bg-lattice-primary' : 'bg-gray-700'} `} style={{ height: `${(i + 2) * 20}%` }} />
                                    ))}
                                </div>
                            </div>
                            <div className="space-y-2">
                                <div className="flex items-center justify-between text-[9px] text-gray-500 uppercase font-bold tracking-tighter">
                                    <span>Load</span>
                                    <span>2/4 Slots</span>
                                </div>
                                <div className="flex gap-1">
                                    {[...Array(4)].map((_, i) => (
                                        <div key={i} className={`h-1.5 flex-1 rounded-full ${i < 2 ? 'bg-lattice-primary' : 'bg-gray-800'}`} />
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="mt-8 flex gap-3">
                            <button className="flex-1 py-2 bg-lattice-border/50 hover:bg-lattice-border rounded text-[10px] font-bold uppercase tracking-widest transition-colors flex items-center justify-center gap-2">
                                <Zap size={14} /> Telemetry
                            </button>
                            <button className="flex-1 py-2 bg-lattice-primary/10 border border-lattice-primary/30 hover:bg-lattice-primary/20 rounded text-[10px] font-bold uppercase tracking-widest text-lattice-primary transition-colors">
                                Command Log
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
