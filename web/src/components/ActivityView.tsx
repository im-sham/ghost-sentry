import React, { useEffect, useState } from 'react';
import { Clock, CheckCircle2, AlertCircle, RefreshCcw } from 'lucide-react';

interface TimelineEvent {
    id: number;
    type: string;
    entity_id: string;
    data: any;
    created_at: string;
}

export const ActivityView: React.FC = () => {
    const [events, setEvents] = useState<TimelineEvent[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchTimeline = async () => {
        try {
            const response = await fetch('http://localhost:8000/timeline');
            const data = await response.json();
            setEvents(data);
        } catch (err) {
            console.error("Failed to fetch timeline", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTimeline();
        const interval = setInterval(fetchTimeline, 5000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="flex-1 flex flex-col bg-lattice-bg p-6 overflow-y-auto">
            <div className="flex items-center justify-between mb-8">
                <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
                    <Clock className="text-lattice-primary" size={20} />
                    MISSION TIMELINE
                </h1>
                <button
                    onClick={fetchTimeline}
                    className="p-2 hover:bg-lattice-border rounded transition-colors text-gray-400 hover:text-white"
                >
                    <RefreshCcw size={16} />
                </button>
            </div>

            <div className="relative border-l border-lattice-border ml-3 space-y-8 pb-12">
                {events.map((event) => (
                    <div key={`${event.type}-${event.id}`} className="relative pl-8">
                        {/* Timeline point */}
                        <div className={`absolute left-[-5px] top-1 w-2.5 h-2.5 rounded-full border-2 border-lattice-bg ${event.type === 'task' ? 'bg-lattice-warning' : 'bg-lattice-primary'
                            }`} />

                        <div className="bg-lattice-panel/40 border border-lattice-border p-4 rounded-lg backdrop-blur-sm hover:border-lattice-primary/30 transition-colors">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500">
                                    {event.type} EVENT
                                </span>
                                <span className="text-[9px] text-gray-600 font-mono">
                                    {new Date(event.created_at).toLocaleTimeString()}
                                </span>
                            </div>

                            <h3 className="text-sm font-bold mb-1">
                                {event.type === 'track' ?
                                    `Detected ${event.data.ontology?.platform_type || 'Unknown'}` :
                                    event.data.type || 'Verification Request'
                                }
                            </h3>

                            <p className="text-xs text-gray-400 mb-3">
                                Entity: {event.entity_id?.slice(0, 12)}...
                            </p>

                            {event.type === 'task' && (
                                <div className="flex items-center gap-2 mt-2">
                                    <span className="text-[9px] px-2 py-0.5 rounded bg-lattice-warning/10 text-lattice-warning border border-lattice-warning/20 uppercase font-bold">
                                        {event.data.state || 'pending'}
                                    </span>
                                    <span className="text-[9px] text-gray-500 italic">
                                        Assigned to: {event.data.assigned_to || 'N/A'}
                                    </span>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {events.length === 0 && !loading && (
                    <div className="text-center py-20 opacity-30 italic text-gray-500">
                        No mission events recorded yet
                    </div>
                )}
            </div>
        </div>
    );
};
