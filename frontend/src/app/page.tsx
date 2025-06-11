"use client";

import React, { useState } from 'react';
import { Search, BarChart3, Users, Settings, Calendar, Database, ChevronRight, Undo2, Crown, Sparkles, LucideIcon } from 'lucide-react';
// import DraftTool from './components/DraftTool'

// TypeScript Interfaces
interface Champion {
  id: number;
  name: string;
  role: string;
  image: string;
  winRate: number;
  pickRate: number;
  banRate: number;
  flexRoles?: string[];
}

interface DraftState {
  bluePicks: (number | null)[];
  redPicks: (number | null)[];
  blueBans: (number | null)[];
  redBans: (number | null)[];
}

interface Role {
  key: string;
  label: string;
  icon: string;
}

interface NavItem {
  id: string;
  label: string;
  icon: LucideIcon;
  active: boolean;
}

interface FearlessChampion {
  championId: number;
  gameNumber: number;
}

interface DraftOrderItem {
  phase: number;
  team: string;
  action: string;
  champion: number | null;
  active: boolean;
}

interface PhaseTheme {
  team: string;
  action: string;
  bgClass: string;
  flowClass: string;
}

// Extended mock data with 30+ champions
const mockChampions: Champion[] = [
  { id: 1, name: "Aatrox", role: "top", image: "/api/placeholder/64/64", winRate: 52.3, pickRate: 8.7, banRate: 12.1 },
  { id: 2, name: "Ahri", role: "mid", image: "/api/placeholder/64/64", winRate: 54.2, pickRate: 15.3, banRate: 3.2 },
  { id: 3, name: "Yasuo", role: "mid", image: "/api/placeholder/64/64", winRate: 48.9, pickRate: 22.1, banRate: 45.2, flexRoles: ["mid", "adc"] },
  { id: 4, name: "Graves", role: "jungle", image: "/api/placeholder/64/64", winRate: 51.8, pickRate: 12.4, banRate: 8.9, flexRoles: ["jungle", "mid"] },
  { id: 5, name: "Jinx", role: "adc", image: "/api/placeholder/64/64", winRate: 53.1, pickRate: 18.7, banRate: 5.4 },
  { id: 6, name: "Thresh", role: "support", image: "/api/placeholder/64/64", winRate: 49.8, pickRate: 14.2, banRate: 7.8 },
  { id: 7, name: "Azir", role: "mid", image: "/api/placeholder/64/64", winRate: 47.2, pickRate: 6.1, banRate: 18.9 },
  { id: 8, name: "Kai'Sa", role: "adc", image: "/api/placeholder/64/64", winRate: 52.7, pickRate: 21.3, banRate: 8.1 },
  { id: 9, name: "Lee Sin", role: "jungle", image: "/api/placeholder/64/64", winRate: 49.1, pickRate: 16.8, banRate: 12.7 },
  { id: 10, name: "Riven", role: "top", image: "/api/placeholder/64/64", winRate: 50.4, pickRate: 9.2, banRate: 6.3 },
  { id: 11, name: "Orianna", role: "mid", image: "/api/placeholder/64/64", winRate: 51.2, pickRate: 11.3, banRate: 4.7 },
  { id: 12, name: "Jhin", role: "adc", image: "/api/placeholder/64/64", winRate: 52.8, pickRate: 19.4, banRate: 6.2 },
  { id: 13, name: "Garen", role: "top", image: "/api/placeholder/64/64", winRate: 51.7, pickRate: 13.2, banRate: 2.1 },
  { id: 14, name: "Lux", role: "support", image: "/api/placeholder/64/64", winRate: 50.9, pickRate: 18.5, banRate: 3.8, flexRoles: ["support", "mid"] },
  { id: 15, name: "Zed", role: "mid", image: "/api/placeholder/64/64", winRate: 49.3, pickRate: 14.7, banRate: 28.4 },
  { id: 16, name: "Vayne", role: "adc", image: "/api/placeholder/64/64", winRate: 51.1, pickRate: 16.9, banRate: 15.7, flexRoles: ["adc", "top"] },
  { id: 17, name: "Blitzcrank", role: "support", image: "/api/placeholder/64/64", winRate: 52.4, pickRate: 12.8, banRate: 22.1 },
  { id: 18, name: "Darius", role: "top", image: "/api/placeholder/64/64", winRate: 50.8, pickRate: 11.4, banRate: 18.9 },
  { id: 19, name: "Syndra", role: "mid", image: "/api/placeholder/64/64", winRate: 48.7, pickRate: 9.3, banRate: 11.2 },
  { id: 20, name: "Ezreal", role: "adc", image: "/api/placeholder/64/64", winRate: 49.6, pickRate: 24.1, banRate: 4.3 },
  { id: 21, name: "Morgana", role: "support", image: "/api/placeholder/64/64", winRate: 51.8, pickRate: 15.7, banRate: 8.4, flexRoles: ["support", "jungle"] },
  { id: 22, name: "Fiora", role: "top", image: "/api/placeholder/64/64", winRate: 50.2, pickRate: 7.8, banRate: 12.3 },
  { id: 23, name: "Katarina", role: "mid", image: "/api/placeholder/64/64", winRate: 49.9, pickRate: 8.1, banRate: 14.7 },
  { id: 24, name: "Caitlyn", role: "adc", image: "/api/placeholder/64/64", winRate: 51.5, pickRate: 17.2, banRate: 6.8 },
  { id: 25, name: "Leona", role: "support", image: "/api/placeholder/64/64", winRate: 52.1, pickRate: 13.9, banRate: 5.2 },
  { id: 26, name: "Camille", role: "top", image: "/api/placeholder/64/64", winRate: 50.7, pickRate: 6.4, banRate: 9.1, flexRoles: ["top", "jungle"] },
  { id: 27, name: "LeBlanc", role: "mid", image: "/api/placeholder/64/64", winRate: 48.4, pickRate: 5.9, banRate: 16.8 },
  { id: 28, name: "Aphelios", role: "adc", image: "/api/placeholder/64/64", winRate: 49.8, pickRate: 11.7, banRate: 13.4 },
  { id: 29, name: "Nautilus", role: "support", image: "/api/placeholder/64/64", winRate: 51.3, pickRate: 14.6, banRate: 7.9 },
  { id: 30, name: "Irelia", role: "top", image: "/api/placeholder/64/64", winRate: 49.1, pickRate: 8.8, banRate: 21.5, flexRoles: ["top", "mid"] }
];

