// Shadow v2.0 Tactical Chat Logic

function startNewSession() {
    state.currentSessionId = null;
    state.selectedImageData = null; 
    const chatWindow = document.getElementById('chatWindow');
    if (chatWindow) {
        chatWindow.innerHTML = `
            <div class="flex gap-4 w-full md:w-3/4 animate-float">
                <div class="w-10 h-10 rounded-full border border-cyber-red/30 bg-black flex-shrink-0 flex items-center justify-center overflow-hidden avatar-small">
                    <img src="/files/assets/shadow_ninja_red.png" class="w-7 h-7 object-contain opacity-50" />
                </div>
                <div class="cyber-panel p-5 flex-1">
                    <div class="flex justify-between items-center mb-2">
                        <p class="text-cyber-red font-orbitron text-[9px] uppercase tracking-[3px] font-black">System_Broadcast</p>
                        <span class="text-[8px] text-white/20 font-mono">NODE_01</span>
                    </div>
                    <div class="text-sm text-cyber-textPrimary/80 leading-relaxed font-bold">New operational thread initialized. State your objective, operative.</div>
                </div>
            </div>
        `;
    }
    clearImage();
    
    // Auto-close sidebar on mobile after selecting new session
    if (window.innerWidth < 1024) {
        toggleSidebar(false);
    }
}

