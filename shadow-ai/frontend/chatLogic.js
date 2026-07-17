// ChatGPT Premium Interface Tactical Chat Logic

function startNewSession() {
    state.currentSessionId = null;
    state.selectedImageData = null; 
    state.selectedFileText = null;
    clearImage();
    
    const chatWindow = document.getElementById('chatWindow');
    if (chatWindow) {
        chatWindow.innerHTML = `
            <div class="welcome-container animate-float">
                <div class="welcome-logo">
                    <img src="/files/assets/shadow_ninja_red.png" alt="Shadow Logo">
                </div>
                <h2 class="welcome-title">What can I help with today, boss?</h2>
                <div class="suggestions-grid">
                    <div class="suggestion-card" onclick="quickAction('Help me write a Python script to scan directories for specific patterns.')">
                        <div class="suggestion-title">Code a search utility</div>
                        <div class="suggestion-desc">Write a python scan function</div>
                        <span class="suggestion-arrow">→</span>
                    </div>
                    <div class="suggestion-card" onclick="quickAction('Draft a professional email asking for feedback on our tactical chat application.')">
                        <div class="suggestion-title">Draft feedback email</div>
                        <div class="suggestion-desc">Formal request for operative feedback</div>
                        <span class="suggestion-arrow">→</span>
                    </div>
                    <div class="suggestion-card" onclick="quickAction('Explain quantum computing and neural embeddings in simple terms.')">
                        <div class="suggestion-title">Explain embeddings</div>
                        <div class="suggestion-desc">Explain high-dimensional vectors</div>
                        <span class="suggestion-arrow">→</span>
                    </div>
                    <div class="suggestion-card" onclick="quickAction('Design a tactical workout plan for physical and cognitive endurance.')">
                        <div class="suggestion-title">Design workout plan</div>
                        <div class="suggestion-desc">For maximum operational stamina</div>
                        <span class="suggestion-arrow">→</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    // De-highlight active list session items
    const activeItems = document.querySelectorAll('.session-item');
    activeItems.forEach(item => item.classList.remove('active'));

    // Auto-close sidebar on mobile after selecting new session
    toggleSidebarMobile(false);
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
        
        if (sessions.length === 0) {
            sessionList.innerHTML = `<div class="text-[10px] text-center text-cyber-textSecondary p-4 uppercase tracking-widest opacity-60">No operational logs</div>`;
            return;
        }

        sessionList.innerHTML = sessions.map(s => {
            const isActive = state.currentSessionId === s.id ? 'active' : '';
            return `
            <div id="session-item-${s.id}" class="session-item ${isActive}">
                <div class="session-title-container" onclick="selectSession('${s.id}')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                    <span class="session-text" id="session-text-${s.id}">${s.title || 'NULL_SUBJECT'}</span>
                </div>
                <div class="session-actions" id="session-actions-${s.id}">
                    <button onclick="startRenameSession('${s.id}', event)" class="session-action-btn" title="Rename log">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
                    </button>
                    <button onclick="deleteSession('${s.id}', event)" class="session-action-btn text-cyber-red/80 hover:text-cyber-red" title="Delete log">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </div>
            </div>
            `;
        }).join('');
    } catch (err) {
        sessionList.innerHTML = `<div class="text-[9px] text-cyber-red/50 uppercase font-black text-center p-4">Uplink_Error: ${err.message}</div>`;
    }
}

function startRenameSession(id, event) {
    if (event) event.stopPropagation();
    const textSpan = document.getElementById(`session-text-${id}`);
    const actionsDiv = document.getElementById(`session-actions-${id}`);
    if (!textSpan || !actionsDiv) return;

    const currentTitle = textSpan.innerText;
    
    // Replace text element with inline input
    textSpan.outerHTML = `<input type="text" class="session-rename-input" id="session-input-${id}" value="${currentTitle}" onkeydown="handleRenameKeydown('${id}', event)" onblur="saveRenameSession('${id}')" />`;
    actionsDiv.style.setProperty('display', 'none', 'important');

    const inputEl = document.getElementById(`session-input-${id}`);
    if (inputEl) {
        inputEl.focus();
        inputEl.select();
    }
}

function handleRenameKeydown(id, event) {
    if (event.key === 'Enter') {
        saveRenameSession(id);
    } else if (event.key === 'Escape') {
        cancelRenameSession(id);
    }
}

async function saveRenameSession(id) {
    const inputEl = document.getElementById(`session-input-${id}`);
    if (!inputEl) return;
    
    const newTitle = inputEl.value.trim();
    if (!newTitle) {
        cancelRenameSession(id);
        return;
    }

    // Optimistic UI rename
    const parent = inputEl.parentElement;
    parent.innerHTML = `
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        <span class="session-text" id="session-text-${id}">${newTitle}</span>
    `;
    
    const itemEl = document.getElementById(`session-item-${id}`);
    const actionsDiv = itemEl ? itemEl.querySelector('.session-actions') : null;
    if (actionsDiv) actionsDiv.style.removeProperty('display');

    try {
        const res = await fetch(`${API_BASE}/api/chat/sessions/${id}`, {
            method: 'PATCH',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${state.token}`
            },
            body: JSON.stringify({ title: newTitle })
        });
        if (!res.ok) throw new Error("Rename failed");
        fetchSessions();
    } catch (err) {
        console.error("Rename session log failed:", err);
        fetchSessions(); // Rollback
    }
}

