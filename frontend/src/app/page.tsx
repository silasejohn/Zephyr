import { ToggleTabs } from '../components/ToggleTabs';
import { TierFilterDropdown } from '../components/TierFilterDropdown';
import { TierTable } from '../components/TierTable';

export default function Home() {
    return (
        <main className="p-8 bg-zinc-900 min-h-screen">
            <div className="flex items-center justify-between mb-6">
                <ToggleTabs />
                <TierFilterDropdown />
            </div>
            <TierTable />
        </main>
    );
}