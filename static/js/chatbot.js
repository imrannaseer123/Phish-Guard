/* Floating Chatbot Logic */
document.addEventListener('DOMContentLoaded', function () {
    if (typeof ENABLE_CHATBOT === 'undefined' || !ENABLE_CHATBOT) return;

    // Inject Chatbot UI
    const chatbotHTML = `
        <div id="phishguard-chatbot" class="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-4 font-sans">
            <!-- Chat Window -->
            <div id="chatbot-window" class="hidden w-80 h-96 bg-white dark:bg-slate-800 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 flex flex-col overflow-hidden transition-all duration-300 transform origin-bottom-right scale-95 opacity-0 relative">
                <!-- Resize Handle (Top-Left) -->
                <div id="chatbot-resize" class="absolute top-0 left-0 w-6 h-6 z-50 cursor-nw-resize flex items-center justify-center text-slate-400/50 hover:text-slate-600 dark:hover:text-white">
                    <svg class="w-4 h-4 transform rotate-90" fill="currentColor" viewBox="0 0 24 24"><path d="M15 4l-2 2 10 10 2-2-10-10zm-6 0l-2 2 6 6 2-2-6-6zm-6 0l-2 2 2 2 2-2-2-2z"/></svg>
                </div>

                <!-- Header -->
                <div class="bg-indigo-600 p-4 flex justify-between items-center cursor-move" id="chatbot-header">
                    <div class="flex items-center gap-2 text-white">
                        <span class="text-xl">🛡️</span>
                        <div>
                            <h3 class="font-bold text-sm leading-tight">Security Assistant</h3>
                            <p class="text-[10px] text-indigo-200 opacity-80">Powered by OpenClaw AI</p>
                        </div>
                    </div>
                    <button id="chatbot-close" class="text-white/70 hover:text-white transition-colors">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>
                
                <!-- Messages Area -->
                <div id="chatbot-messages" class="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50 dark:bg-slate-900/50">
                    <div class="flex flex-col gap-1 items-start max-w-[85%]">
                        <div class="bg-indigo-100 dark:bg-indigo-900/30 text-slate-800 dark:text-slate-200 p-3 rounded-2xl rounded-tl-none text-sm shadow-sm">
                            Hello! I'm your PhishGuard security assistant. I can explain risk scores, analyzer details, or general security concepts. How can I help?
                        </div>
                        <span class="text-[10px] text-slate-400 ml-1">OpenClaw AI</span>
                    </div>
                </div>

                <!-- Input Area -->
                <div class="p-3 bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700">
                    <form id="chatbot-form" class="flex gap-2">
                        <input type="text" id="chatbot-input" placeholder="Ask a question..." 
                            class="flex-1 bg-slate-100 dark:bg-slate-900 border-0 rounded-full px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 dark:text-white placeholder-slate-400">
                        <button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white p-2 rounded-full transition-colors disabled:opacity-50 disabled:cursor-not-allowed" id="chatbot-send">
                            <svg class="w-4 h-4 transform rotate-90" fill="currentColor" viewBox="0 0 20 20"><path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path></svg>
                        </button>
                    </form>
                </div>
            </div>

            <!-- Floating Button -->
            <button id="chatbot-toggle" class="animate-bounce-in w-14 h-14 bg-indigo-600 hover:bg-indigo-500 text-white rounded-full shadow-lg hover:shadow-indigo-500/50 flex items-center justify-center transition-all transform hover:scale-110 active:scale-95 group relative">
                <span class="notif-dot" id="chatbot-notif"></span>
                <span class="absolute inset-0 rounded-full bg-indigo-600 animate-ping opacity-0 group-hover:opacity-20"></span>
                <span class="text-2xl">💬</span>
            </button>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', chatbotHTML);

    // Elements
    const root = document.getElementById('phishguard-chatbot');
    const toggleBtn = document.getElementById('chatbot-toggle');
    const windowEl = document.getElementById('chatbot-window');
    const closeBtn = document.getElementById('chatbot-close');
    const messagesEl = document.getElementById('chatbot-messages');
    const formEl = document.getElementById('chatbot-form');
    const inputEl = document.getElementById('chatbot-input');
    const sendBtn = document.getElementById('chatbot-send');

    let isOpen = false;

    // Toggle Window functions
    function openChat() {
        windowEl.classList.remove('hidden');
        // Trigger reflow for animation
        void windowEl.offsetWidth;
        windowEl.classList.remove('scale-95', 'opacity-0');
        windowEl.classList.add('chatbot-spring-open');
        windowEl.classList.remove('chatbot-spring-close');
        // Hide notif dot
        var notifDot = document.getElementById('chatbot-notif');
        if (notifDot) notifDot.style.display = 'none';
        isOpen = true;
        inputEl.focus();
    }

    function closeChat() {
        windowEl.classList.add('chatbot-spring-close');
        windowEl.classList.remove('chatbot-spring-open');
        setTimeout(() => {
            windowEl.classList.add('scale-95', 'opacity-0', 'hidden');
            windowEl.classList.remove('chatbot-spring-close');
        }, 250);
        isOpen = false;
    }

    toggleBtn.addEventListener('click', () => {
        if (isOpen) closeChat();
        else openChat();
    });

    closeBtn.addEventListener('click', closeChat);

    // Messaging Logic
    function parseMarkdown(text) {
        // Basic Markdown Parser for Chatbot
        let html = text
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Lists (simple bullet points)
            .replace(/^\s*-\s+(.*)$/gm, '<li class="ml-4">$1</li>')
            // Line breaks
            .replace(/\n/g, '<br>');

        // Wrap lists in ul if present
        if (html.includes('<li')) {
            html = html.replace(/<li.*<\/li>/s, '<ul>$&</ul>'); // Very basic, might need better logic for multiple lists
        }
        return html;
    }

    function appendMessage(text, isUser, source = "You") {
        const align = isUser ? 'items-end' : 'items-start';
        const color = isUser ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-indigo-100 dark:bg-indigo-900/30 text-slate-800 dark:text-slate-200 rounded-tl-none';
        const metaAlign = isUser ? 'mr-1 text-right' : 'ml-1 text-left';

        const content = isUser ? text : parseMarkdown(text);

        const html = `
            <div class="flex flex-col gap-1 ${align} max-w-[85%] animate-fade-in">
                <div class="${color} p-3 rounded-2xl text-sm shadow-sm break-words leading-relaxed">
                    ${content}
                </div>
                <span class="text-[10px] text-slate-400 ${metaAlign}">${source}</span>
            </div>
        `;
        messagesEl.insertAdjacentHTML('beforeend', html);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    formEl.addEventListener('submit', function (e) {
        e.preventDefault();
        const msg = inputEl.value.trim();
        if (!msg) return;

        appendMessage(msg, true);
        inputEl.value = '';
        inputEl.disabled = true;
        sendBtn.disabled = true;

        // Show typing indicator
        const typingId = 'typing-' + Date.now();
        const typingHTML = `
            <div id="${typingId}" class="flex flex-col gap-1 items-start max-w-[85%] animate-fade-in">
                <div class="bg-indigo-100 dark:bg-indigo-900/30 p-3 rounded-2xl rounded-tl-none text-sm shadow-sm">
                    <span class="inline-block w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce"></span>
                    <span class="inline-block w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-100"></span>
                    <span class="inline-block w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce delay-200"></span>
                </div>
            </div>
        `;
        messagesEl.insertAdjacentHTML('beforeend', typingHTML);
        messagesEl.scrollTop = messagesEl.scrollHeight;

        // Gather context
        // Try to find report context if available on page
        let context = {};
        const scoreEl = document.querySelector('.risk-score-value'); // Hypothetical selector
        if (scoreEl) context.risk_score = parseInt(scoreEl.innerText);

        fetch('/chatbot/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg, context: context })
        })
            .then(r => r.json())
            .then(data => {
                const typingEl = document.getElementById(typingId);
                if (typingEl) typingEl.remove();

                if (data.error) throw new Error(data.error);
                appendMessage(data.response, false, data.source);
            })
            .catch(err => {
                const typingEl = document.getElementById(typingId);
                if (typingEl) typingEl.remove();

                appendMessage("Sorry, I couldn't connect to the security server. Please try again.", false, "System Error");
                console.error(err);
            })
            .finally(() => {
                inputEl.disabled = false;
                sendBtn.disabled = false;
                inputEl.focus();
            });
    });

    // Drag and Drop Logic (Move the whole container)
    // We move the entire 'root' container
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;

    toggleBtn.addEventListener('mousedown', dragStart);
    document.addEventListener('mouseup', dragEnd);
    document.addEventListener('mousemove', drag);

    function dragStart(e) {
        if (e.target.closest('#chatbot-toggle')) {
            initialX = e.clientX - xOffset;
            initialY = e.clientY - yOffset;
            isDragging = true;
        }
    }

    function dragEnd(e) {
        initialX = currentX;
        initialY = currentY;
        isDragging = false;
        isResizing = false; // Also stop resizing
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            xOffset = currentX;
            yOffset = currentY;
            setTranslate(currentX, currentY, root);
        }
        if (isResizing) {
            e.preventDefault();
            resize(e);
        }
    }

    function setTranslate(xPos, yPos, el) {
        el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
    }

    // Resize Logic
    let isResizing = false;
    let startWidth, startHeight, startX, startY;
    const resizeHandle = document.getElementById('chatbot-resize');

    resizeHandle.addEventListener('mousedown', function (e) {
        e.preventDefault();
        e.stopPropagation(); // Prevent drag start
        isResizing = true;
        startWidth = windowEl.offsetWidth;
        startHeight = windowEl.offsetHeight;
        startX = e.clientX;
        startY = e.clientY;
    });

    function resize(e) {
        // Calculate new dimensions
        // Dragging Top-Left handle:
        // Move Left (negative delta X) -> Increase width
        // Move Up (negative delta Y) -> Increase height
        const deltaX = startX - e.clientX;
        const deltaY = startY - e.clientY;

        const newWidth = Math.max(300, startWidth + deltaX); // Min width 300
        const newHeight = Math.max(400, startHeight + deltaY); // Min height 400

        windowEl.style.width = `${newWidth}px`;
        windowEl.style.height = `${newHeight}px`;
    }
});
