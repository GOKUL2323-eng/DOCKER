console.log("[SYSTEM]: Shadow Architecture V3.1 - Visual Materialization Protocols Engaged.");
const API_BASE = window.location.origin;

// Application State Management
window.state = {
    token: localStorage.getItem('shadow_token'),
    user: localStorage.getItem('shadow_user'),
    currentSessionId: null,
    voiceEnabled: localStorage.getItem('shadow_voice') === 'true',
    listening: false,
    selectedImageData: null,
    preferredLang: localStorage.getItem('shadow_lang') || 'en-US',
    responseMode: localStorage.getItem('shadow_response_mode') || 'shadow',
    preferredModel: localStorage.getItem('shadow_preferred_model') || 'auto',
    globalVectors: [
        { code: 'en-US', name: 'English (US)' },
        { code: 'ta-IN', name: 'Tamil (இந்தியா)' },
        { code: 'hi-IN', name: 'Hindi (हिन्दी)' },
        { code: 'te-IN', name: 'Telugu (తెలుగు)' },
        { code: 'kn-IN', name: 'Kannada (ಕನ್ನಡ)' },
        { code: 'ml-IN', name: 'Malayalam (മലയാളം)' },
        { code: 'bn-IN', name: 'Bengali (বাংলা)' },
        { code: 'mr-IN', name: 'Marathi (मराठी)' },
        { code: 'gu-IN', name: 'Gujarati (ગુજરાતી)' },
        { code: 'pa-IN', name: 'Punjabi (ਪੰਜਾਬੀ)' },
        { code: 'ja-JP', name: 'Japanese (日本語)' },
        { code: 'ko-KR', name: 'Korean (한국어)' },
        { code: 'zh-CN', name: 'Chinese (简体中文)' },
        { code: 'fr-FR', name: 'French (Français)' },
        { code: 'es-ES', name: 'Spanish (Español)' },
        { code: 'de-DE', name: 'German (Deutsch)' },
        { code: 'it-IT', name: 'Italian (Italiano)' },
        { code: 'pt-BR', name: 'Portuguese (Português)' },
        { code: 'ru-RU', name: 'Russian (Русский)' },
        { code: 'ar-SA', name: 'Arabic (العربية)' },
        { code: 'tr-TR', name: 'Turkish (Türkçe)' },
        { code: 'vi-VN', name: 'Vietnamese (Tiếng Việt)' },
        { code: 'th-TH', name: 'Thai (ไทย)' },
        { code: 'id-ID', name: 'Indonesian (Bahasa)' },
        { code: 'nl-NL', name: 'Dutch (Nederlands)' },
        { code: 'pl-PL', name: 'Polish (Polski)' },
        { code: 'sv-SE', name: 'Swedish (Svenska)' },
        { code: 'da-DK', name: 'Danish (Dansk)' },
        { code: 'no-NO', name: 'Norwegian (Norsk)' },
        { code: 'fi-FI', name: 'Finnish (Suomi)' },
        { code: 'el-GR', name: 'Greek (Ελληνικά)' },
        { code: 'cs-CZ', name: 'Czech (Čeština)' },
        { code: 'hu-HU', name: 'Hungarian (Magyar)' },
        { code: 'ro-RO', name: 'Romanian (Română)' },
        { code: 'he-IL', name: 'Hebrew (עברית)' },
        { code: 'fa-IR', name: 'Persian (فارسی)' },
        { code: 'ur-PK', name: 'Urdu (اردو)' },
        { code: 'sw-KE', name: 'Swahili (Kiswahili)' },
        { code: 'zu-ZA', name: 'Zulu (isiZulu)' },
        { code: 'am-ET', name: 'Amharic (አማርኛ)' }
    ],
    // Intelligence utility to map 2-letter ISO codes to robust BCP-47 identifiers
    getBCP47: (iso) => {
        const map = {
            'ta': 'ta-IN', 'hi': 'hi-IN', 'te': 'te-IN', 'kn': 'kn-IN', 'ml': 'ml-IN',
            'bn': 'bn-IN', 'mr': 'mr-IN', 'gu': 'gu-IN', 'pa': 'pa-IN', 'ja': 'ja-JP',
            'ko': 'ko-KR', 'zh': 'zh-CN', 'fr': 'fr-FR', 'es': 'es-ES', 'de': 'de-DE',
            'it': 'it-IT', 'pt': 'pt-BR', 'ru': 'ru-RU', 'ar': 'ar-SA', 'tr': 'tr-TR',
            'vi': 'vi-VN', 'th': 'th-TH', 'id': 'id-ID', 'nl': 'nl-NL', 'pl': 'pl-PL',
            'sv': 'sv-SE', 'da': 'da-DK', 'no': 'no-NO', 'fi': 'fi-FI', 'el': 'el-GR',
            'cs': 'cs-CZ', 'hu': 'hu-HU', 'ro': 'ro-RO', 'he': 'he-IL', 'fa': 'fa-IR',
            'ur': 'ur-PK', 'sw': 'sw-KE', 'zu': 'zu-ZA', 'am': 'am-ET', 'en': 'en-US'
        };
        return map[iso.split('-')[0]] || iso;
    }
};
const state = window.state;

