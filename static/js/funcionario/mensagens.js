let allMessages = [];
        let currentFilter = 'all';

        async function loadMessages() {
            try {
                const response = await fetch('/api/contact/messages');
                if (!response.ok) throw new Error('Erro ao carregar mensagens');
                
                allMessages = await response.json();
                renderMessages();
                updateStats();
            } catch (error) {
                console.error('Erro:', error);
                document.getElementById('messages-list').innerHTML = 
                    '<p class="empty-message">❌ Erro ao carregar mensagens</p>';
            }
        }

        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentFilter = this.dataset.filter;
                renderMessages();
            });
        });

        function renderMessages() {
            let filtered = allMessages;

            if (currentFilter === 'unread') {
                filtered = allMessages.filter(msg => !msg.read);
            } else if (currentFilter === 'read') {
                filtered = allMessages.filter(msg => msg.read);
            }

            const messagesList = document.getElementById('messages-list');

            if (filtered.length === 0) {
                messagesList.innerHTML = '<p class="empty-message">Nenhuma mensagem encontrada</p>';
                return;
            }

            messagesList.innerHTML = filtered.map((msg, index) => {
                const date = new Date(msg.timestamp).toLocaleString('pt-BR');
                const unread = !msg.read;
                
                return `
                    <div class="message-card ${unread ? 'unread' : ''}" style="animation-delay: ${index * 0.08}s">
                        <div class="message-header">
                            <div class="message-sender-info">
                                <div class="message-sender">${msg.name}</div>
                                <div class="message-contact">📧 ${msg.email}</div>
                                ${msg.phone ? `<div class="message-contact">📱 ${msg.phone}</div>` : ''}
                                <div class="message-timestamp">${date}</div>
                            </div>
                            <span class="message-badge ${unread ? 'unread-badge' : 'read-badge'}">
                                ${unread ? '●' : '✓'}
                            </span>
                        </div>
                        <div class="message-text">${escapeHtml(msg.message)}</div>
                        <div class="message-actions">
                            ${!msg.read ? `<button class="btn btn-mark-read" onclick="markAsRead(${msg.id})">✓ Marcar como Lida</button>` : ''}
                            <button class="btn btn-delete" onclick="deleteMessage(${msg.id})">🗑️ Deletar</button>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function markAsRead(messageId) {
            try {
                const response = await fetch(`/api/contact/messages/${messageId}/read`, {
                    method: 'PUT'
                });
                if (response.ok) {
                    loadMessages();
                } else {
                    alert('Erro ao marcar como lida');
                }
            } catch (error) {
                console.error('Erro:', error);
                alert('Erro ao marcar como lida');
            }
        }

        async function deleteMessage(messageId) {
            if (confirm('Tem certeza que deseja deletar esta mensagem?')) {
                try {
                    const response = await fetch(`/api/contact/messages/${messageId}`, {
                        method: 'DELETE'
                    });
                    if (response.ok) {
                        loadMessages();
                    } else {
                        alert('Erro ao deletar mensagem');
                    }
                } catch (error) {
                    console.error('Erro:', error);
                    alert('Erro ao deletar mensagem');
                }
            }
        }

        function updateStats() {
            const unread = allMessages.filter(msg => !msg.read).length;
            document.getElementById('total-messages').textContent = allMessages.length;
            document.getElementById('unread-messages').textContent = unread;
        }

        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }

        loadMessages();
        setInterval(loadMessages, 5000);