const draftOrder: string[] = [
  'blue-ban', 'red-ban', 'blue-ban', 'red-ban', 'blue-ban', 'red-ban',
  'blue-pick', 'red-pick', 'red-pick', 'blue-pick', 'blue-pick', 'red-pick',
  'red-ban', 'blue-ban', 'blue-ban', 'red-ban',
  'red-pick', 'blue-pick', 'blue-pick', 'red-pick'
];

const roles: Role[] = [
  { key: 'all', label: 'All', icon: '⚔️' },
  { key: 'top', label: 'Top', icon: '🛡️' },
  { key: 'jungle', label: 'Jungle', icon: '🌲' },
  { key: 'mid', label: 'Mid', icon: '⚡' },
  { key: 'adc', label: 'ADC', icon: '🏹' },
  { key: 'support', label: 'Support', icon: '💎' }
];

const navItems: NavItem[] = [
  { id: 'draft', label: 'Draft Tool', icon: Users, active: true },
  {
    id: 'analytics', label: 'Analytics', icon: BarChart3, active: false
  },
  { id: 'teams', label: 'Team Manager', icon: Calendar, active: false },
  { id: 'data', label: 'Data Sources', icon: Database, active: false },
  { id: 'settings', label: 'Settings', icon: Settings, active: false }
];