function cancelRenameSession(id) {
    fetchSessions(); // Reload sessions lists to rollback input elements
}

async function deleteSession(id, event) {
    if (event) event.stopPropagation();
    
    if (!confirm("Are you sure you want to terminate this operational thread log?")) return;

    // Optimistic delete
    const item = document.getElementById(`session-item-${id}`);
    if (item) item.remove();

    try {
        const res = await fetch(`${API_BASE}/api/chat/sessions/${id}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        
        if (!res.ok) throw new Error("Delete failed");
        
        if (state.currentSessionId === id) {
            startNewSession();
        }
        fetchSessions();
    } catch (err) {
        console.error("Delete session failure:", err);
        fetchSessions(); // Rollback
    }
}

function selectSession(id) {
    loadSession(id);
    toggleSidebarMobile(false);
}

async function loadSession(sessionId) {
    state.currentSessionId = sessionId;
    const chatWindow = document.getElementById('chatWindow');
    if (!chatWindow) return;

    chatWindow.innerHTML = `
        <div class="flex flex-col items-center justify-center py-20 gap-4">
            <div class="w-10 h-10 border-2 border-accent-color border-t-transparent rounded-full animate-spin"></div>
            <div class="text-xs text-cyber-textSecondary font-semibold uppercase tracking-[3px] animate-pulse">Syncing Neural Archives...</div>
        </div>
    `;

    // Active visual highlight
    const items = document.querySelectorAll('.session-item');
    items.forEach(el => el.classList.remove('active'));
    const activeItem = document.getElementById(`session-item-${sessionId}`);
    if (activeItem) activeItem.classList.add('active');

    try {
        const res = await fetch(`${API_BASE}/api/chat/sessions/${sessionId}`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        if (!res.ok) throw new Error("ACCESS_DENIED");

        const data = await res.json();
        chatWindow.innerHTML = '';
        
        if (data.messages.length === 0) {
            startNewSession();
        } else {
            data.messages.forEach(msg => appendMessage(msg.role, msg.content));
            scrollToBottom();
        }
    } catch (err) {
        chatWindow.innerHTML = `<div class="cyber-panel p-6 border-cyber-red text-cyber-red text-xs font-black uppercase tracking-widest text-center">ARCHIVE_CORRUPTED: ${err.message}</div>`;
    }
}

function appendMessage(role, content, isStreaming = false) {
    const chatWindow = document.getElementById('chatWindow');
    if (!chatWindow) return;

    const isUser = role === 'user';
    
    // Check if streaming is active to append directly to assistant bubble
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

    // Typing indicator check
    removeTypingIndicator();

    const outerDiv = document.createElement('div');
    outerDiv.className = 'message-outer-container';
    outerDiv.dataset.role = role;
    if (isStreaming) {
        outerDiv.dataset.streaming = 'true';
        outerDiv.dataset.rawContent = content;
    }

    const panelClass = isUser ? 'cyber-panel-red' : 'cyber-panel';
    const senderLabel = isUser ? 'OPERATIVE' : 'SHADOW_AI';
    const avatarClass = isUser ? 'message-avatar-user' : 'message-avatar-ai';
    const avatarContent = isUser ? 'OP' : `<img src="/files/assets/shadow_ninja_red.png" class="w-full h-full object-cover p-0.5 opacity-90" />`;

    outerDiv.innerHTML = `
        <div class="${panelClass}">
            <div class="message-wrapper">
                <div class="message-avatar ${avatarClass}">
                    ${avatarContent}
                </div>
                <div class="message-content-container">
                    <div class="message-header">
                        <span class="message-sender">${senderLabel}</span>
                        <span class="message-timestamp">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}</span>
                    </div>
                    <div class="message-content">
                        ${state.selectedImageData && isUser ? `<img src="data:image/jpeg;base64,${state.selectedImageData}" class="max-w-sm mb-4 rounded border border-cyber-red/30 shadow-2xl" />` : ''}
                        ${formatAIResponse(content)}
                    </div>
                </div>
            </div>
        </div>
    `;

    chatWindow.appendChild(outerDiv);
    return outerDiv;
}

function appendTypingIndicator() {
    const chatWindow = document.getElementById('chatWindow');
    if (!chatWindow) return;
    
    removeTypingIndicator();

    const outerDiv = document.createElement('div');
    outerDiv.id = 'typingIndicator';
    outerDiv.className = 'message-outer-container';
    
    const panelClass = 'cyber-panel';
    const avatarClass = 'message-avatar-ai';
    const avatarContent = `<img src="/files/assets/shadow_ninja_red.png" class="w-full h-full object-cover p-0.5 opacity-40" />`;

    outerDiv.innerHTML = `
        <div class="${panelClass}">
            <div class="message-wrapper">
                <div class="message-avatar ${avatarClass}">
                    ${avatarContent}
                </div>
                <div class="message-content-container">
                    <div class="message-header">
                        <span class="message-sender">SHADOW_AI</span>
                        <span class="message-timestamp">PROBING MATRIX...</span>
                    </div>
                    <div class="message-content">
                        <div class="typing-bubble">
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    chatWindow.appendChild(outerDiv);
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

    // Trigger visual avatar pulses if speaking
    const avatar = document.querySelector('.message-avatar-ai');
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
                            fetchSessions(); // Refresh list to add newly created session log
                        }
                    } catch (e) {
                        console.warn("MALFORMED_STREAM_CHUNK", e);
                    }
                }
            }
        }

        if (window.triggerGlitch) window.triggerGlitch();
        
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
        btn.style.color = 'var(--cyber-blue, #00f0ff)';
        if (icon) {
            icon.innerHTML = `<path d="M11 5L6 9H2v6h4l5 4V5z"></path><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>`;
        }
    } else {
        btn.style.color = 'var(--cyber-red, #ff003c)';
        if (icon) {
            icon.innerHTML = `<path d="M11 5L6 9H2v6h4l5 4V5z"></path><line x1="23" y1="9" x2="17" y2="15"></line><line x1="17" y1="9" x2="23" y2="15"></line>`;
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
        status.innerText = state.responseMode.toUpperCase();
        status.className = state.responseMode === 'direct' ? 'text-cyber-blue font-semibold' : 'text-cyber-red font-semibold';
    }
}

