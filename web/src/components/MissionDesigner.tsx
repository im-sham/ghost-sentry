import React, { useState } from 'react';
import { Target, Save, Trash2, Crosshair } from 'lucide-react';

interface Geometry {
    type: 'polygon' | 'point';
    coords: [number, number][];
    label: string;
}

interface MissionDesignerProps {
    onSave: (name: string, geometries: Geometry[]) => void;
}

export const MissionDesigner: React.FC<MissionDesignerProps> = ({ onSave }) => {
    const [name, setName] = useState('New Mission');
    const [geometries, setGeometries] = useState<Geometry[]>([]);

    const addMockAO = () => {
        const newAO: Geometry = {
            type: 'polygon',
            coords: [
                [33.95, -118.42],
                [33.95, -118.38],
                [33.92, -118.38],
                [33.92, -118.42]
            ],
            label: `AO-${geometries.length + 1}`
        };
        setGeometries([...geometries, newAO]);
    };

    return (
        <div className="absolute bottom-10 right-10 z-[1000] w-72 bg-black/90 border border-lattice-border p-5 rounded-lg backdrop-blur-md shadow-2xl">
            <div className="flex items-center gap-2 mb-4">
                <Target className="text-lattice-primary" size={18} />
                <h2 className="text-sm font-bold uppercase tracking-widest text-white">Mission Designer</h2>
            </div>

            <div className="space-y-4">
                <div>
                    <label className="text-[9px] text-gray-500 uppercase font-bold block mb-1">Mission Name</label>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        className="w-full bg-lattice-bg border border-lattice-border rounded px-2 py-1.5 text-xs focus:border-lattice-primary outline-none"
                    />
                </div>

                <div className="space-y-2">
                    <label className="text-[9px] text-gray-500 uppercase font-bold block">Active Geometries</label>
                    {geometries.map((g, i) => (
                        <div key={i} className="flex items-center justify-between bg-white/5 border border-white/10 rounded px-2 py-1.5">
                            <span className="text-[10px] text-gray-300">{g.label} ({g.type})</span>
                            <Trash2
                                size={12}
                                className="text-gray-500 hover:text-red-500 cursor-pointer"
                                onClick={() => setGeometries(geometries.filter((_, idx) => idx !== i))}
                            />
                        </div>
                    ))}
                    {geometries.length === 0 && (
                        <div className="text-[10px] text-gray-600 italic py-2">No areas defined</div>
                    )}
                </div>

                <div className="flex gap-2 pt-2 border-t border-lattice-border/50">
                    <button
                        onClick={addMockAO}
                        className="flex-1 flex items-center justify-center gap-1.5 py-2 bg-lattice-bg border border-lattice-border hover:border-lattice-primary rounded transition-all text-[9px] font-bold uppercase tracking-widest"
                    >
                        <Crosshair size={12} /> Add AO
                    </button>
                    <button
                        onClick={() => onSave(name, geometries)}
                        disabled={geometries.length === 0}
                        className="flex-1 flex items-center justify-center gap-1.5 py-2 bg-lattice-primary/20 border border-lattice-primary/40 hover:bg-lattice-primary/30 text-lattice-primary rounded transition-all text-[9px] font-bold uppercase tracking-widest disabled:opacity-30"
                    >
                        <Save size={12} /> Persist
                    </button>
                </div>
            </div>
        </div>
    );
};
