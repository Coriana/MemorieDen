let selectedUserId = null;
const historyModal = new bootstrap.Modal(document.getElementById('historyModal'));

// Load users when the page loads
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
    loadAllMemories();
});

// User Management Functions
async function loadUsers() {
    try {
        const response = await fetch('/users/all');
        const data = await response.json();
        const userList = document.getElementById('userList');
        userList.innerHTML = data.users.map(user => `
            <a href="#" class="list-group-item list-group-item-action ${user.user_id === selectedUserId ? 'active' : ''}"
               onclick="selectUser('${user.user_id}')">
                ${user.user_id}
            </a>
        `).join('');
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Failed to load users');
    }
}

async function addUser() {
    const userIdInput = document.getElementById('newUserId');
    const userId = userIdInput.value.trim();
    
    if (!userId) {
        alert('Please enter a user ID');
        return;
    }

    try {
        const response = await fetch('/users/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId })
        });

        if (response.ok) {
            userIdInput.value = '';
            loadUsers();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to add user');
        }
    } catch (error) {
        console.error('Error adding user:', error);
        alert('Failed to add user');
    }
}

function selectUser(userId) {
    selectedUserId = selectedUserId === userId ? null : userId;
    loadUsers();
    loadAllMemories();
}

// Memory Management Functions
async function addMemory() {
    const content = document.getElementById('memoryContent').value.trim();
    const metadataStr = document.getElementById('memoryMetadata').value.trim();
    
    if (!content) {
        alert('Please enter memory content');
        return;
    }

    let metadata = null;
    if (metadataStr) {
        try {
            metadata = JSON.parse(metadataStr);
        } catch (error) {
            alert('Invalid JSON in metadata field');
            return;
        }
    }

    try {
        const response = await fetch('/memories/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                content: content,
                user_id: selectedUserId,
                metadata: metadata
            })
        });

        if (response.ok) {
            document.getElementById('memoryContent').value = '';
            document.getElementById('memoryMetadata').value = '';
            loadAllMemories();
        } else {
            const error = await response.json();
            alert(error.error || 'Failed to add memory');
        }
    } catch (error) {
        console.error('Error adding memory:', error);
        alert('Failed to add memory');
    }
}

async function searchMemories() {
    const query = document.getElementById('searchQuery').value.trim();
    
    if (!query) {
        loadAllMemories();
        return;
    }

    try {
        const url = new URL('/memories/search', window.location.origin);
        url.searchParams.append('query', query);
        if (selectedUserId) {
            url.searchParams.append('user_id', selectedUserId);
        }

        const response = await fetch(url);
        const data = await response.json();
        displayMemories(data.memories, query);
    } catch (error) {
        console.error('Error searching memories:', error);
        alert('Failed to search memories');
    }
}

async function loadAllMemories() {
    try {
        const url = new URL('/memories/all', window.location.origin);
        if (selectedUserId) {
            url.searchParams.append('user_id', selectedUserId);
        }

        const response = await fetch(url);
        const data = await response.json();
        displayMemories(data.memories);
    } catch (error) {
        console.error('Error loading memories:', error);
        alert('Failed to load memories');
    }
}

function displayMemories(memories, searchQuery = '') {
    const memoriesList = document.getElementById('memoriesList');
    
    if (!memories.length) {
        memoriesList.innerHTML = '<p class="text-muted">No memories found.</p>';
        return;
    }

    memoriesList.innerHTML = memories.map(memory => {
        let content = memory.content;
        if (searchQuery) {
            // Escape the search query to handle special regex characters
            const escapedQuery = searchQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            const regex = new RegExp(`(${escapedQuery})`, 'gi');
            content = content.replace(regex, '<span class="search-highlight">$1</span>');
        }

        return `
            <div class="memory-card">
                <div class="memory-content">${content}</div>
                ${memory.metadata ? 
                    `<div class="memory-metadata">Metadata: ${JSON.stringify(memory.metadata)}</div>` : 
                    ''}
                ${memory.score !== undefined ? 
                    `<div class="memory-score">Relevance Score: ${memory.score}</div>` : 
                    ''}
                <div class="memory-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="showHistory('${memory.memory_id}')">
                        View History
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="editMemory('${memory.memory_id}')">
                        Edit
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

async function showHistory(memoryId) {
    try {
        const response = await fetch(`/memories/history/${memoryId}`);
        const data = await response.json();
        
        const historyContent = document.getElementById('historyContent');
        if (!data.history.length) {
            historyContent.innerHTML = '<p class="text-muted">No history available.</p>';
        } else {
            historyContent.innerHTML = data.history.map(record => `
                <div class="history-item">
                    <div class="history-timestamp">${new Date(record.updated_at).toLocaleString()}</div>
                    <div class="text-danger memory-content">- ${record.prev_value}</div>
                    <div class="text-success memory-content">+ ${record.new_value}</div>
                </div>
            `).join('');
        }
        
        historyModal.show();
    } catch (error) {
        console.error('Error loading memory history:', error);
        alert('Failed to load memory history');
    }
}

async function editMemory(memoryId) {
    const dialog = document.createElement('div');
    dialog.innerHTML = `
        <div class="modal fade" id="editMemoryModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit Memory</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <textarea class="form-control memory-content memory-edit-textarea" rows="5" id="editMemoryContent"></textarea>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" id="saveMemoryEdit">Save</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(dialog);

    const memories = await fetch('/memories/all').then(r => r.json());
    const memory = memories.memories.find(m => m.memory_id === memoryId);
    
    const modalElement = document.getElementById('editMemoryModal');
    const modal = new bootstrap.Modal(modalElement);
    const textarea = document.getElementById('editMemoryContent');
    textarea.value = memory?.content || '';
    
    document.getElementById('saveMemoryEdit').onclick = async () => {
        const newContent = textarea.value;
        if (!newContent) return;

        try {
            const response = await fetch('/memories/update', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    memory_id: memoryId,
                    new_content: newContent
                })
            });

            if (response.ok) {
                modal.hide();
                loadAllMemories();
            } else {
                const error = await response.json();
                alert(error.error || 'Failed to update memory');
            }
        } catch (error) {
            console.error('Error updating memory:', error);
            alert('Failed to update memory');
        }
    };

    modalElement.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(dialog);
    });

    modal.show();
}