async function fetchSessions() {
    const sessionList = document.getElementById('sessionList');
    if (!sessionList) return;

    try {
        const res = await fetch(`${API_BASE}/api/chat/sessions`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        if (!res.ok) throw new Error("FETCH_FAILED");

        const sessions = await res.json();
        sessionList.innerHTML = sessions.map(s => `
            <div onclick="selectSession('${s.id}')" class="group cursor-pointer p-4 border border-white/5 bg-white/5 hover:bg-cyber-blue/5 hover:border-cyber-blue/20 transition-all relative overflow-hidden">
                <div class="absolute left-0 top-0 w-0.5 h-full bg-cyber-blue opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div class="text-[10px] text-cyber-blue/50 font-black uppercase tracking-widest mb-1">${new Date(s.updated_at).toLocaleDateString()}</div>
                <div class="text-xs font-bold text-cyber-textPrimary truncate">${s.title || 'NULL_SUBJECT'}</div>
            </div>
        `).join('');
    } catch (err) {
        sessionList.innerHTML = `<div class="text-[9px] text-cyber-red/50 uppercase font-black text-center p-4">Uplink_Error: ${err.message}</div>`;
    }
}

function selectSession(id) {
    loadSession(id);
    if (window.innerWidth < 1024) {
        toggleSidebar(false);
    }
}

function toggleSidebar(force = null) {
    const sidebar = document.getElementById('sidebar');
    const backdrop = document.getElementById('sidebarBackdrop');
    if (!sidebar) return;

    const isActive = force !== null ? force : !sidebar.classList.contains('sidebar-active');
    
    if (isActive) {
        sidebar.classList.add('sidebar-active');
        if (backdrop) backdrop.classList.remove('hidden');
    } else {
        sidebar.classList.remove('sidebar-active');
        if (backdrop) backdrop.classList.add('hidden');
    }
}

async function loadSession(sessionId) {
    state.currentSessionId = sessionId;
    const chatWindow = document.getElementById('chatWindow');
    if (!chatWindow) return;

    chatWindow.innerHTML = `
        <div class="flex flex-col items-center justify-center py-20 gap-4">
            <div class="w-12 h-12 border-2 border-cyber-red/20 border-t-cyber-red rounded-full animate-spin"></div>
            <div class="text-[10px] text-cyber-red font-black uppercase tracking-[4px] animate-pulse">Accessing_Neural_Archives...</div>
        </div>
    `;

    try {
        const res = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        if (!res.ok) throw new Error("ACCESS_DENIED");

        const data = await res.json();
        chatWindow.innerHTML = '';
        data.messages.forEach(msg => appendMessage(msg.role, msg.content));
        scrollToBottom();
    } catch (err) {
        chatWindow.innerHTML = `<div class="cyber-panel p-6 border-cyber-red text-cyber-red text-xs font-black uppercase tracking-widest text-center">ARCHIVE_CORRUPTED: ${err.message}</div>`;
    }
}

function appendMessage(role, content, isStreaming = false) {
    const chatWindow = document.getElementById('chatWindow');
    if (!chatWindow) return;

    // Use existing streaming bubble if it belongs to the assistant and we are streaming
    if (isStreaming && role === 'assistant') {
        const lastMsg = chatWindow.lastElementChild;
        if (lastMsg && lastMsg.dataset.role === 'assistant' && lastMsg.dataset.streaming === 'true') {
            const contentDiv = lastMsg.querySelector('.message-content');
            if (contentDiv) {
                lastMsg.dataset.rawContent += content;
                contentDiv.innerHTML = formatAIResponse(lastMsg.dataset.rawContent);
                return lastMsg;
            }
        }
    }

    const div = document.createElement('div');
    const isUser = role === 'user';
    div.className = `flex gap-4 w-full ${isUser ? 'flex-row-reverse md:pl-20' : 'md:pr-20'} animate-float group`;
    div.dataset.role = role;
    if (isStreaming) {
        div.dataset.streaming = 'true';
        div.dataset.rawContent = content;
    }

    const panelClass = isUser ? 'cyber-panel-red' : 'cyber-panel';
    const accentColor = isUser ? 'text-cyber-blue' : 'text-cyber-red';
    const label = isUser ? 'OPERATIVE' : 'SHADOW_AI';

    div.innerHTML = `
        <div class="w-10 h-10 rounded-full border border-cyber-red/30 bg-black flex-shrink-0 flex items-center justify-center font-orbitron font-black text-[10px] ${accentColor} overflow-hidden avatar-small">
            ${isUser ? 'OP' : `<img src="/files/assets/shadow_ninja_red.png" class="w-full h-full object-cover p-1 opacity-80" />`}
        </div>
        <div class="${panelClass} p-5 flex-1 relative min-w-0">
            <div class="flex justify-between items-center mb-3 border-b border-white/5 pb-2">
                <p class="${accentColor} font-orbitron text-[9px] uppercase tracking-[3px] font-black">${label}</p>
                <span class="text-[8px] text-white/10 font-mono uppercase">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}</span>
            </div>
            <div class="text-sm text-cyber-textPrimary leading-relaxed prose prose-invert max-w-none message-content">
                ${state.selectedImageData && isUser ? `<img src="data:image/jpeg;base64,${state.selectedImageData}" class="max-w-sm mb-4 rounded border border-cyber-red/30 shadow-2xl" />` : ''}
                ${formatAIResponse(content)}
            </div>
        </div>
    `;

    chatWindow.appendChild(div);
    return div;
}

function appendTypingIndicator() {
    const chatWindow = document.getElementById('chatWindow');
    const div = document.createElement('div');
    div.id = 'typingIndicator';
    div.className = "flex gap-4 w-full md:w-1/2 animate-float";
    div.innerHTML = `
        <div class="w-10 h-10 rounded-full border border-cyber-red/30 bg-black flex-shrink-0 flex items-center justify-center overflow-hidden avatar-small">
            <img src="/files/assets/shadow_ninja_red.png" class="w-7 h-7 object-contain opacity-30" />
        </div>
        <div class="cyber-panel p-5 flex-1 flex gap-2 items-center h-14">
            <div class="w-2 h-2 rounded-full bg-cyber-red/40 typing-dot"></div>
            <div class="w-2 h-2 rounded-full bg-cyber-red/60 typing-dot"></div>
            <div class="w-2 h-2 rounded-full bg-cyber-red typing-dot"></div>
            <span class="ml-4 text-[9px] text-cyber-red/40 font-black uppercase tracking-[3px]">Analyzing_Matrix...</span>
        </div>
    `;
    chatWindow.appendChild(div);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

function scrollToBottom() {
    const chatWindow = document.getElementById('chatWindow');
    if (chatWindow) {
        chatWindow.scrollTo({ top: chatWindow.scrollHeight, behavior: 'smooth' });
    }
}

async function handleSendMessage(event) {
    if (event && typeof event.preventDefault === 'function') event.preventDefault();
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    input.style.height = 'auto';

    appendMessage('user', message);
    if (window.triggerGlitch) window.triggerGlitch();
    scrollToBottom();
    appendTypingIndicator();

        // Visual feedback
        const avatar = document.getElementById('chatAvatar');
        if (avatar) avatar.classList.add('speaking-glow');

        try {
            const payload = {
                message: message,
                image_data: state.selectedImageData ? state.selectedImageData.split(',')[1] : null,
                response_mode: state.responseMode || 'direct',
                preferred_model: state.preferredModel || 'auto'
            };

            if (state.selectedFileText) {
                payload.message = `[ATTACHED_FILE: ${state.selectedFileText.name}]\n\`\`\`\n${state.selectedFileText.content}\n\`\`\`\n\n${payload.message}`;
            }

            // session_id is handled in the URL query param for send_message endpoint

        const tempImgData = state.selectedImageData;
        state.selectedImageData = null;
        state.selectedFileText = null;
        clearImage();

        const responseFlow = await fetch(`${API_BASE}/api/chat/message?session_id=${state.currentSessionId || ''}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify(payload)
        });

        if (responseFlow.status === 401) { logout(); return; }
        if (!responseFlow.ok) throw new Error("UPLINK_FAILURE");

        removeTypingIndicator();
        
        // Process SSE Stream
        const reader = responseFlow.body.getReader();
        const decoder = new TextDecoder();
        let fullReply = "";
        
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            const chunkText = decoder.decode(value);
            const lines = chunkText.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.substring(6));
                        if (data.chunk) {
                            fullReply += data.chunk;
                            appendMessage('assistant', data.chunk, true);
                            scrollToBottom();
                        }
                        if (data.session_id && !state.currentSessionId) {
                            state.currentSessionId = data.session_id;
                        }
                    } catch (e) {
                        console.warn("MALFORMED_STREAM_CHUNK", e);
                    }
                }
            }
        }

        if (window.triggerGlitch) window.triggerGlitch();
        
        // Finalize metadata (lang detection could be improved but we use default/manual for speed)
        if (state.voiceEnabled) speakResponse(fullReply, state.preferredLang);

    } catch (err) {
        removeTypingIndicator();
        appendMessage('assistant', `[PROTOCOL_INTERRUPT]: Uplink failure. Diagnostic: ${err.message}`);
    } finally {
        if (avatar) avatar.classList.remove('speaking-glow');
        scrollToBottom();
    }
}

function updateVoiceBtnUI() {
    const btn = document.getElementById('voiceToggleBtn');
    const icon = document.getElementById('voiceIcon');
    if (!btn) return;

    if (state.voiceEnabled) {
        btn.className = "mb-1 flex items-center justify-center h-11 w-12 rounded border border-cyber-blue/30 text-cyber-blue hover:bg-cyber-blue/5 transition-all";
        if (icon) {
            icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path>`;
        }
    } else {
        btn.className = "mb-1 flex items-center justify-center h-11 w-12 rounded border border-cyber-red/30 text-cyber-red hover:bg-cyber-red/5 transition-all";
        if (icon) {
            icon.innerHTML = `<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"></path>
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"></path>`;
        }
    }
}

function toggleVoice() {
    state.voiceEnabled = !state.voiceEnabled;
    localStorage.setItem('shadow_voice', state.voiceEnabled);
    updateVoiceBtnUI();
    if (!state.voiceEnabled) window.speechSynthesis.cancel();
}

function toggleResponseMode() {
    state.responseMode = state.responseMode === 'direct' ? 'shadow' : 'direct';
    localStorage.setItem('shadow_response_mode', state.responseMode);
    const status = document.getElementById('responseModeStatus');
    if (status) {
        status.innerText = state.responseMode === 'direct' ? 'DIRECT' : 'SHADOW';
        status.className = state.responseMode === 'direct' ? 'text-cyber-blue' : 'text-cyber-red';
    }
}

async function speakResponse(text, lang) {
    const cleanText = text.replace(/[*#`_\[\]()]/g, '').replace(/!\[.*?\]\(.*?\)/g, '');
    if (!cleanText) return;

    // Fast Fallback Protocol: Trigger standard voice if neural takes too long
    let neuralStarted = false;
    const fallbackTimeout = setTimeout(() => {
        if (!neuralStarted) {
            console.log("[VOICE_SYSTEM]: Optimistic fallback triggered.");
            speakFallback(cleanText, lang);
        }
    }, 450); // Improved timeout for better perceived speed

    try {
        const response = await fetch(`${API_BASE}/api/chat/tts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({ text: cleanText, lang: lang || 'en-US' })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.audioContent) {
                clearTimeout(fallbackTimeout);
                if (window.speechSynthesis) window.speechSynthesis.cancel();
                neuralStarted = true;
                const audio = new Audio(`data:audio/mp3;base64,${data.audioContent}`);
                audio.play();
                return;
            }
        }
    } catch (err) {
        // Fallback already handled by timeout
    }
}

function speakFallback(cleanText, lang) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = lang || 'en';
    
    const voices = window.speechSynthesis.getVoices();
    const targetLangPrefix = (lang || 'en').toLowerCase().split('-')[0];
    
    let validVoices = voices.filter(v => {
        const vLang = v.lang.toLowerCase();
        return vLang.startsWith(targetLangPrefix) || vLang.includes(targetLangPrefix);
    });

    if (validVoices.length === 0) validVoices = voices;

    const targetVoice = validVoices.sort((a, b) => {
        const aName = a.name.toLowerCase();
        const bName = b.name.toLowerCase();
        const aPriority = aName.includes('neural') || aName.includes('google');
        const bPriority = bName.includes('neural') || bName.includes('google');
        return bPriority - aPriority;
    })[0] || voices[0];
    
    if (targetVoice) utterance.voice = targetVoice;
    window.speechSynthesis.speak(utterance);
}

function formatAIResponse(str) {
    if (typeof marked === 'undefined') return str;
    
    const renderer = new marked.Renderer();
    
    renderer.code = (code, lang) => {
        const encodedCode = btoa(unescape(encodeURIComponent(code)));
        const langClass = lang ? `language-${lang}` : '';
        const displayLang = lang ? lang.toUpperCase() : 'CODE';
        
        return `
            <div class="code-block-container relative group my-4 border border-white/5 bg-black/40 rounded">
                <div class="flex justify-between items-center px-4 py-2 border-b border-white/5 bg-black/20 text-[9px] uppercase font-black text-cyber-textSecondary">
                    <span>${displayLang}</span>
                    <button onclick="loadCodeIntoWorkspace('${encodedCode}', '${lang || 'python'}')" class="text-cyber-blue hover:text-white transition-colors cursor-pointer select-none">
                        LOAD_INTO_WORKSPACE
                    </button>
                </div>
                <pre class="${langClass} p-4 overflow-x-auto text-sm"><code class="${langClass}">${code}</code></pre>
            </div>
        `;
    };

    renderer.image = (href, title, text) => {
        return `
            <div class="mt-4 tactical-image-container group">
                <img src="${href}" alt="${text}" title="${title || ''}" 
                    class="rounded border border-cyber-red/30 shadow-[0_0_20px_rgba(255,0,60,0.1)] max-w-full h-auto transition-all hover:border-cyber-red/60"
                    onload="this.parentElement.classList.remove('animate-pulse')"
                    onerror="this.parentElement.innerHTML='<div class=\"p-4 border border-cyber-red/30 bg-cyber-red/5 text-cyber-red text-[10px] uppercase font-black\">Visual_Link_Severed: ORB_Interception</div>'">
                <div class="mt-2 flex justify-between items-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <span class="text-[8px] text-cyber-red/40 uppercase tracking-widest font-black">Visual_Construct [RAW_DATA]</span>
                    <a href="${href}" target="_blank" class="text-[8px] text-cyber-red hover:underline uppercase font-black">Open_Full_Resolution</a>
                </div>
            </div>
        `;
    };

    marked.setOptions({
        renderer: renderer,
        highlight: (code, lang) => Prism.languages[lang] ? Prism.highlight(code, Prism.languages[lang], lang) : code,
        breaks: true,
        gfm: true
    });
    return marked.parse(str);
}

function handleImageSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = e => {
            state.selectedImageData = e.target.result;
            state.selectedFileText = null;
            const preview = document.getElementById('imagePreview');
            const container = document.getElementById('imagePreviewContainer');
            if (preview && container) {
                preview.src = e.target.result;
                preview.title = '';
                container.classList.remove('hidden');
            }
        };
        reader.readAsDataURL(file);
    } else {
        // Document/Code format
        const reader = new FileReader();
        reader.onload = e => {
            state.selectedFileText = {
                name: file.name,
                content: e.target.result
            };
            state.selectedImageData = null;
            
            const preview = document.getElementById('imagePreview');
            const container = document.getElementById('imagePreviewContainer');
            if (preview && container) {
                // Generate tactical Document SVG Icon
                const svgIcon = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="%2300ff9d" stroke-width="1"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`;
                preview.src = svgIcon;
                preview.title = file.name;
                container.classList.remove('hidden');
            }
        };
        reader.readAsText(file);
    }
}

function clearImage() {
    state.selectedImageData = null;
    state.selectedFileText = null;
    const preview = document.getElementById('imagePreview');
    const container = document.getElementById('imagePreviewContainer');
    const input = document.getElementById('imageInput');
    if (preview) { preview.src = ''; preview.title = ''; }
    if (container) container.classList.add('hidden');
    if (input) input.value = '';
}

function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSendMessage();
    }
}

function quickAction(command) {
    const input = document.getElementById('chatInput');
    if (input) {
        input.value = command;
        handleSendMessage();
    }
}

// Protocol Alpha: Voice Command Interface (STT)
let recognition = null;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = state.getBCP47(state.preferredLang || 'en-US'); // Dynamic language uplink

    recognition.onstart = () => {
        state.listening = true;
        updateMicUI();
    };

    recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
            .map(result => result[0])
            .map(result => result.transcript)
            .join('');
        
        const input = document.getElementById('chatInput');
        if (input) {
            input.value = transcript;
            autoScaleTextarea(input);
        }
    };

    recognition.onerror = (event) => {
        console.error('[PROTOCOL_ERROR]: Voice Uplink Failure:', event.error);
        stopListening();
    };

    recognition.onend = () => {
        if (state.listening) {
            const input = document.getElementById('chatInput');
            if (input && input.value.trim()) {
                handleSendMessage();
            }
        }
        stopListening();
    };
}

