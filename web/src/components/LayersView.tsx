import React from 'react';
import { Layers, Eye, EyeOff, Radio, Navigation, Target } from 'lucide-react';

interface LayerToggleProps {
    id: string;
    name: string;
    icon: React.ReactNode;
    active: boolean;
    onToggle: (id: string) => void;
    description: string;
}

const LayerToggle: React.FC<LayerToggleProps> = ({ id, name, icon, active, onToggle, description }) => (
    <div
        onClick={() => onToggle(id)}
        className={`p-4 border rounded-lg cursor-pointer transition-all flex items-start gap-4 ${active ? 'bg-lattice-primary/10 border-lattice-primary' : 'bg-lattice-panel/20 border-lattice-border hover:border-gray-700'
            }`}
    >
        <div className={`p-2 rounded ${active ? 'bg-lattice-primary/20 text-lattice-primary' : 'bg-gray-800 text-gray-500'}`}>
            {icon}
        </div>
        <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
                <h3 className={`text-sm font-bold ${active ? 'text-white' : 'text-gray-400'}`}>{name}</h3>
                {active ? <Eye size={14} className="text-lattice-primary" /> : <EyeOff size={14} className="text-gray-600" />}
            </div>
            <p className="text-[10px] text-gray-500 uppercase tracking-tight">{description}</p>
        </div>
    </div>
);

export const LayersView: React.FC = () => {
    const [activeLayers, setActiveLayers] = React.useState<string[]>(['optical', 'sar', 'assets', 'ao']);

    const toggleLayer = (id: string) => {
        setActiveLayers(prev =>
            prev.includes(id) ? prev.filter(l => l !== id) : [...prev, id]
        );
    };

    return (
        <div className="flex-1 flex flex-col bg-lattice-bg p-6">
            <div className="flex items-center justify-between mb-8">
                <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
                    <Layers className="text-lattice-primary" size={20} />
                    STRATEGIC OVERLAYS
                </h1>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <LayerToggle
                    id="optical"
                    name="Optical Detections"
                    icon={<Target size={18} />}
                    active={activeLayers.includes('optical')}
                    onToggle={toggleLayer}
                    description="Real-time object detection from optical sensors"
                />
                <LayerToggle
                    id="sar"
                    name="SAR Leads"
                    icon={<Radio size={18} />}
                    active={activeLayers.includes('sar')}
                    onToggle={toggleLayer}
                    description="Synthetic Aperture Radar all-weather leads"
                />
                <LayerToggle
                    id="assets"
                    name="Asset Tracking"
                    icon={<Navigation size={18} />}
                    active={activeLayers.includes('assets')}
                    onToggle={toggleLayer}
                    description="Live positions of UAV and UGV platforms"
                />
                <LayerToggle
                    id="ao"
                    name="AOR Boundaries"
                    icon={<Layers size={18} />}
                    active={activeLayers.includes('ao')}
                    onToggle={toggleLayer}
                    description="Area of Operations and exclusion zone markers"
                />
            </div>

            <div className="mt-8 p-6 border border-dashed border-lattice-border rounded-lg bg-lattice-panel/10">
                <h4 className="text-[10px] font-bold text-gray-600 uppercase tracking-widest mb-4">Base Map Configuration</h4>
                <div className="flex gap-4">
                    <div className="px-4 py-2 bg-lattice-primary text-[10px] font-bold rounded uppercase">Tactical Dark</div>
                    <div className="px-4 py-2 bg-lattice-border text-[10px] font-bold rounded uppercase text-gray-400">Satellite Imagery</div>
                    <div className="px-4 py-2 bg-lattice-border text-[10px] font-bold rounded uppercase text-gray-400">Hybrid Grid</div>
                </div>
            </div>
        </div>
    );
};