async function speakResponse(text, lang) {
    const cleanText = text.replace(/[*#`_\[\]()]/g, '').replace(/!\[.*?\]\(.*?\)/g, '');
    if (!cleanText) return;

    let neuralStarted = false;
    const fallbackTimeout = setTimeout(() => {
        if (!neuralStarted) {
            speakFallback(cleanText, lang);
        }
    }, 450);

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
        // Fallback triggers
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
    
    renderer.code = (codeOrObj, lang) => {
        let code = codeOrObj;
        let codeLang = lang;
        if (codeOrObj && typeof codeOrObj === 'object') {
            code = codeOrObj.text || '';
            codeLang = codeOrObj.lang || lang;
        }

        const encodedCode = btoa(unescape(encodeURIComponent(code)));
        const displayLang = codeLang ? codeLang.toUpperCase() : 'CODE';
        
        return `
            <div class="code-block-container">
                <div class="code-block-header">
                    <span>${displayLang}</span>
                    <div class="code-block-actions">
                        <button onclick="copyCodeSnippet('${encodedCode}', this)" class="code-action-btn">
                            COPY CODE
                        </button>
                        <button onclick="loadCodeIntoWorkspace('${encodedCode}', '${codeLang || 'python'}')" class="code-action-btn">
                            LOAD TO WORKSPACE
                        </button>
                    </div>
                </div>
                <pre class="p-4 overflow-x-auto text-sm"><code>${code}</code></pre>
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

// Copy Code Snippet implementation
function copyCodeSnippet(encodedCode, buttonEl) {
    const code = decodeURIComponent(escape(atob(encodedCode)));
    navigator.clipboard.writeText(code).then(() => {
        const originalText = buttonEl.innerText;
        buttonEl.innerText = "COPIED!";
        buttonEl.style.color = "var(--accent-color)";
        setTimeout(() => {
            buttonEl.innerText = originalText;
            buttonEl.style.removeProperty('color');
        }, 2000);
    }).catch(err => {
        console.error("Clipboard copy failure:", err);
        alert("Clipboard copy block interrupted.");
    });
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
                container.style.display = 'block';
            }
        };
        reader.readAsDataURL(file);
    } else {
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
                const svgIcon = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 24 24" fill="none" stroke="%2310a37f" stroke-width="1"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`;
                preview.src = svgIcon;
                container.style.display = 'block';
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
    if (preview) preview.src = '';
    if (container) container.style.display = 'none';
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
        autoScaleTextarea(input);
        handleSendMessage();
    }
}

// Voice Recognition
let recognition = null;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = state.getBCP47(state.preferredLang || 'en-US');

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
        console.error('Voice input error:', event.error);
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
        alert('Speech recognition is not supported in this browser.');
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
        recognition.lang = state.getBCP47(state.preferredLang || 'en-US');
        recognition.start();
    } catch (e) {
        console.warn('Recognition active');
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
            <h3 class="text-sm font-orbitron font-black text-cyber-blue uppercase tracking-[3px]">Language Configuration</h3>
            <button onclick="closeLanguageSelector()" class="text-cyber-red/50 hover:text-cyber-red">✕</button>
        </div>
        <input type="text" id="langSearch" placeholder="Search language codes..." 
               class="cyber-search-input" oninput="filterLanguages(this.value)">
        <div class="lang-grid" id="langGrid">
            ${langOptions}
        </div>
        <div class="p-4 bg-cyber-red/5 border-t border-white/5 text-[9px] text-cyber-textSecondary uppercase tracking-widest text-center px-10">
            Selected language applies to speech output synthesis and voice inputs.
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
        filteredHtml = '<div class="col-span-full p-10 text-center text-cyber-red/50 text-xs uppercase tracking-widest">No match found</div>';
    }
    
    grid.innerHTML = filteredHtml;
}