function toggleMicrophone() {
    if (!recognition) {
        appendMessage('assistant', '[SYSTEM_ERROR]: Voice uplink hardware not detected by this browser.');
        return;
    }
    if (state.listening) {
        stopListening();
    } else {
        startListening();
    }
}

function startListening() {
    if (!recognition) return;
    try {
        // Synchronize with the latest Neural Protocol via global mapper
        recognition.lang = state.getBCP47(state.preferredLang || 'en-US');
        recognition.start();
    } catch (e) {
        console.warn('Recognition already active');
    }
}

function stopListening() {
    state.listening = false;
    if (recognition) recognition.stop();
    updateMicUI();
}

function showLanguageSelector() {
    const overlay = document.createElement('div');
    overlay.className = 'cyber-modal-overlay';
    overlay.id = 'langSelectorOverlay';
    overlay.onclick = (e) => { if(e.target === overlay) closeLanguageSelector(); };

    const modal = document.createElement('div');
    modal.className = 'cyber-modal';
    
    let langOptions = state.globalVectors.map(v => `
        <div onclick="selectLanguageVector('${v.code}')" class="lang-opt ${state.preferredLang === v.code ? 'active' : ''}">
            <span class="code">${v.code}</span>
            <span class="name">${v.name}</span>
        </div>
    `).join('');

    modal.innerHTML = `
        <div class="p-6 border-b border-white/5 bg-black/40 flex justify-between items-center">
            <h3 class="text-sm font-orbitron font-black text-cyber-blue uppercase tracking-[3px]">Select_Neural_Protocol</h3>
            <button onclick="closeLanguageSelector()" class="text-cyber-red/50 hover:text-cyber-red">✕</button>
        </div>
        <input type="text" id="langSearch" placeholder="SEARCH NEURAL VECTORS (E.G. TAMIL, HINDI, JAPANESE)..." 
               class="cyber-search-input" oninput="filterLanguages(this.value)">
        <div class="lang-grid" id="langGrid">
            ${langOptions}
        </div>
        <div class="p-4 bg-cyber-red/5 border-t border-white/5 text-[9px] text-cyber-textSecondary uppercase tracking-widest text-center px-10">
            Note: SHADOW will prioritize the selected vector for input recognition and speech synthesis.
        </div>
    `;

    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    setTimeout(() => document.getElementById('langSearch')?.focus(), 100);
}