const DraftTool: React.FC = () => {
  const [currentPhase, setCurrentPhase] = useState<number>(0);
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedChampion, setSelectedChampion] = useState<Champion | null>(null);
  const [draftState, setDraftState] = useState<DraftState>({
    bluePicks: Array(5).fill(null),
    redPicks: Array(5).fill(null),
    blueBans: Array(5).fill(null),
    redBans: Array(5).fill(null)
  });
  const [gameNumber, setGameNumber] = useState<number>(1);
  const [fearlessChampions, setFearlessChampions] = useState<FearlessChampion[]>([]);
  const [navExpanded, setNavExpanded] = useState<boolean>(false);

  const currentPhaseInfo: string | undefined = draftOrder[currentPhase];
  const [currentTeam, currentAction]: string[] = currentPhaseInfo ? currentPhaseInfo.split('-') : ['', ''];

  // Get champions that are currently picked/banned in this game
  const getCurrentGameChampions = (): number[] => {
    return [...draftState.bluePicks, ...draftState.redPicks, ...draftState.blueBans, ...draftState.redBans].filter((id): id is number => id !== null);
  };

  // Filter champions for main grid (exclude current game and fearless)
  const filteredChampions: Champion[] = mockChampions.filter((champ: Champion) => {
    const currentGameChampions: number[] = getCurrentGameChampions();
    const isInCurrentGame: boolean = currentGameChampions.includes(champ.id);
    const isFearless: boolean = fearlessChampions.some((f: FearlessChampion) => f.championId === champ.id);

    const matchesRole: boolean =
      selectedRole === 'all' ||
      champ.role === selectedRole ||
      (champ.flexRoles?.includes(selectedRole) ?? false);
    const matchesSearch: boolean = champ.name.toLowerCase().includes(searchTerm.toLowerCase());

    return matchesRole && matchesSearch && !isInCurrentGame && !isFearless;
  });

  const handleChampionSelect = (champion: Champion): void => {
    setSelectedChampion(champion);
  };

  const handleLockIn = (): void => {
    if (!selectedChampion || currentPhase >= draftOrder.length) return;

    const newDraftState: DraftState = { ...draftState };

    if (currentAction === 'pick') {
      if (currentTeam === 'blue') {
        const pickIndex: number = newDraftState.bluePicks.findIndex((pick: number | null) => pick === null);
        if (pickIndex !== -1) newDraftState.bluePicks[pickIndex] = selectedChampion.id;
      } else {
        const pickIndex: number = newDraftState.redPicks.findIndex((pick: number | null) => pick === null);
        if (pickIndex !== -1) newDraftState.redPicks[pickIndex] = selectedChampion.id;
      }
    } else if (currentAction === 'ban') {
      if (currentTeam === 'blue') {
        const banIndex: number = newDraftState.blueBans.findIndex((ban: number | null) => ban === null);
        if (banIndex !== -1) newDraftState.blueBans[banIndex] = selectedChampion.id;
      } else {
        const banIndex: number = newDraftState.redBans.findIndex((ban: number | null) => ban === null);
        if (banIndex !== -1) newDraftState.redBans[banIndex] = selectedChampion.id;
      }
    }

    setDraftState(newDraftState);
    setSelectedChampion(null);
    setCurrentPhase((prev: number) => prev + 1);
  };

  const getChampionById = (id: number): Champion | undefined => mockChampions.find((champ: Champion) => champ.id === id);

  const handleUndo = (): void => {
    if (currentPhase === 0) return;

    const prevPhase: number = currentPhase - 1;
    const prevPhaseInfo: string = draftOrder[prevPhase];
    const [prevTeam, prevAction]: string[] = prevPhaseInfo.split('-');

    const newDraftState: DraftState = { ...draftState };

    if (prevAction === 'pick') {
      if (prevTeam === 'blue') {
        const lastPickIndex: number = newDraftState.bluePicks.findLastIndex((pick: number | null) => pick !== null);
        if (lastPickIndex !== -1) newDraftState.bluePicks[lastPickIndex] = null;
      } else {
        const lastPickIndex: number = newDraftState.redPicks.findLastIndex((pick: number | null) => pick !== null);
        if (lastPickIndex !== -1) newDraftState.redPicks[lastPickIndex] = null;
      }
    } else if (prevAction === 'ban') {
      if (prevTeam === 'blue') {
        const lastBanIndex: number = newDraftState.blueBans.findLastIndex((ban: number | null) => ban !== null);
        if (lastBanIndex !== -1) newDraftState.blueBans[lastBanIndex] = null;
      } else {
        const lastBanIndex: number = newDraftState.redBans.findLastIndex((ban: number | null) => ban !== null);
        if (lastBanIndex !== -1) newDraftState.redBans[lastBanIndex] = null;
      }
    }

    setDraftState(newDraftState);
    setCurrentPhase(prevPhase);
  };

  const getDraftOrder = (): DraftOrderItem[] => {
    const order: DraftOrderItem[] = [];

    // First 6 bans
    for (let i = 0; i < 6; i++) {
      const [team, action]: string[] = draftOrder[i].split('-');

      order.push({
        phase: i,
        team,
        action,
        champion: team === 'blue' ? draftState.blueBans[Math.floor(i / 2)] : draftState.redBans[Math.floor(i / 2)],
        active: currentPhase === i
      });
    }

    // First 6 picks
    for (let i = 6; i < 12; i++) {
      const [team, action]: string[] = draftOrder[i].split('-');
      const pickOrder: number[] = [0, 0, 1, 1, 2, 2];
      const pickIndex: number = pickOrder[i - 6];

      order.push({
        phase: i,
        team,
        action,
        champion: team === 'blue' ? draftState.bluePicks[pickIndex] : draftState.redPicks[pickIndex],
        active: currentPhase === i
      });
    }

    // Last 4 bans
    for (let i = 12; i < 16; i++) {
      const [team, action]: string[] = draftOrder[i].split('-');
      const banIndex: number = team === 'blue' ? 3 + (i - 12) % 2 : 3 + (i - 13) % 2;

      order.push({
        phase: i,
        team,
        action,
        champion: team === 'blue' ? draftState.blueBans[banIndex] : draftState.redBans[banIndex],
        active: currentPhase === i
      });
    }

    // Last 4 picks
    for (let i = 16; i < 20; i++) {
      const [team, action]: string[] = draftOrder[i].split('-');
      const pickOrder: number[] = [3, 3, 4, 4];
      const pickIndex: number = pickOrder[i - 16];

      order.push({
        phase: i,
        team,
        action,
        champion: team === 'blue' ? draftState.redPicks[pickIndex] : draftState.bluePicks[pickIndex],
        active: currentPhase === i
      });
    }

    return order;
  };

  // Get current game picks and bans with champion objects
  const getCurrentGamePicksAndBans = (): { picks: Champion[], bans: Champion[] } => {
    const allPicks: number[] = [...draftState.bluePicks, ...draftState.redPicks].filter((pick): pick is number => pick !== null);
    const allBans: number[] = [...draftState.blueBans, ...draftState.redBans].filter((ban): ban is number => ban !== null);
    return {
      picks: allPicks.map((id: number) => getChampionById(id)).filter((champ): champ is Champion => champ !== undefined),
      bans: allBans.map((id: number) => getChampionById(id)).filter((champ): champ is Champion => champ !== undefined)
    };
  };

  // Get theme based on current phase
  const getPhaseTheme = (): PhaseTheme => {
    if (currentPhase >= draftOrder.length) {
      return { team: 'complete', action: 'complete', bgClass: 'from-green-600 to-emerald-700', flowClass: '' };
    }

    // Different shades for pick vs ban phases
    let bgClass: string;
    if (currentTeam === 'blue') {
      bgClass = currentAction === 'pick' ? 'from-blue-500 to-blue-600' : 'from-blue-700 to-blue-800';
    } else {
      bgClass = currentAction === 'pick' ? 'from-red-500 to-red-600' : 'from-red-700 to-red-800';
    }

    const flowClass: string = currentAction === 'pick'
      ? (currentTeam === 'blue' ? 'flowing-arrows-blue' : 'flowing-arrows-red')
      : (currentTeam === 'blue' ? 'flowing-bans-blue' : 'flowing-bans-red');

    return { team: currentTeam, action: currentAction, bgClass, flowClass };
  };

  const theme: PhaseTheme = getPhaseTheme();

  const handleStartNextGame = (): void => {
    setGameNumber((prev: number) => prev + 1);
    const currentGamePicks: number[] = [...draftState.bluePicks, ...draftState.redPicks].filter((id): id is number => id !== null);
    const newFearlessChampions: FearlessChampion[] = currentGamePicks.map((championId: number) => ({
      championId,
      gameNumber
    }));
    setFearlessChampions([...fearlessChampions, ...newFearlessChampions]);
    setDraftState({
      bluePicks: Array(5).fill(null),
      redPicks: Array(5).fill(null),
      blueBans: Array(5).fill(null),
      redBans: Array(5).fill(null)
    });
    setCurrentPhase(0);
    setSelectedChampion(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white flex relative">
      {/* Floating Undo Button */}
      {currentPhase > 0 && (
        <button
          onClick={handleUndo}
          className="fixed bottom-8 right-8 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 p-4 rounded-full shadow-2xl transition-all duration-300 hover:scale-110 z-50 backdrop-blur-sm"
        >
          <Undo2 size={24} />
        </button>
      )}

      {/* Minimalist Side Navigation */}
      <div
        className={`bg-gray-800/90 backdrop-blur-xl border-r border-gray-700/50 transition-all duration-500 ease-out ${navExpanded ? 'w-72' : 'w-1'
          } shadow-2xl relative group`}
        onMouseEnter={() => setNavExpanded(true)}
        onMouseLeave={() => setNavExpanded(false)}
      >
        {/* Collapsed state trigger */}
        <div className={`absolute left-0 top-0 w-8 h-full bg-gradient-to-r from-gray-700/50 to-transparent ${navExpanded ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300 hover:from-gray-600/70 cursor-pointer`}>
          <div className="absolute left-1 top-1/2 transform -translate-y-1/2 w-2 h-16 bg-gradient-to-b from-purple-500 to-pink-600 rounded-r-full shadow-lg"></div>
        </div>

        {/* Expanded content */}
        <div className={`p-6 transition-all duration-300 ${navExpanded ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-8'}`}>
          <div className="flex items-center space-x-3 mb-10">
            <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-lg">
              <Crown size={22} className="text-white" />
            </div>
            <div>
              <h2 className="font-bold text-xl text-gray-100">Draft Pro</h2>
              <p className="text-xs text-gray-400">Elite Edition</p>
            </div>
          </div>

          <nav className="space-y-3">
            {navItems.map((item: NavItem) => (
              <div
                key={item.id}
                className={`flex items-center space-x-4 p-4 rounded-xl cursor-pointer transition-all duration-200 ${item.active
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                  : 'text-gray-300 hover:bg-gray-700/50 hover:text-white'
                  }`}
              >
                <item.icon size={22} />
                <span className="font-medium">{item.label}</span>
                {item.active && (
                  <ChevronRight size={16} className="ml-auto" />
                )}
              </div>
            ))}
          </nav>
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        {/* Themed Header with Flowing Animations */}
        <div className={`bg-gradient-to-r ${theme.bgClass} border-b border-gray-700/50 p-6 shadow-lg relative overflow-hidden`}>
          {/* Flowing Animation Background */}
          <div className={`absolute inset-0 ${theme.flowClass}`}></div>

          <div className="flex items-center justify-between relative z-10">
            <div className="flex items-center space-x-6">
              <div>
                <h1 className="text-3xl font-bold text-white drop-shadow-lg">
                  Draft Analysis Tool
                </h1>
                <div className="text-sm text-gray-100/80 mt-1 drop-shadow">Game {gameNumber} • Patch 14.18 • Admin Mode</div>
              </div>
            </div>

            {/* Prominent Phase Indicator */}
            <div className="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2">
              <div className="px-8 py-4 rounded-2xl text-2xl font-black shadow-2xl bg-black/30 backdrop-blur-sm border border-white/20 text-white text-center">
                {currentPhase < draftOrder.length ?
                  `${currentTeam.toUpperCase()} ${currentAction.toUpperCase()} PHASE` :
                  'DRAFT COMPLETE'}
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-100/60 drop-shadow">
                Phase {currentPhase + 1} of {draftOrder.length}
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-1">
          {/* Premium Stats Panel */}
          <div className="w-96 bg-gray-800/40 backdrop-blur-xl border-r border-gray-700/50 p-6 h-full overflow-y-auto">
            <div className="space-y-6">
              <div>
                <h3 className="text-xl font-bold mb-4 flex items-center text-gray-100">
                  <BarChart3 className="mr-3" size={24} />
                  Champion Analysis
                </h3>

                {selectedChampion && (
                  <div className="bg-gradient-to-br from-gray-700/80 to-gray-800/80 backdrop-blur-xl rounded-xl p-4 mb-4 border border-gray-600/50 shadow-xl">
                    <div className="flex items-center space-x-3 mb-4">
                      <div className="relative">
                        <img
                          src={selectedChampion.image}
                          alt={selectedChampion.name}
                          className="w-12 h-12 rounded-lg border-2 border-gray-500"
                        />
                        <div className="absolute -top-1 -right-1 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full p-0.5">
                          <Crown size={10} />
                        </div>
                      </div>
                      <div>
                        <h4 className="font-bold text-lg text-gray-100">{selectedChampion.name}</h4>
                        <div className="text-sm text-gray-400 capitalize font-medium">{selectedChampion.role}</div>
                      </div>
                    </div>

                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Win Rate</span>
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${selectedChampion.winRate >= 50 ? 'bg-green-400' : 'bg-red-400'}`}></div>
                          <span className={`font-bold ${selectedChampion.winRate >= 50 ? 'text-green-400' : 'text-red-400'}`}>
                            {selectedChampion.winRate}%
                          </span>
                        </div>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Pick Rate</span>
                        <span className="font-bold text-purple-400">{selectedChampion.pickRate}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-300">Ban Rate</span>
                        <span className="font-bold text-pink-400">{selectedChampion.banRate}%</span>
                      </div>
                      {selectedChampion.flexRoles && (
                        <div className="flex justify-between items-center">
                          <span className="text-gray-300">Flex Roles</span>
                          <span className="text-yellow-400 font-bold text-xs">{selectedChampion.flexRoles.join(', ')}</span>
                        </div>
                      )}
                    </div>

                    <button
                      onClick={handleLockIn}
                      disabled={currentPhase >= draftOrder.length}
                      className="w-full mt-4 bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 disabled:opacity-50 disabled:cursor-not-allowed px-4 py-3 rounded-lg font-bold text-sm shadow-lg transition-all duration-200 hover:scale-105"
                    >
                      🔒 Lock In Champion
                    </button>
                  </div>
                )}

                {/* Premium Suggestions */}
                <div className="bg-gradient-to-br from-gray-700/60 to-gray-800/60 backdrop-blur-xl rounded-xl p-4 border border-gray-600/50 shadow-xl">
                  <h4 className="font-bold text-lg mb-3 text-gray-100">AI Recommendations</h4>
                  <div className="space-y-2">
                    <div className="bg-gradient-to-r from-green-600/20 to-emerald-600/20 border border-green-500/30 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                        <span className="text-green-400 font-bold text-xs">HIGH PRIORITY</span>
                      </div>
                      <div className="text-gray-200 text-sm">Strong teamfight composition available</div>
                    </div>
                    <div className="bg-gradient-to-r from-yellow-600/20 to-orange-600/20 border border-yellow-500/30 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                        <span className="text-yellow-400 font-bold text-xs">MEDIUM PRIORITY</span>
                      </div>
                      <div className="text-gray-200 text-sm">Consider flex picks for late-game scaling</div>
                    </div>
                    <div className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border border-purple-500/30 rounded-lg p-3">
                      <div className="flex items-center space-x-2 mb-1">
                        <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                        <span className="text-purple-400 font-bold text-xs">STRATEGIC</span>
                      </div>
                      <div className="text-gray-200 text-sm">Enemy team lacks crowd control</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1 p-6 space-y-6">
            {/* Role Filter */}
            <div className="flex bg-gray-800/60 backdrop-blur-xl p-2 rounded-lg border border-gray-600/50 shadow-lg w-fit">
              {roles.map((role: Role) => (
                <button
                  key={role.key}
                  onClick={() => setSelectedRole(role.key)}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200 flex items-center space-x-1.5 ${selectedRole === role.key
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700/50'
                    }`}
                >
                  <span className="text-xs">{role.icon}</span>
                  <span>{role.label}</span>
                </button>
              ))}
            </div>

            {/* Enhanced Search Bar */}
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-6 pointer-events-none z-20">
                <Search className="w-5 h-5 text-purple-400" />
              </div>
              <div className="absolute inset-y-0 right-0 flex items-center pr-6 pointer-events-none z-20">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                  <Sparkles className="w-4 h-4 text-purple-400/70" />
                </div>
              </div>
              <input
                type="text"
                placeholder="Search champions..."
                value={searchTerm}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchTerm(e.target.value)}
                className="w-full pl-14 pr-16 py-4 bg-gray-800/70 backdrop-blur-sm border border-gray-600/50 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 text-white placeholder-gray-400 text-lg font-medium relative z-10"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 via-pink-500/10 to-orange-500/10 rounded-xl pointer-events-none"></div>
            </div>

            {/* Premium Champion Grid */}
            <div className="bg-gray-800/40 backdrop-blur-xl rounded-2xl p-6 border border-gray-700/50 shadow-xl">
              <div className="h-96 overflow-y-auto custom-scrollbar">
                <div className="grid grid-cols-6 gap-4">
                  {filteredChampions.map((champion: Champion) => {
                    const isSelected: boolean = selectedChampion?.id === champion.id;

                    return (
                      <div
                        key={champion.id}
                        onClick={() => handleChampionSelect(champion)}
                        className={`relative aspect-square rounded-xl overflow-hidden cursor-pointer transition-all duration-300 ${isSelected
                          ? 'ring-4 ring-orange-500 scale-110 shadow-2xl shadow-orange-500/50'
                          : 'hover:scale-105 hover:ring-2 hover:ring-blue-500 hover:shadow-xl hover:shadow-blue-500/30'
                          }`}
                      >
                        <img
                          src={champion.image}
                          alt={champion.name}
                          className="w-full h-full object-cover"
                        />
                        {champion.flexRoles && (
                          <div className="absolute top-2 right-2 bg-gradient-to-r from-yellow-400 to-orange-500 text-black text-xs px-2 py-1 rounded-lg font-bold shadow-lg">
                            FLEX
                          </div>
                        )}
                        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-3">
                          <div className="text-sm font-bold text-white drop-shadow-lg">{champion.name}</div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Current Game & Fearless Champions */}
            <div className="grid grid-cols-2 gap-6">
              <div className="bg-gray-800/40 backdrop-blur-xl rounded-2xl p-6 border border-gray-700/50 shadow-xl">
                <h4 className="font-bold text-lg mb-4 text-gray-100">Current Game</h4>
                <div className="space-y-4">
                  <div>
                    <div className="text-sm text-gray-400 mb-3 flex items-center">
                      <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
                      Picks
                    </div>
                    <div className="flex flex-wrap gap-3">
                      {getCurrentGamePicksAndBans().picks.map((champion: Champion) => (
                        <div key={champion.id} className="text-center">
                          <img src={champion.image} alt={champion.name}
                            className="w-12 h-12 rounded-lg border-2 border-green-500/50 shadow-lg mb-1" />
                          <div className="text-xs text-gray-300 font-medium">{champion.name}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-400 mb-3 flex items-center">
                      <div className="w-2 h-2 bg-red-400 rounded-full mr-2"></div>
                      Bans
                    </div>
                    <div className="flex flex-wrap gap-3">
                      {getCurrentGamePicksAndBans().bans.map((champion: Champion) => (
                        <div key={champion.id} className="text-center">
                          <div className="relative">
                            <img src={champion.image} alt={champion.name}
                              className="w-12 h-12 rounded-lg border-2 border-red-500/50 opacity-60 shadow-lg mb-1" />
                            <div className="absolute inset-0 flex items-center justify-center">
                              <div className="w-0.5 h-10 bg-red-500 rotate-45"></div>
                            </div>
                          </div>
                          <div className="text-xs text-gray-300 font-medium">{champion.name}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800/40 backdrop-blur-xl rounded-2xl p-6 border border-gray-700/50 shadow-xl">
                <h4 className="font-bold text-lg mb-4 text-gray-100">Fearless (Previous Games)</h4>
                <div className="flex flex-wrap gap-3">
                  {fearlessChampions.map(({ championId, gameNumber: gNum }: FearlessChampion) => {
                    const champion: Champion | undefined = getChampionById(championId);
                    return champion ? (
                      <div key={championId} className="text-center">
                        <div className="relative">
                          <img src={champion.image} alt={champion.name}
                            className="w-12 h-12 rounded-lg border-2 border-gray-500/50 grayscale shadow-lg mb-1" />
                          <div className="absolute top-0 right-0 bg-slate-900 text-white text-xs px-1.5 py-0.5 rounded-full border border-gray-500 font-bold">
                            G{gNum}
                          </div>
                        </div>
                        <div className="text-xs text-gray-300 font-medium">{champion.name}</div>
                      </div>
                    ) : null;
                  })}
                  {fearlessChampions.length === 0 && (
                    <div className="text-gray-400 italic">No fearless champions yet</div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Premium Draft Order */}
          <div className="w-80 bg-gray-800/40 backdrop-blur-xl border-l border-gray-700/50 p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-xl font-bold text-gray-100">Draft Order</h3>
              {currentPhase >= draftOrder.length && (
                <button
                  onClick={handleStartNextGame}
                  className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 px-4 py-2 rounded-xl text-sm font-bold shadow-lg transition-all duration-200"
                >
                  Start Game {gameNumber + 1}
                </button>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Blue Column */}
              <div>
                <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white text-center py-3 rounded-t-xl font-bold shadow-lg">
                  BLUE SIDE
                </div>
                <div className="bg-gray-700/60 backdrop-blur-xl rounded-b-xl p-3 space-y-3 border border-gray-600/50">
                  {getDraftOrder().filter((item: DraftOrderItem) => item.team === 'blue').map((item: DraftOrderItem, idx: number) => {
                    const champion: Champion | undefined = item.champion ? getChampionById(item.champion) : undefined;
                    return (
                      <div
                        key={idx}
                        className={`flex items-center space-x-3 p-3 rounded-xl transition-all duration-300 ${item.active ? 'bg-gradient-to-r from-blue-600/40 to-blue-700/40 border-2 border-blue-500 shadow-lg' : 'bg-gray-600/50'
                          }`}
                      >
                        <div className="w-10 h-10 bg-gray-500/50 rounded-lg flex items-center justify-center">
                          {champion ? (
                            <img src={champion.image} alt={champion.name} className="w-full h-full object-cover rounded-lg" />
                          ) : (
                            <div className="text-xs text-gray-300 font-bold">
                              {item.action === 'ban' ? 'B' : 'P'}{Math.floor(item.phase / 2) + 1}
                            </div>
                          )}
                        </div>
                        <div className="flex-1 text-xs">
                          <div className="text-gray-200 font-bold">{item.action.toUpperCase()}</div>
                          <div className="text-gray-400">
                            {champion ? champion.name : `${item.action === 'ban' ? 'B' : 'P'}${Math.floor(item.phase / 2) + 1}`}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Red Column */}
              <div>
                <div className="bg-gradient-to-r from-red-600 to-red-700 text-white text-center py-3 rounded-t-xl font-bold shadow-lg">
                  RED SIDE
                </div>
                <div className="bg-gray-700/60 backdrop-blur-xl rounded-b-xl p-3 space-y-3 border border-gray-600/50">
                  {getDraftOrder().filter((item: DraftOrderItem) => item.team === 'red').map((item: DraftOrderItem, idx: number) => {
                    const champion: Champion | undefined = item.champion ? getChampionById(item.champion) : undefined;
                    return (
                      <div
                        key={idx}
                        className={`flex items-center space-x-3 p-3 rounded-xl transition-all duration-300 ${item.active ? 'bg-gradient-to-r from-red-600/40 to-red-700/40 border-2 border-red-500 shadow-lg' : 'bg-gray-600/50'
                          }`}
                      >
                        <div className="w-10 h-10 bg-gray-500/50 rounded-lg flex items-center justify-center">
                          {champion ? (
                            <img src={champion.image} alt={champion.name} className="w-full h-full object-cover rounded-lg" />
                          ) : (
                            <div className="text-xs text-gray-300 font-bold">
                              {item.action === 'ban' ? 'B' : 'P'}{Math.floor(item.phase / 2) + 1}
                            </div>
                          )}
                        </div>
                        <div className="flex-1 text-xs">
                          <div className="text-gray-200 font-bold">{item.action.toUpperCase()}</div>
                          <div className="text-gray-400">
                            {champion ? champion.name : `${item.action === 'ban' ? 'B' : 'P'}${Math.floor(item.phase / 2) + 1}`}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        /* Flowing Animations */
        .flowing-arrows-blue {
          background-image: 
            repeating-linear-gradient(
              90deg,
              transparent,
              transparent 40px,
              rgba(59, 130, 246, 0.1) 40px,
              rgba(59, 130, 246, 0.1) 60px
            );
          animation: flow-right 3s linear infinite;
        }

        .flowing-arrows-blue::after {
          content: '→ → → → → → → → → → → → → → → → → → → →';
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          transform: translateY(-50%);
          color: rgba(59, 130, 246, 0.15);
          font-size: 24px;
          text-align: center;
          letter-spacing: 20px;
          animation: flow-right 4s linear infinite;
          pointer-events: none;
        }

        .flowing-arrows-red {
          background-image: 
            repeating-linear-gradient(
              90deg,
              transparent,
              transparent 40px,
              rgba(239, 68, 68, 0.1) 40px,
              rgba(239, 68, 68, 0.1) 60px
            );
          animation: flow-right 3s linear infinite;
        }

        .flowing-arrows-red::after {
          content: '→ → → → → → → → → → → → → → → → → → → →';
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          transform: translateY(-50%);
          color: rgba(239, 68, 68, 0.15);
          font-size: 24px;
          text-align: center;
          letter-spacing: 20px;
          animation: flow-right 4s linear infinite;
          pointer-events: none;
        }

        .flowing-bans-blue {
          background-image: 
            repeating-linear-gradient(
              90deg,
              transparent,
              transparent 40px,
              rgba(59, 130, 246, 0.1) 40px,
              rgba(59, 130, 246, 0.1) 60px
            );
          animation: flow-right 3s linear infinite;
        }

        .flowing-bans-blue::after {
          content: '✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗';
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          transform: translateY(-50%);
          color: rgba(59, 130, 246, 0.15);
          font-size: 20px;
          text-align: center;
          letter-spacing: 25px;
          animation: flow-right 4s linear infinite;
          pointer-events: none;
        }

        .flowing-bans-red {
          background-image: 
            repeating-linear-gradient(
              90deg,
              transparent,
              transparent 40px,
              rgba(239, 68, 68, 0.1) 40px,
              rgba(239, 68, 68, 0.1) 60px
            );
          animation: flow-right 3s linear infinite;
        }

        .flowing-bans-red::after {
          content: '✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗ ✗';
          position: absolute;
          top: 50%;
          left: 0;
          right: 0;
          transform: translateY(-50%);
          color: rgba(239, 68, 68, 0.15);
          font-size: 20px;
          text-align: center;
          letter-spacing: 25px;
          animation: flow-right 4s linear infinite;
          pointer-events: none;
        }

        /* Animations */
        @keyframes flow-right {
          0% { background-position-x: 0; }
          100% { background-position-x: 80px; }
        }

        /* Custom Scrollbar */
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(75, 85, 99, 0.3);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(107, 114, 128, 0.8);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(156, 163, 175, 0.9);
        }
      `}</style>
    </div>
  );
};

export default DraftTool;