function closeLanguageSelector() {
    const overlay = document.getElementById('langSelectorOverlay');
    if (overlay) overlay.remove();
}

function selectLanguageVector(langCode) {
    state.preferredLang = langCode;
    localStorage.setItem('shadow_lang', langCode);
    
    const activeLangEl = document.getElementById('activeLang');
    if (activeLangEl) activeLangEl.innerText = langCode.toUpperCase();
    
    closeLanguageSelector();

    const langNames = {
        'ta-IN': 'Tamil (தமிழ்)', 'hi-IN': 'Hindi (हिन्दी)', 'ja-JP': 'Japanese (日本語)',
        'fr-FR': 'French (Français)', 'es-ES': 'Spanish (Español)', 'te-IN': 'Telugu (తెలుగు)',
        'kn-IN': 'Kannada (ಕನ್ನಡ)', 'ml-IN': 'Malayalam (மலையாளம்)', 'bn-IN': 'Bengali (বাংলা)',
        'mr-IN': 'Marathi (மராठी)', 'gu-IN': 'Gujarati (ગુજરાતી)', 'pa-IN': 'Punjabi (பண்பீ)',
        'ru-RU': 'Russian (Русский)', 'ar-SA': 'Arabic (العربية)', 'tr-TR': 'Turkish (Türkçe)',
        'vi-VN': 'Vietnamese (Tiếng Việt)', 'th-TH': 'Thai (ไทย)', 'id-ID': 'Indonesian (Bahasa)',
        'nl-NL': 'Dutch (Nederlands)', 'pl-PL': 'Polish (Polski)', 'el-GR': 'Greek (Ελληνικά)',
        'ko-KR': 'Korean (한국어)', 'zh-CN': 'Chinese (简体中文)', 'it-IT': 'Italian (Italiano)'
    };
    const langLabel = langNames[langCode] || langCode;
    
    appendMessage('assistant', `[SYSTEM]: Unified neural communication vector aligned to **${langLabel}**.`);
    if (state.voiceEnabled) speakResponse(`Language vector synchronized to ${langLabel}`, 'en-US');
    
    if (recognition) {
        recognition.lang = langCode;
        if (state.listening) {
            try { 
                recognition.stop(); 
                setTimeout(() => { if (state.listening) recognition.start(); }, 100);
            } catch(e) {}
        }
    }
}