function filterLanguages(query) {
    const grid = document.getElementById('langGrid');
    const q = query.toLowerCase().trim();
    
    let filteredHtml = state.globalVectors
        .filter(v => v.name.toLowerCase().includes(q) || v.code.toLowerCase().includes(q))
        .map(v => `
            <div onclick="selectLanguageVector('${v.code}')" class="lang-opt ${state.preferredLang === v.code ? 'active' : ''}">
                <span class="code">${v.code}</span>
                <span class="name">${v.name}</span>
            </div>
        `).join('');
    
    if (filteredHtml === '') {
        filteredHtml = '<div class="col-span-full p-10 text-center text-cyber-red/50 text-xs uppercase tracking-widest">No matching neural vectors found.</div>';
    }
    
    grid.innerHTML = filteredHtml;
}

function closeLanguageSelector() {
    const overlay = document.getElementById('langSelectorOverlay');
    if (overlay) overlay.remove();
}

function selectLanguageVector(langCode) {
    state.preferredLang = langCode;
    state.manualLangOverride = true;
    localStorage.setItem('shadow_lang', langCode);
    
    const activeLangEl = document.getElementById('activeLang');
    if (activeLangEl) activeLangEl.innerText = langCode.toUpperCase();
    
    closeLanguageSelector();

    // AI Acknowledgment of Neural Vector Shift
    const langNames = {
        'ta-IN': 'Tamil (தமிழ்)', 'hi-IN': 'Hindi (हिन्दी)', 'ja-JP': 'Japanese (日本語)',
        'fr-FR': 'French (Français)', 'es-ES': 'Spanish (Español)', 'te-IN': 'Telugu (తెలుగు)',
        'kn-IN': 'Kannada (ಕನ್ನಡ)', 'ml-IN': 'Malayalam (മലയാളம்)', 'bn-IN': 'Bengali (বাংলা)',
        'mr-IN': 'Marathi (मराठी)', 'gu-IN': 'Gujarati (ગુજરાતી)', 'pa-IN': 'Punjabi (ਪੰਜਾਬੀ)',
        'ru-RU': 'Russian (Русский)', 'ar-SA': 'Arabic (العربية)', 'tr-TR': 'Turkish (Türkçe)',
        'vi-VN': 'Vietnamese (Tiếng Việt)', 'th-TH': 'Thai (ไทย)', 'id-ID': 'Indonesian (Bahasa)',
        'nl-NL': 'Dutch (Nederlands)', 'pl-PL': 'Polish (Polski)', 'el-GR': 'Greek (Ελληνικά)',
        'ko-KR': 'Korean (한국어)', 'zh-CN': 'Chinese (简体中文)', 'it-IT': 'Italian (Italiano)'
    };
    const langLabel = langNames[langCode] || langCode;
    const ackMessage = langCode === 'ta-IN' ? 
        `[SYSTEM]: Neural Vector synchronized. Communication protocols now optimized for **${langLabel}**. இப்போது நான் உங்களுடன் தமிழில் பேச முடியும்.` :
        `[SYSTEM]: Neural Vector synchronized. Communication protocols now optimized for **${langLabel}**. Ready for tactical input.`;
    
    appendMessage('assistant', ackMessage);
    if (state.voiceEnabled) speakResponse(`Neural Vector Aligned. Language set to ${langLabel}`, 'en-US');
    
    // Impact: Synchronize STT recognition engine with the new Neural Protocol immediately
    if (recognition) {
        recognition.lang = langCode;
        if (state.listening) {
            // Need to restart recognition to apply language change in some browsers
            try { 
                recognition.stop(); 
                setTimeout(() => { if (state.listening) recognition.start(); }, 100);
            } catch(e) {}
        }
    }
    
    // Pulse animation on the footer label
    if (activeLangEl) {
        activeLangEl.classList.add('animate-pulse', 'text-white');
        setTimeout(() => activeLangEl.classList.remove('animate-pulse', 'text-white'), 1000);
    }
}

