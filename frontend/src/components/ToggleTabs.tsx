'use client';
import * as ToggleGroup from '@radix-ui/react-toggle-group';
import { cn } from '@/lib/utils';
import { Brush, Sword, Boxes } from 'lucide-react';

export function ToggleTabs() {
    return (
        <ToggleGroup.Root type="single" defaultValue="all" className="inline-flex rounded-2xl bg-zinc-800 p-1">
            <ToggleGroup.Item value="all" className={cn('p-2 rounded-lg hover:bg-zinc-700')}><Boxes className="w-5 h-5" /></ToggleGroup.Item>
            <ToggleGroup.Item value="brush" className={cn('p-2 rounded-lg hover:bg-zinc-700')}><Brush className="w-5 h-5" /></ToggleGroup.Item>
            <ToggleGroup.Item value="sword" className={cn('p-2 rounded-lg hover:bg-zinc-700')}><Sword className="w-5 h-5" /></ToggleGroup.Item>
        </ToggleGroup.Root>
    );
}