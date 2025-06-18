'use client';
import Image from 'next/image';
import { ArrowUp, ArrowDown } from 'lucide-react';

interface Row { rank: number; champ: string; img: string; lanePct: number; tier: string; winRate: number; delta: number; pickRate: number; games: number; }
const data: Row[] = [ /* your data here */];

export function TierTable() {
    return (
        <div className="overflow-x-auto">
            <table className="w-full table-auto">
                <thead className="bg-zinc-800 sticky top-0">
                    <tr>
                        {['#', 'Champion', 'Lane', 'Tier', 'Win Rate', 'Δ', 'Pick', 'Games'].map(h => <th key={h} className="p-3 text-left text-sm text-zinc-400">{h}</th>)}
                    </tr>
                </thead>
                <tbody>
                    {data.map(row => (
                        <tr key={row.rank} className="odd:bg-zinc-900 even:bg-zinc-950 hover:bg-zinc-800">
                            <td className="p-3 text-sm text-white">{row.rank}</td>
                            <td className="p-3 flex items-center space-x-2">
                                <Image src={row.img} alt={row.champ} width={24} height={24} className="rounded-full" />
                                <span>{row.champ}</span>
                            </td>
                            <td className="p-3 text-sm text-zinc-300">{row.lanePct}%</td>
                            <td className="p-3 font-semibold text-sm text-indigo-400">{row.tier}</td>
                            <td className="p-3 text-sm text-white">{row.winRate}%</td>
                            <td className="p-3 text-sm flex items-center">
                                {row.delta >= 0 ? <ArrowUp className="w-4 h-4 text-green-400" /> : <ArrowDown className="w-4 h-4 text-red-400" />}
                                <span className={row.delta >= 0 ? 'text-green-400' : 'text-red-400'}>{Math.abs(row.delta)}%</span>
                            </td>
                            <td className="p-3 text-sm text-zinc-300">{row.pickRate}%</td>
                            <td className="p-3 text-sm text-zinc-300">{row.games.toLocaleString()}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}