function updateMicUI() {
    const micBtn = document.getElementById('micBtn');
    const micIcon = document.getElementById('micIcon');
    if (!micBtn || !micIcon) return;

    if (state.listening) {
        micBtn.classList.add('bg-cyber-blue/20', 'border-cyber-blue', 'animate-pulse');
        micIcon.classList.add('text-cyber-blue');
    } else {
        micBtn.classList.remove('bg-cyber-blue/20', 'border-cyber-blue', 'animate-pulse');
        micIcon.classList.remove('text-cyber-blue');
    }
}

// Model Selection Routing Override
function changeModel(val) {
    state.preferredModel = val;
    localStorage.setItem('shadow_preferred_model', val);
}

function toggleCodeWorkspace() {
    const ws = document.getElementById('codeWorkspace');
    const status = document.getElementById('workspaceStatus');
    if (!ws || !status) return;

    if (ws.classList.contains('w-0')) {
        ws.classList.remove('w-0');
        ws.classList.add('w-full', 'absolute', 'inset-0', 'z-40', 'lg:relative', 'lg:w-[500px]', 'lg:border-l', 'lg:z-auto');
        status.innerText = 'ON';
        status.className = 'text-cyber-blue';
    } else {
        ws.classList.add('w-0');
        ws.classList.remove('w-full', 'absolute', 'inset-0', 'z-40', 'lg:relative', 'lg:w-[500px]', 'lg:border-l', 'lg:z-auto');
        status.innerText = 'OFF';
        status.className = 'text-cyber-red';
    }
}