// View management logic
const views = {
    auth: () => `
        <div class="flex-1 flex items-center justify-center p-4 overflow-auto bg-cyber-black">
            <div class="w-full max-w-md">
                <div class="text-center mb-10 flex flex-col items-center">
                    <div class="w-24 h-24 rounded-full border border-cyber-red/40 p-1 mb-6 bg-black shadow-[0_0_30px_rgba(255,0,60,0.15)] overflow-hidden animate-float">
                        <img src="/files/assets/shadow_ninja_red.png" class="w-full h-full object-cover opacity-90 hover:opacity-100 transition-opacity" alt="Shadow AI Logo">
                    </div>
                    <h1 class="text-5xl font-orbitron font-black tracking-tighter text-cyber-blue italic mb-2 glitch-text">SHADOW AI</h1>
                    <p class="text-cyber-textSecondary tracking-[0.3em] text-[10px] uppercase font-bold opacity-80">Tier-1 Neural Interface</p>
                </div>

                <div class="cyber-panel p-10">
                    <div class="mb-8 border-b border-white/5 pb-4 flex justify-between items-end">
                        <h2 class="text-lg font-orbitron font-bold text-cyber-red uppercase tracking-widest">Auth_Protocol</h2>
                        <span class="text-[10px] text-cyber-textSecondary font-mono pb-1">UPLINK_01</span>
                    </div>
                    
                    <form id="authForm" onsubmit="handleAuth(event)" class="space-y-6">
                        <div class="space-y-2">
                            <label class="block text-[10px] uppercase tracking-[2px] text-cyber-textSecondary">Designation</label>
                            <input type="text" id="username" required 
                                class="w-full px-4 py-3 cyber-input text-sm" 
                                placeholder="OPERATIVE ID">
                        </div>

                        <div id="emailGroup" class="space-y-2 hidden">
                            <label class="block text-[10px] uppercase tracking-[2px] text-cyber-textSecondary">Neural Link (Email)</label>
                            <input type="email" id="email" 
                                class="w-full px-4 py-3 cyber-input text-sm" 
                                placeholder="NEXUS@SHADOW.NET">
                        </div>

                        <div class="space-y-2">
                            <label class="block text-[10px] uppercase tracking-[2px] text-cyber-textSecondary">Access Key</label>
                            <input type="password" id="password" required 
                                class="w-full px-4 py-3 cyber-input text-sm" 
                                placeholder="••••••••">
                        </div>

                        <button type="submit" id="authBtn" class="w-full cyber-btn h-14 mt-4">
                            INITIALIZE SYSTEM
                        </button>
                    </form>

                    <p class="mt-8 text-center">
                        <a href="#" onclick="toggleAuthMode()" id="authToggleText" class="text-[11px] text-cyber-textSecondary hover:text-cyber-blue transition-colors uppercase tracking-widest font-bold">
                            NEW_OPERATIVE? REGISTER_HERE
                        </a>
                    </p>
                    
                    <div id="authError" class="mt-6 p-4 border border-cyber-red/30 bg-cyber-red/5 text-cyber-red text-[11px] hidden uppercase tracking-wider font-bold"></div>
                    
                    <!-- <div class="social-auth-container">
                        <button onclick="handleSocialAuth('google')" class="social-btn google" title="UPLINK via GOOGLE">
                            <i class="fab fa-google"></i>
                        </button>
                        <button onclick="handleSocialAuth('facebook')" class="social-btn facebook" title="UPLINK via FACEBOOK">
                            <i class="fab fa-facebook-f"></i>
                        </button>
                        <button onclick="handleSocialAuth('github')" class="social-btn github" title="UPLINK via GITHUB">
                            <i class="fab fa-github"></i>
                        </button>
                    </div> -->
                </div>
            </div>
        </div>
    `,

    chat: () => {
        if (!state.token) {
            setTimeout(() => navigate('auth'), 0);
            return '<div class="flex items-center justify-center h-full text-cyber-blue animate-pulse uppercase tracking-widest">Redirecting to Neural Uplink...</div>';
        }
        return `
        <div class="flex-1 flex overflow-hidden bg-transparent">
            <!-- Sidebar Backdrop for mobile -->
            <div id="sidebarBackdrop" onclick="toggleSidebar(false)" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 hidden lg:hidden transition-all duration-300"></div>

            <!-- Tactical Sidebar -->
            <div id="sidebar" class="fixed inset-y-0 left-0 w-80 flex flex-col border-r border-white/5 bg-black/90 backdrop-blur-3xl p-6 transition-transform -translate-x-full lg:translate-x-0 lg:static lg:flex z-50">
                <div class="flex items-center justify-between mb-10 border-b border-white/5 pb-6">
                    <div class="flex items-center gap-4">
                        <div class="w-10 h-10 rounded-full border border-cyber-red/30 p-0.5 bg-black overflow-hidden avatar-small">
                            <img src="/files/assets/shadow_ninja_red.png" class="w-full h-full object-cover opacity-80" />
                        </div>
                        <div>
                            <div class="text-[9px] text-cyber-blue uppercase tracking-widest font-black mb-0.5">Operative_Active</div>
                            <div class="text-sm font-orbitron font-bold tracking-wider truncate max-w-[120px]">${state.user || 'OPERATIVE'}</div>
                        </div>
                    </div>
                    <button onclick="toggleSidebar(false)" class="lg:hidden p-2 text-cyber-red/50 hover:text-cyber-red">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>

                <div class="mb-4 ml-6">
                    <div id="google_translate_element" class="opacity-80 hover:opacity-100 transition-opacity"></div>
                </div>

                <div class="flex-1 overflow-y-auto space-y-4 custom-scrollbar pr-2">
                    <button onclick="startNewSession()" class="w-full flex items-center justify-between p-4 text-[10px] font-black border border-cyber-blue/20 text-cyber-blue hover:bg-cyber-blue/5 transition-all uppercase tracking-[3px] group">
                        <span>NEW_DEPLOYMENT</span>
                        <span class="group-hover:translate-x-1 transition-transform">→</span>
                    </button>
                    <div id="sessionList" class="space-y-2">
                        <!-- Sessions rendered here -->
                    </div>
                </div>

                <div class="mt-8 pt-6 border-t border-white/5 space-y-2">
                    <button onclick="showSystemCore()" class="w-full flex items-center justify-between p-3 text-[10px] uppercase font-black text-cyber-blue/60 hover:text-cyber-blue hover:bg-cyber-blue/5 transition-all tracking-widest border border-cyber-blue/10">
                        <span>SYSTEM_CORE</span>
                        <span class="animate-pulse">●</span>
                    </button>
                    <button onclick="logout()" class="w-full flex items-center justify-between p-3 text-[10px] uppercase font-black text-cyber-red/60 hover:text-cyber-red hover:bg-cyber-red/5 transition-all tracking-widest">
                        <span>TERMINATE_SESSION</span>
                        <span>[ESC]</span>
                    </button>
                </div>
            </div>

            <!-- Main Interface Grid -->
            <div class="flex-1 flex relative overflow-hidden h-full">
                <!-- Chat Window Column (Left) -->
                <div id="chatContainer" class="flex-1 flex flex-col relative h-full transition-all duration-300">
                    <!-- Mobile Header -->
                    <div class="lg:hidden flex items-center justify-between p-4 border-b border-white/5 bg-black/40 backdrop-blur-xl z-30">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full border border-cyber-red/30 p-0.5 bg-black overflow-hidden avatar-small">
                                <img src="/files/assets/shadow_ninja_red.png" class="w-full h-full object-cover opacity-80" />
                            </div>
                            <h1 class="text-sm font-orbitron font-black tracking-widest text-cyber-blue">SHADOW_AI</h1>
                        </div>
                        <button onclick="toggleSidebar()" class="px-4 py-2 border border-cyber-blue/30 text-[10px] font-black tracking-[2px] text-cyber-blue bg-cyber-blue/5 hover:bg-cyber-blue/10 transition-all uppercase">
                            HISTORY
                        </button>
                    </div>

                    <!-- Data Stream -->
                    <div id="chatWindow" class="flex-1 overflow-y-auto p-4 md:p-10 space-y-8 custom-scrollbar pb-44 bg-transparent">
                        <div class="flex gap-4 w-full md:w-3/4 animate-float">
                            <div class="w-10 h-10 rounded-full border border-cyber-red/20 bg-black flex-shrink-0 flex items-center justify-center overflow-hidden avatar-small">
                                <img src="/files/assets/shadow_ninja_red.png" class="w-7 h-7 object-contain opacity-50" />
                            </div>
                            <div class="cyber-panel p-5 flex-1">
                                <div class="flex justify-between items-center mb-2">
                                    <p class="text-cyber-red font-orbitron text-[9px] uppercase tracking-[3px] font-black">System_Broadcast</p>
                                    <span class="text-[8px] text-white/20 font-mono">NODE_01</span>
                                </div>
                                <div class="text-sm text-cyber-textPrimary/80 leading-relaxed font-medium">Uplink established. Shadow AI initialized. Protocols active. Ready for tactical support, operative.</div>
                            </div>
                        </div>
                    </div>

                    <!-- Control Console -->
                    <div class="absolute bottom-0 left-0 w-full p-4 md:p-10 bg-gradient-to-t from-cyber-black via-cyber-black/90 to-transparent z-30">
                        <div class="max-w-5xl mx-auto">
                            <!-- Status Bar -->
                            <div class="flex flex-wrap gap-4 justify-between items-center mb-4 px-2 bg-black/60 p-2 border border-white/5 rounded backdrop-blur-md">
                                <div class="flex gap-4">
                                    <div class="text-[9px] text-cyber-textSecondary flex items-center gap-2 tracking-widest">
                                        <span class="w-1.5 h-1.5 bg-cyber-red rounded-full animate-pulse"></span>
                                        SYSTEM_STABLE
                                    </div>
                                    <div class="text-[9px] text-cyber-textSecondary flex items-center gap-2 tracking-widest hidden md:flex">
                                        <span class="w-1.5 h-1.5 bg-white/20 rounded-full"></span>
                                        SEC_LEVEL_IV
                                    </div>
                                    <div class="text-[9px] text-cyber-textSecondary flex items-center gap-2 tracking-widest">
                                        CORE_LINK:
                                        <select id="modelSelect" onchange="changeModel(this.value)" class="bg-cyber-dark text-cyber-blue border border-white/10 text-[9px] uppercase tracking-widest font-black focus:outline-none cursor-pointer p-0.5 rounded">
                                            <option value="auto" ${window.state.preferredModel === 'auto' || !window.state.preferredModel ? 'selected' : ''}>AUTO (FALLBACK)</option>
                                            <option value="openai" ${window.state.preferredModel === 'openai' ? 'selected' : ''}>GPT-4o (OPENAI)</option>
                                            <option value="groq" ${window.state.preferredModel === 'groq' ? 'selected' : ''}>LLAMA-3.3 (GROQ)</option>
                                            <option value="gemini" ${window.state.preferredModel === 'gemini' ? 'selected' : ''}>GEMINI-1.5 (PRO)</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="flex items-center gap-4">
                                    <button onclick="toggleResponseMode()" id="responseModeToggle" class="text-[9px] uppercase tracking-widest text-cyber-textSecondary hover:text-cyber-blue transition-colors font-black">
                                        RESPONSE: <span id="responseModeStatus" class="${window.state.responseMode === 'direct' ? 'text-cyber-blue' : 'text-cyber-red'}">${window.state.responseMode === 'direct' ? 'DIRECT' : 'SHADOW'}</span>
                                    </button>
                                    <div class="text-[9px] text-cyber-textSecondary flex items-center gap-2 tracking-widest uppercase hidden sm:flex">
                                        PROTOCOL: <button onclick="showLanguageSelector()" id="activeLang" class="text-cyber-blue font-black hover:underline underline-offset-4 decoration-cyber-blue/30">${window.state.preferredLang || 'EN-US'}</button>
                                    </div>
                                    <button onclick="toggleVoice()" id="voiceToggle" class="text-[9px] uppercase tracking-widest text-cyber-textSecondary hover:text-cyber-blue transition-colors font-black">
                                        VOICE_FEED: <span id="voiceStatus" class="text-cyber-red">${window.state.voiceEnabled ? 'ON' : 'OFF'}</span>
                                    </button>
                                </div>
                            </div>

                            <div class="relative group">
                                <!-- Payload Preview -->
                                <div id="imagePreviewContainer" class="absolute bottom-full left-0 mb-4 hidden animate-float">
                                    <div class="relative group">
                                        <img id="imagePreview" src="" class="h-24 rounded border border-cyber-blue/30 shadow-2xl">
                                        <button onclick="clearImage()" class="absolute -top-2 -right-2 w-6 h-6 bg-cyber-red text-white flex items-center justify-center text-[11px] rounded transition-transform hover:scale-110">✕</button>
                                    </div>
                                </div>
                                <div class="flex items-end gap-2 bg-cyber-dark/80 backdrop-blur-xl border border-white/5 p-3 md:p-4 rounded-lg focus-within:border-cyber-blue/30 transition-all shadow-2xl w-full">
                                    <button onclick="document.getElementById('imageInput').click()" class="mb-1 p-2 text-cyber-textSecondary hover:text-cyber-blue hover:bg-cyber-blue/5 rounded transition-all flex-shrink-0" title="Attach Payload">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"></path></svg>
                                    </button>
                                    
                                    <input type="file" id="imageInput" class="hidden" accept="image/*,.txt,.js,.py,.html,.css,.json,.md,.csv,.log,.sh" onchange="handleImageSelect(event)">
                                    
                                    <textarea id="chatInput" rows="1" placeholder="ENTER_COMMAND..." 
                                        class="flex-1 bg-transparent border-none focus:ring-0 text-white font-rajdhani text-lg resize-none min-h-[44px] max-h-48 py-2 custom-scrollbar placeholder:text-white/10" 
                                        onkeydown="handleKeydown(event)" 
                                        oninput="autoScaleTextarea(this)"></textarea>
                                    <button onclick="handleSendMessage()" id="sendBtn" class="mb-1 flex items-center justify-center h-11 w-12 rounded bg-cyber-red text-black hover:bg-white hover:shadow-[0_0_30px_#ff003c] transition-all group">
                                        <svg class="w-5 h-5 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 5l7 7-7 7M5 5l7 7-7 7"></path></svg>
                                    </button>
                                    
                                    <button onclick="toggleMicrophone()" id="micBtn" class="mb-1 flex items-center justify-center h-11 w-12 rounded border border-cyber-blue/30 text-cyber-blue hover:bg-cyber-blue/5 transition-all">
                                        <svg id="micIcon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </div>
        `;
    }
};

