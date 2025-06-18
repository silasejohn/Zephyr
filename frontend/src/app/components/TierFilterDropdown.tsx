'use client';
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { cn } from '@shadcn/ui';
import { Check } from 'lucide-react';

const tiers = ['Challenger', 'Grandmaster', 'Master+', 'Master', 'Diamond+', 'Diamond', 'Emerald+', 'Emerald', 'Platinum+', 'Platinum', 'Gold+', 'Gold', 'Silver+', 'Bronze', 'Iron'];

export function TierFilterDropdown() {
    const [selected, setSelected] = React.useState('Emerald+');
    return (
        <DropdownMenu.Root>
            <DropdownMenu.Trigger className="px-3 py-1 bg-zinc-800 rounded hover:bg-zinc-700">{selected}</DropdownMenu.Trigger>
            <DropdownMenu.Content className="grid grid-cols-3 gap-2 bg-zinc-900 p-4 rounded">
                {tiers.map(t => (
                    <button
                        key={t}
                        onClick={() => setSelected(t)}
                        className={cn(
                            'flex items-center justify-between p-2 rounded hover:ring-1 hover:ring-indigo-500',
                            t === selected && 'bg-zinc-700'
                        )}
                    >
                        <span>{t}</span>
                        {t === selected && <Check className="w-4 h-4" />}
                    </button>
                ))}
            </DropdownMenu.Content>
        </DropdownMenu.Root>
    );
}