function clearEditor() {
    const editor = document.getElementById('workspaceEditor');
    if (editor) editor.value = '';
}

function clearTerminal() {
    const terminal = document.getElementById('workspaceTerminal');
    if (terminal) terminal.innerText = 'Ready for execution...';
}

async function runCode() {
    const editor = document.getElementById('workspaceEditor');
    const langSelect = document.getElementById('codeLangSelect');
    const terminal = document.getElementById('workspaceTerminal');
    const runBtn = document.getElementById('runCodeBtn');

    if (!editor || !langSelect || !terminal || !runBtn) return;

    const code = editor.value;
    const lang = langSelect.value;

    if (!code.trim()) {
        terminal.innerText = 'ERROR: No code provided to execute.';
        return;
    }

    terminal.innerText = 'Initializing execution sandbox...\nRunning payload...';
    runBtn.disabled = true;
    runBtn.classList.add('opacity-50', 'cursor-not-allowed');

    try {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (state.token) {
            headers['Authorization'] = `Bearer ${state.token}`;
        }

        const res = await fetch(`${API_BASE}/api/chat/execute`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ code, lang })
        });

        const data = await res.json();
        if (res.ok) {
            let output = '';
            if (data.stdout) output += data.stdout;
            if (data.stderr) output += (output ? '\n' : '') + 'STDERR:\n' + data.stderr;
            
            output = output || 'Code executed successfully with no output.';
            terminal.innerText = `${output}\n\n[Process completed with exit code: ${data.exit_code}]`;
        } else {
            terminal.innerText = `SYSTEM_FAILURE: ${data.detail || 'Failed to execute code'}`;
        }
    } catch (err) {
        terminal.innerText = `CONNECTION_ERROR: Failed to reach sandbox executor. ${err.message}`;
    } finally {
        runBtn.disabled = false;
        runBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

function loadCodeIntoWorkspace(encodedCode, lang) {
    const code = decodeURIComponent(escape(atob(encodedCode)));
    
    // Ensure workspace is open
    const ws = document.getElementById('codeWorkspace');
    if (ws && ws.classList.contains('w-0')) {
        toggleCodeWorkspace();
    }
    
    // Set code in editor
    const editor = document.getElementById('workspaceEditor');
    if (editor) {
        editor.value = code;
    }
    
    // Set language in dropdown
    const langSelect = document.getElementById('codeLangSelect');
    if (langSelect) {
        const normalizedLang = lang.toLowerCase();
        if (normalizedLang === 'python' || normalizedLang === 'py') {
            langSelect.value = 'python';
        } else if (normalizedLang === 'java') {
            langSelect.value = 'java';
        } else if (normalizedLang === 'cpp' || normalizedLang === 'c++' || normalizedLang === 'c') {
            langSelect.value = 'cpp';
        }
    }
}