// Auto Scale Textarea
function autoScaleTextarea(el) {
    el.style.height = 'auto';
    el.style.height = (el.scrollHeight) + 'px';
}

// System Core Modal (Team/Credits)
function showSystemCore() {
    const modal = document.createElement('div');
    modal.className = 'cyber-modal-overlay';
    modal.innerHTML = `
        <div class="cyber-modal max-w-2xl">
            <div class="p-8">
                <div class="flex justify-between items-center mb-8 border-b border-cyber-blue/20 pb-4">
                    <div>
                        <h2 class="text-2xl font-orbitron font-black text-cyber-blue tracking-tighter italic">NEURAL_CORE_v3.1</h2>
                        <p class="text-[10px] uppercase tracking-[4px] text-cyber-textSecondary opacity-70">Architecture & Intelligence Synthesis</p>
                    </div>
                    <button onclick="this.closest('.cyber-modal-overlay').remove()" class="text-cyber-red/50 hover:text-cyber-red p-2 transition-colors">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <!-- Founder: Gokul -->
                    <div class="founder-card p-6 border border-white/5 bg-black/40 relative group overflow-hidden">
                        <div class="absolute top-0 left-0 w-1 h-full bg-cyber-blue scale-y-0 group-hover:scale-y-100 transition-transform origin-top duration-500"></div>
                        <div class="flex items-center gap-4 mb-4">
                            <div class="w-12 h-12 rounded border border-cyber-blue/30 p-0.5 bg-black overflow-hidden avatar-small">
                                <img src="/files/assets/shadow_ninja_red.png" class="w-full h-full object-cover opacity-80" />
                            </div>
                            <div>
                                <h3 class="text-sm font-orbitron font-bold text-white tracking-widest uppercase">Gokul P.</h3>
                                <p class="text-[8px] text-cyber-blue uppercase font-black tracking-widest">Founder / Visionary</p>
                            </div>
                        </div>
                        <div class="space-y-2 text-[11px] leading-relaxed text-cyber-textSecondary">
                            <p class="flex gap-2">
                                <span class="text-cyber-blue/40 font-mono">U_ID:</span>
                                <span>Takshashila University</span>
                            </p>
                            <p class="flex gap-2">
                                <span class="text-cyber-blue/40 font-mono">SPEC:</span>
                                <span>B.Sc AI/ML</span>
                            </p>
                            <p class="flex gap-2">
                                <span class="text-cyber-blue/40 font-mono">LOC:</span>
                                <span>Tamil Nadu, India</span>
                            </p>
                        </div>
                        <div class="mt-4 pt-4 border-t border-white/5 text-[9px] text-white/30 italic">
                            Primary operative responsible for initial synthesis and core matrix logic.
                        </div>
                    </div>

                    <!-- Founder: Balaji MJ -->
                    <div class="founder-card p-6 border border-white/5 bg-black/40 relative group overflow-hidden">
                        <div class="absolute top-0 left-0 w-1 h-full bg-cyber-red scale-y-0 group-hover:scale-y-100 transition-transform origin-top duration-500"></div>
                        <div class="flex items-center gap-4 mb-4">
                            <div class="w-12 h-12 rounded border border-cyber-red/30 p-0.5 bg-black overflow-hidden avatar-small">
                                <img src="/files/assets/shadow_ninja_red.png" class="w-full h-full object-cover opacity-80 filter hue-rotate-[180deg]" />
                            </div>
                            <div>
                                <h3 class="text-sm font-orbitron font-bold text-white tracking-widest uppercase">Balaji MJ</h3>
                                <p class="text-[8px] text-cyber-red uppercase font-black tracking-widest">Cofounder / Designer</p>
                            </div>
                        </div>
                        <div class="space-y-2 text-[11px] leading-relaxed text-cyber-textSecondary">
                            <p class="flex gap-2">
                                <span class="text-cyber-red/40 font-mono">U_ID:</span>
                                <span>Takshashila University</span>
                            </p>
                            <p class="flex gap-2">
                                <span class="text-cyber-red/40 font-mono">SPEC:</span>
                                <span>B.Sc AI/ML</span>
                            </p>
                            <p class="flex gap-2">
                                <span class="text-cyber-red/40 font-mono">LOC:</span>
                                <span>Tamil Nadu, India</span>
                            </p>
                        </div>
                        <div class="mt-4 pt-4 border-t border-white/5 text-[9px] text-white/30 italic">
                            Creative architect behind the tactile interface and cognitive visual design.
                        </div>
                    </div>
                </div>

                <div class="mt-8 grid grid-cols-3 gap-4 border-t border-white/5 pt-8 text-center">
                    <div>
                        <div class="text-[9px] text-cyber-textSecondary uppercase tracking-widest mb-1">Architecture</div>
                        <div class="text-xs font-orbitron font-black text-cyber-blue">NEURAL_V3.1</div>
                    </div>
                    <div>
                        <div class="text-[9px] text-cyber-textSecondary uppercase tracking-widest mb-1">Uptime</div>
                        <div class="text-xs font-orbitron font-black text-cyber-blue">99.98%</div>
                    </div>
                    <div>
                        <div class="text-[9px] text-cyber-textSecondary uppercase tracking-widest mb-1">Synapse</div>
                        <div class="text-xs font-orbitron font-black text-cyber-blue">ACTIVE</div>
                    </div>
                </div>
            </div>
            
            <div class="bg-black/80 p-4 border-t border-white/5 flex justify-between items-center px-8">
                <span class="text-[8px] text-white/20 font-mono uppercase tracking-widest">Takshashila_NeuralLink_Established</span>
                <span class="text-[8px] text-cyber-red font-mono animate-glitch">ENCRYPTED_UPLINK</span>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });
}

// Navigation
function navigate(viewName) {
    const app = document.getElementById('app');
    if (views[viewName]) {
        app.innerHTML = views[viewName]();
        
        // Post-render init
        if (viewName === 'chat') {
            fetchSessions();
            // Re-initialize Google Translate if needed
            if (typeof google !== 'undefined' && google.translate && google.translate.TranslateElement) {
                new google.translate.TranslateElement({pageLanguage: 'en'}, 'google_translate_element');
            }
        }
    }
}

// Neural Matrix Animation
function initNeuralMatrix() {
    const canvas = document.getElementById('neuralMatrix');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    const chars = '01ABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%&*+=-';
    const fontSize = 14;
    const columns = Math.floor(width / fontSize);
    const drops = new Array(columns).fill(height);

    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
        ctx.fillRect(0, 0, width, height);

        ctx.fillStyle = '#00ff9d';
        ctx.font = `bold ${fontSize}px Rajdhani`;

        for (let i = 0; i < drops.length; i++) {
            const text = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);

            if (drops[i] * fontSize > height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }

    window.addEventListener('resize', () => {
        const oldColumns = columns;
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        const newColumns = Math.floor(width / fontSize);
        
        if (newColumns > oldColumns) {
            for (let i = oldColumns; i < newColumns; i++) {
                drops[i] = Math.random() * height / fontSize;
            }
        } else {
            drops.length = newColumns;
        }
    });

    setInterval(draw, 33);
}

// Global Initialization
window.addEventListener('DOMContentLoaded', () => {
    initNeuralMatrix();
    if (state.token) {
        navigate('chat');
    } else {
        navigate('auth');
    }
});


function triggerGlitch() {
    const app = document.getElementById('app');
    if (app) {
        app.classList.add('glitch-active');
        setTimeout(() => app.classList.remove('glitch-active'), 300);
    }
}

async function handleSocialAuth(provider) {
    const authError = document.getElementById('authError');
    if (authError) authError.classList.add('hidden');
    
    // Redirect to backend OAuth initiation endpoint
    window.location.href = `/auth/login/${provider}`;
}


