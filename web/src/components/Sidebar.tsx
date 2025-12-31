import React from 'react';
import { Target, AlertTriangle, Crosshair, ChevronRight } from 'lucide-react';

interface Track {
    entityId: string;
    description: string;
    ontology: { platform_type: string };
    location: { position: { latitudeDegrees: number; longitudeDegrees: number } };
    confidence: number;
}

interface SidebarProps {
    tracks: Track[];
}

export const Sidebar: React.FC<SidebarProps> = ({ tracks }) => {
    return (
        <div className="w-80 h-full flex flex-col bg-lattice-panel/50 backdrop-blur-md">
            {/* Header */}
            <div className="p-4 border-b border-lattice-border flex justify-between items-center">
                <h2 className="text-xs font-bold uppercase tracking-widest text-gray-400">Detection Feed</h2>
                <span className="text-[10px] text-lattice-primary bg-lattice-primary/10 px-2 py-0.5 rounded border border-lattice-primary/20">
                    LIVE: {tracks.length}
                </span>
            </div>

            {/* Track List */}
            <div className="flex-1 overflow-y-auto overflow-x-hidden">
                {tracks.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-600 gap-4 opacity-50">
                        <Crosshair size={40} className="animate-spin-slow" />
                        <p className="text-[10px] uppercase tracking-widest">Scanning AO...</p>
                    </div>
                ) : (
                    <div className="divide-y divide-lattice-border">
                        {tracks.map((track) => (
                            <div
                                key={track.entityId}
                                className="p-4 hover:bg-lattice-border/30 cursor-pointer group transition-colors"
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-2">
                                        <Target size={14} className="text-lattice-primary" />
                                        <span className="text-[11px] font-bold uppercase tracking-tight">
                                            {track.ontology.platform_type}
                                        </span>
                                    </div>
                                    <span className={`text-[10px] font-bold ${track.confidence > 0.9 ? 'text-lattice-primary' : 'text-lattice-warning'}`}>
                                        {(track.confidence * 100).toFixed(0)}%
                                    </span>
                                </div>

                                <div className="text-[10px] text-gray-500 mb-2 flex flex-col gap-0.5">
                                    <p>UID: {track.entityId.slice(0, 12)}...</p>
                                    <p>COORD: {track.location.position.latitudeDegrees.toFixed(4)}, {track.location.position.longitudeDegrees.toFixed(4)}</p>
                                </div>

                                <div className="flex items-center justify-between">
                                    {track.confidence > 0.85 ? (
                                        <div className="flex items-center gap-1 text-[9px] text-lattice-primary font-bold uppercase py-0.5 px-2 bg-lattice-primary/5 rounded border border-lattice-primary/10">
                                            <AlertTriangle size={10} />
                                            Cue Generated
                                        </div>
                                    ) : (
                                        <div className="text-[9px] text-gray-600 uppercase">Awaiting Confidence</div>
                                    )}
                                    <ChevronRight size={12} className="text-gray-700 group-hover:text-lattice-primary transform group-hover:translate-x-1 transition-all" />
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Footer Info */}
            <div className="p-4 border-t border-lattice-border bg-black/20">
                <div className="flex items-center justify-between text-[9px] text-gray-500 mb-2">
                    <span>AO: LAX_VIRTUAL_01</span>
                    <span>4 SENSORS OK</span>
                </div>
                <div className="w-full bg-lattice-border h-1 rounded-full overflow-hidden">
                    <div className="bg-lattice-primary h-full w-2/3 animate-pulse" />
                </div>
            </div>
        </div>
    );
};