function updateMicUI() {
    const micBtn = document.getElementById('micBtn');
    const micIcon = document.getElementById('micIcon');
    if (!micBtn || !micIcon) return;

    if (state.listening) {
        micBtn.classList.add('speaking-glow', 'bg-cyber-blue/20');
        micIcon.style.color = "var(--accent-color)";
    } else {
        micBtn.classList.remove('speaking-glow', 'bg-cyber-blue/20');
        micIcon.style.removeProperty('color');
    }
}

function changeModel(val) {
    state.preferredModel = val;
    localStorage.setItem('shadow_preferred_model', val);
    
    // Optimistically update top model dropdown indicator if available on UI
    const indicator = document.querySelector('.indicator-pill span span');
    if (indicator) {
        indicator.innerText = val.toUpperCase();
    }
}

function toggleCodeWorkspace() {
    const ws = document.getElementById('codeWorkspace');
    const status = document.getElementById('workspaceStatus');
    if (!ws || !status) return;

    state.workspaceOpen = !state.workspaceOpen;
    localStorage.setItem('shadow_workspace_open', state.workspaceOpen);

    if (state.workspaceOpen) {
        ws.className = 'w-full absolute inset-0 z-40 lg:relative lg:w-[500px] lg:border-l lg:z-auto';
        status.innerText = 'ON';
        status.className = 'font-semibold text-cyber-blue';
    } else {
        ws.className = 'w-0';
        status.innerText = 'OFF';
        status.className = 'font-semibold text-cyber-red';
    }
}

function clearEditor() {
    const editor = document.getElementById('workspaceEditor');
    if (editor) editor.value = '';
}

function clearTerminal() {
    const terminal = document.getElementById('workspaceTerminal');
    if (terminal) terminal.innerText = 'Ready for compilation execution...';
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
        terminal.innerText = 'ERROR: No source payload provided.';
        return;
    }

    terminal.innerText = 'Compiling sandbox container matrix...\nRunning payload execution thread...';
    runBtn.disabled = true;
    runBtn.classList.add('opacity-50', 'cursor-not-allowed');

    try {
        const headers = { 'Content-Type': 'application/json' };
        if (state.token) headers['Authorization'] = `Bearer ${state.token}`;

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
            
            output = output || 'Code executed successfully with zero console output.';
            terminal.innerText = `${output}\n\n[Process completed. Sandbox exit code: ${data.exit_code}]`;
        } else {
            terminal.innerText = `SYSTEM_FAILURE: ${data.detail || 'Failed compilation response'}`;
        }
    } catch (err) {
        terminal.innerText = `SANDBOX_LINK_ERROR: ${err.message}`;
    } finally {
        runBtn.disabled = false;
        runBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    }
}

function loadCodeIntoWorkspace(encodedCode, lang) {
    const code = decodeURIComponent(escape(atob(encodedCode)));
    
    // Ensure workspace is open
    if (!state.workspaceOpen) {
        toggleCodeWorkspace();
    }
    
    const editor = document.getElementById('workspaceEditor');
    if (editor) editor.value = code;
    
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

// React to global theme change events
window.addEventListener('themechanged', (e) => {
    // If matrix canvas exists and we shifted themes, draw frame triggers
    initNeuralMatrix();
});
