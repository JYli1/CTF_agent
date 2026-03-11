// API Client wrapper
// 使用相对路径，自动适配当前域名和端口
const API_BASE = '/api';

// 模拟延迟
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// 统一的 Mock 处理函数
const handleMock = async (mockData) => {
    await delay(500);
    console.warn('[Mock API] Backend unreachable, using mock data.');
    return mockData;
};

const api = {
    async initSession() {
        try {
            const res = await axios.post(`${API_BASE}/agent/init`);
            return res.data;
        } catch (e) {
            if (e.message === 'Network Error') return handleMock({ success: true, session_id: 'mock-session-' + Date.now(), message: 'Mock session created' });
            throw e;
        }
    },
    async setTarget(sessionId, targetUrl) {
        try {
            const res = await axios.post(`${API_BASE}/agent/set-target`, { session_id: sessionId, target_url: targetUrl });
            return res.data;
        } catch (e) {
            if (e.message === 'Network Error') return handleMock({ success: true, message: `Target set to: ${targetUrl}` });
            throw e;
        }
    },
    async step(sessionId, userInput, autoMode) {
        try {
            const res = await axios.post(`${API_BASE}/agent/step`, { session_id: sessionId, user_input: userInput, auto_mode: autoMode });
            return res.data;
        } catch (e) {
            if (e.message === 'Network Error') return handleMock({ 
                success: true, 
                response: "This is a mock response. The backend is currently unreachable, so I'm simulating a reply.",
                state: "INFO_GATHERING",
                progress: Math.min(100, Math.floor(Math.random() * 40) + 20),
                phases: ["Information Gathering", "Port Scanning"],
                flags: []
            });
            throw e;
        }
    },
    async getStatus(sessionId) {
        try {
            const res = await axios.get(`${API_BASE}/agent/status?session_id=${sessionId}`);
            return res.data;
        } catch (e) {
            if (e.message === 'Network Error') return handleMock({ success: true, state: 'MOCK_STATE', progress: 50 });
            throw e;
        }
    },
    async getHistory(sessionId) {
        try {
            const res = await axios.get(`${API_BASE}/agent/history?session_id=${sessionId}`);
            return res.data;
        } catch (e) {
            if (e.message === 'Network Error') return handleMock({ success: true, messages: [] });
            throw e;
        }
    },
    async resetSession(sessionId) {
        try {
            const res = await axios.post(`${API_BASE}/agent/reset`, { session_id: sessionId });
            return res.data;
        } catch (e) {
            if (e.message === 'Network Error') return handleMock({ success: true, session_id: 'mock-session-' + Date.now(), message: 'Session reset' });
            throw e;
        }
    },
    async getConfig() {
        try {
            const res = await axios.get(`${API_BASE}/config/get`);
            return res.data;
        } catch (e) {
            if (e.message === 'Network Error') {
                return handleMock({
                    success: true,
                    config: {
                        llm: { provider: "openai", model: "Pro/zai-org/GLM-5", api_key: "sk-mock..." },
                        advanced: { max_sub_steps: 5, log_level: "INFO" },
                        rag: { embedding_model: "Qwen/Qwen3-Embedding-8B" }
                    }
                });
            }
            throw e;
        }
    },
    async getSkills() {
        try {
            const res = await axios.get(`${API_BASE}/skills/list`);
            return res.data;
        } catch (e) {
            if (e.message === 'Network Error') {
                return handleMock({
                    success: true,
                    skills: [
                        { id: "sqli_detection", name: "SQL Injection", difficulty: "medium", description: "Automatically detect SQL injection vulnerabilities." },
                        { id: "dir_scan", name: "Dir Scanner", difficulty: "easy", description: "Scan for hidden directories and files." },
                        { id: "pwn_analysis", name: "PWN Analysis", difficulty: "hard", description: "Analyze binary for common vulnerabilities." }
                    ]
                });
            }
            throw e;
        }
    },
    async executeSkill(sessionId, skillId, context) {
        try {
            const res = await axios.post(`${API_BASE}/skills/execute`, { session_id: sessionId, skill_id: skillId, context });
            return res.data;
        } catch (e) {
            if (e.message === 'Network Error') return handleMock({ 
                success: true, 
                result: { success: true, message: "Mock execution completed successfully.", findings: ["Found mock vulnerability in parameter 'id'"] } 
            });
            throw e;
        }
    }
};
