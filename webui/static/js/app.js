const { createApp, ref, onMounted, nextTick, watch } = Vue;

// Configure marked with highlight.js
marked.setOptions({
    highlight: function(code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    langPrefix: 'hljs language-'
});

createApp({
    setup() {
        const sessionId = ref('');
        const targetUrl = ref('');
        const sessionState = ref('UNINITIALIZED');
        const progress = ref(0);
        const phases = ref([]);
        const flags = ref([]);
        const messages = ref([]);
        const userInput = ref('');
        const autoMode = ref(false);
        const isProcessing = ref(false);
        const errorMsg = ref('');
        const connected = ref(false);
        const socket = ref(null);
        
        const currentEvents = ref([]);
        const expandedThinking = ref(new Set());
        
        const showConfig = ref(false);
        const configData = ref({});
        const skills = ref([]);

        // Sidebar Resizer state
        const sidebarWidth = ref(340);
        const isResizing = ref(false);

        const startResize = (e) => {
            isResizing.value = true;
            document.addEventListener('mousemove', doResize);
            document.addEventListener('mouseup', stopResize);
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
        };

        const doResize = (e) => {
            if (!isResizing.value) return;
            let newWidth = e.clientX;
            if (newWidth < 250) newWidth = 250;
            if (newWidth > 800) newWidth = 800;
            sidebarWidth.value = newWidth;
        };

        const stopResize = () => {
            isResizing.value = false;
            document.removeEventListener('mousemove', doResize);
            document.removeEventListener('mouseup', stopResize);
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        };

        const scrollToBottom = () => {
            nextTick(() => {
                const container = document.getElementById('chat-container');
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            });
        };

        const addEvent = (type, text) => {
            const time = new Date().toLocaleTimeString('en-US', { hour12: false });
            currentEvents.value.push({ type, text, time });
            scrollToBottom();
        };

        const initSocket = () => {
            if (socket.value) socket.value.disconnect();

            // 使用当前页面的 origin，支持不同端口和域名
            socket.value = io(window.location.origin, {
                reconnectionDelayMax: 10000,
            });

            socket.value.on('connect', () => {
                connected.value = true;
                if (sessionId.value) {
                    socket.value.emit('join', { session_id: sessionId.value });
                }
            });

            socket.value.on('disconnect', () => {
                connected.value = false;
            });

            socket.value.on('agent_thinking', (data) => addEvent('thinking', `Agent thinking: ${data.message}`));
            socket.value.on('tool_call', (data) => {
                let text = `Tool call: <span class="text-accent font-extrabold">${data.tool}</span>`;
                if (data.code) text += `<br><pre class="mt-2 bg-background p-3 rounded-xl text-xs text-primary border border-border shadow-inner"><code>${escapeHtml(data.code)}</code></pre>`;
                addEvent('tool', text);
            });
            socket.value.on('tool_result', (data) => {
                let out = data.output;
                if(out && out.length > 200) out = out.substring(0, 200) + '...';
                addEvent('result', `Tool result: <span class="text-slate-400">${escapeHtml(out)}</span>`);
            });
            socket.value.on('phase_achieved', (data) => {
                addEvent('phase', `Phase achieved: <span class="text-success font-extrabold">${data.phase}</span>`);
                if (data.phases) phases.value = data.phases;
            });
            socket.value.on('flag_found', (data) => {
                addEvent('flag', `FLAG FOUND: <span class="text-warning font-extrabold bg-warning/10 border border-warning/30 px-2 py-1 rounded-lg shadow-sm">${data.flag}</span>`);
                if (data.flags) flags.value = data.flags;
                else if (!flags.value.includes(data.flag)) flags.value.push(data.flag);
            });
            socket.value.on('state_change', (data) => {
                if (data.state) sessionState.value = data.state;
                if (data.progress !== undefined) progress.value = data.progress;
            });
            socket.value.on('error', (data) => {
                addEvent('error', `Error: ${data.message}`);
                errorMsg.value = data.message;
            });
        };

        const escapeHtml = (unsafe) => {
            if(!unsafe) return '';
            return unsafe
                 .toString()
                 .replace(/&/g, "&amp;")
                 .replace(/</g, "&lt;")
                 .replace(/>/g, "&gt;")
                 .replace(/"/g, "&quot;")
                 .replace(/'/g, "&#039;");
        };

        const renderMarkdown = (text) => {
            return marked.parse(text || '');
        };

        const toggleThinking = (idx) => {
            const s = new Set(expandedThinking.value);
            if (s.has(idx)) s.delete(idx);
            else s.add(idx);
            expandedThinking.value = s;
        };

        const eventColor = (type) => {
            switch(type) {
                case 'thinking': return 'text-slate-500';
                case 'tool': return 'text-accent font-extrabold';
                case 'result': return 'text-slate-400';
                case 'phase': return 'text-success font-extrabold';
                case 'flag': return 'text-warning font-extrabold';
                case 'error': return 'text-danger font-extrabold';
                default: return 'text-primary';
            }
        };

        const difficultyColor = (diff) => {
            switch((diff || '').toLowerCase()) {
                case 'easy': return 'text-success';
                case 'medium': return 'text-warning';
                case 'hard': return 'text-danger';
                default: return 'text-slate-400';
            }
        };

        const loadHistory = async () => {
            try {
                const res = await api.getHistory(sessionId.value);
                if (res.success && res.messages) {
                    messages.value = res.messages;
                    scrollToBottom();
                }
            } catch (e) {
                console.error("Failed to load history", e);
            }
        };

        const loadStatus = async () => {
            try {
                const res = await api.getStatus(sessionId.value);
                if (res.success) {
                    sessionState.value = res.state || 'UNKNOWN';
                    progress.value = res.progress || 0;
                    targetUrl.value = res.target_url || targetUrl.value;
                }
            } catch (e) {
                console.error("Failed to load status", e);
            }
        };

        const initSession = async () => {
            try {
                isProcessing.value = true;
                errorMsg.value = '';
                const res = await api.initSession();
                if (res.success) {
                    sessionId.value = res.session_id;
                    sessionState.value = 'INITIALIZED';
                    messages.value = [];
                    currentEvents.value = [];
                    phases.value = [];
                    flags.value = [];
                    progress.value = 0;
                    
                    if (socket.value && connected.value) {
                        socket.value.emit('join', { session_id: sessionId.value });
                    }
                } else {
                    errorMsg.value = res.message || 'Failed to initialize session';
                }
            } catch (e) {
                errorMsg.value = e.response?.data?.error?.message || e.message;
            } finally {
                isProcessing.value = false;
            }
        };

        const resetSession = async () => {
            if (!sessionId.value) return initSession();
            try {
                isProcessing.value = true;
                const res = await api.resetSession(sessionId.value);
                if (res.success) {
                    sessionId.value = res.session_id;
                    messages.value = [];
                    currentEvents.value = [];
                    phases.value = [];
                    flags.value = [];
                    progress.value = 0;
                    sessionState.value = 'INITIALIZED';
                    if (socket.value && connected.value) {
                        socket.value.emit('join', { session_id: sessionId.value });
                    }
                }
            } catch (e) {
                errorMsg.value = e.response?.data?.error?.message || e.message;
            } finally {
                isProcessing.value = false;
            }
        };

        const setTarget = async () => {
            if (!sessionId.value) await initSession();
            if (!targetUrl.value) return;
            
            try {
                isProcessing.value = true;
                errorMsg.value = '';
                const res = await api.setTarget(sessionId.value, targetUrl.value);
                if (!res.success) {
                    errorMsg.value = res.message || 'Failed to set target';
                } else {
                    addEvent('info', `Target set to: ${targetUrl.value}`);
                }
            } catch (e) {
                errorMsg.value = e.response?.data?.error?.message || e.message;
            } finally {
                isProcessing.value = false;
            }
        };

        const sendStep = async () => {
            if (!userInput.value.trim() || isProcessing.value) return;
            if (!sessionId.value) await initSession();
            
            const input = userInput.value;
            userInput.value = '';
            
            messages.value.push({ role: 'user', content: input });
            currentEvents.value = []; // Clear previous events for new step
            scrollToBottom();
            
            try {
                isProcessing.value = true;
                errorMsg.value = '';
                const res = await api.step(sessionId.value, input, autoMode.value);
                
                if (res.success) {
                    const eventsSnapshot = [...currentEvents.value];
                    messages.value.push({ role: 'assistant', content: res.response, events: eventsSnapshot });
                    const newIdx = messages.value.length - 1;
                    if (eventsSnapshot.length > 0) {
                        const s = new Set(expandedThinking.value);
                        s.add(newIdx);
                        expandedThinking.value = s;
                    }
                    currentEvents.value = [];
                    if (res.state) sessionState.value = res.state;
                    if (res.progress !== undefined) progress.value = res.progress;
                    if (res.phases) phases.value = res.phases;
                    if (res.flags) flags.value = res.flags;
                } else {
                    errorMsg.value = res.message || 'Step execution failed';
                }
            } catch (e) {
                errorMsg.value = e.response?.data?.error?.message || e.message;
                messages.value.push({ role: 'assistant', content: `**Error:** ${errorMsg.value}` });
            } finally {
                isProcessing.value = false;
                scrollToBottom();
            }
        };

        const fetchConfig = async () => {
            try {
                const res = await api.getConfig();
                if (res.success) configData.value = res.config;
            } catch (e) {
                console.error("Failed to fetch config", e);
            }
        };

        const fetchSkills = async () => {
            try {
                // Fetching all skills, ignoring category for now or passing empty
                const res = await api.getSkills();
                if (res.success) skills.value = res.skills || [];
            } catch (e) {
                console.error("Failed to fetch skills", e);
            }
        };

        const executeSkill = async (skillId) => {
            if (!sessionId.value) await initSession();
            try {
                isProcessing.value = true;
                currentEvents.value = [];
                addEvent('info', `Executing skill: ${skillId}...`);
                
                const res = await api.executeSkill(sessionId.value, skillId, { target_url: targetUrl.value });
                if (res.success && res.result) {
                    const r = res.result;
                    let content = `**Skill Execution: ${skillId}**\n\nStatus: ${r.success ? 'Success' : 'Failed'}\nMessage: ${r.message}`;
                    if (r.findings && r.findings.length) {
                        content += `\n\n**Findings:**\n- ${r.findings.join('\n- ')}`;
                    }
                    messages.value.push({ role: 'assistant', content, events: [...currentEvents.value] });
                    currentEvents.value = [];
                }
            } catch (e) {
                errorMsg.value = e.response?.data?.error?.message || e.message;
                addEvent('error', `Skill execution failed: ${errorMsg.value}`);
            } finally {
                isProcessing.value = false;
                scrollToBottom();
            }
        };

        onMounted(() => {
            initSocket();
            initSession();
            fetchConfig();
            fetchSkills();
        });

        return {
            sessionId, targetUrl, sessionState, progress, phases, flags,
            messages, userInput, autoMode, isProcessing, errorMsg, connected,
            currentEvents, expandedThinking, showConfig, configData, skills,
            sidebarWidth, startResize,
            setTarget, sendStep, resetSession, fetchConfig, executeSkill,
            toggleThinking, renderMarkdown, eventColor, difficultyColor
        };
    }
}).mount('#app');
