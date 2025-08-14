document.addEventListener('DOMContentLoaded', function() {
    // 显示页面加载提示
    showNotification('🔄 正在加载数据...', 'info');
    
    // 延迟加载以避免阻塞页面渲染
    setTimeout(() => {
        loadDashboardStats();
        loadRecentActivities();
        setupQuickAddForms();
        
        // 隐藏加载提示
        setTimeout(() => {
            showNotification('✅ 页面加载完成', 'success');
        }, 500);
    }, 100);
});

function navigateTo(url) {
    location.href = url;
}

function goToCustomers() {
    navigateTo('/customers');
}

function goToRooms() {
    navigateTo('/rooms');
}

function goToContracts() {
    navigateTo('/contracts');
}

function goToPayments() {
    navigateTo('/payments');
}

function goToAddCustomer() {
    navigateTo('/customers/add');
}

function goToAddRoom() {
    navigateTo('/rooms/add');
}

function goToAddContract() {
    navigateTo('/contracts/add');
}

function goToAddPayment() {
    navigateTo('/payments/add');
}

function loadDashboardStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('totalCustomers').textContent = data.total_customers;
            document.getElementById('totalRooms').textContent = data.total_rooms;
            document.getElementById('activeContracts').textContent = data.active_contracts;
            document.getElementById('monthlyRevenue').textContent = '¥' + data.monthly_revenue.toLocaleString();
        })
        .catch(error => console.error('Error loading stats:', error));
}

function loadRecentActivities() {
    fetch('/api/activities')
        .then(response => response.json())
        .then(data => {
            const activityList = document.getElementById('activityList');
            activityList.innerHTML = '';
            
            data.activities.forEach(activity => {
                const activityItem = document.createElement('div');
                activityItem.className = 'activity-item';
                activityItem.innerHTML = `
                    <div class="activity-icon">
                        <i class="${activity.icon}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${activity.title}</div>
                        <div class="activity-time">${activity.time}</div>
                    </div>
                `;
                activityList.appendChild(activityItem);
            });
        })
        .catch(error => console.error('Error loading activities:', error));
}

function showQuickAdd() {
    document.getElementById('quickAddModal').style.display = 'block';
    loadCustomersForContract();
    loadRoomsForContract();
}

function closeQuickAdd() {
    document.getElementById('quickAddModal').style.display = 'none';
    resetQuickAddForms();
}

function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-btn');
    
    tabs.forEach(tab => tab.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabName + 'Tab').classList.add('active');
    event.target.classList.add('active');
}

function loadCustomersForContract() {
    fetch('/api/customers')
        .then(response => response.json())
        .then(data => {
            const select = document.querySelector('select[name="customer_id"]');
            select.innerHTML = '<option value="">选择客户</option>';
            data.customers.forEach(customer => {
                select.innerHTML += `<option value="${customer.id}">${customer.company_name}</option>`;
            });
        });
}

function loadRoomsForContract() {
    fetch('/api/rooms/available')
        .then(response => response.json())
        .then(data => {
            const select = document.querySelector('select[name="room_id"]');
            select.innerHTML = '<option value="">选择房间</option>';
            data.rooms.forEach(room => {
                select.innerHTML += `<option value="${room.id}">${room.room_number} (${room.area}㎡)</option>`;
            });
        });
}

function setupQuickAddForms() {
    document.getElementById('quickCustomerForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData);
        data.customer_id = 'CUST' + Date.now();
        
        fetch('/customers/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showNotification(result.message, 'success');
                closeQuickAdd();
                loadDashboardStats();
            } else {
                showNotification(result.message, 'error');
            }
        });
    });

    document.getElementById('quickRoomForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData);
        
        fetch('/rooms/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showNotification(result.message, 'success');
                closeQuickAdd();
                loadDashboardStats();
            } else {
                showNotification(result.message, 'error');
            }
        });
    });

    document.getElementById('quickContractForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const data = Object.fromEntries(formData);
        
        data.payment_frequency = '月付';
        data.deposit_contract = 0;
        data.deposit_received = 0;
        data.payment_day = 1;
        data.payment_method = '银行转账';
        data.invoice_method = '月结';
        data.remarks = '';
        
        fetch('/contracts/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                showNotification(result.message, 'success');
                closeQuickAdd();
                loadDashboardStats();
            } else {
                showNotification(result.message, 'error');
            }
        });
    });
}

function resetQuickAddForms() {
    document.getElementById('quickCustomerForm').reset();
    document.getElementById('quickRoomForm').reset();
    document.getElementById('quickContractForm').reset();
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // 添加图标
    const icon = document.createElement('i');
    switch(type) {
        case 'success':
            icon.className = 'fas fa-check-circle';
            break;
        case 'error':
            icon.className = 'fas fa-exclamation-circle';
            break;
        case 'warning':
            icon.className = 'fas fa-exclamation-triangle';
            break;
        case 'info':
            icon.className = 'fas fa-info-circle';
            break;
        default:
            icon.className = 'fas fa-bell';
    }
    
    const text = document.createElement('span');
    text.textContent = message;
    
    notification.appendChild(icon);
    notification.appendChild(text);
    document.body.appendChild(notification);
    
    // 自动移除通知
    setTimeout(() => {
        notification.classList.add('removing');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 4000);
    
    // 点击关闭通知
    notification.addEventListener('click', () => {
        notification.classList.add('removing');
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    });
}

function deleteItem(url, itemName) {
    if (confirm(`确定要删除这个${itemName}吗？`)) {
        fetch(url, {method: 'POST'})
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    showNotification(result.message, 'success');
                    location.reload();
                } else {
                    showNotification(result.message, 'error');
                }
            });
    }
}

function exportData(type) {
    const typeNames = {
        'customers': '客户数据',
        'rooms': '房间数据', 
        'contracts': '合同数据',
        'rent_plans': '租金计划数据'
    };
    
    const typeName = typeNames[type] || type;
    
    if (confirm(`📊 数据导出确认\n\n您即将导出：${typeName}\n\n导出文件将包含：\n• 当前所有${typeName}记录\n• 格式为Excel文件(.xlsx)\n• 文件名包含当前日期\n\n确定要导出吗？`)) {
        showNotification(`📤 正在导出${typeName}...`, 'info');
        window.location.href = `/export/${type}`;
    }
}

// 优化的搜索功能
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    const filter = input.value.trim().toUpperCase();
    const rows = table.getElementsByTagName('tr');
    let visibleCount = 0;

    // 清除之前的高亮
    clearSearchHighlights(table);

    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const cells = row.getElementsByTagName('td');
        let found = false;
        
        for (let j = 0; j < cells.length; j++) {
            const cell = cells[j];
            const cellText = cell.textContent.toUpperCase();
            
            if (filter && cellText.indexOf(filter) > -1) {
                found = true;
                // 高亮匹配的文本
                highlightSearchText(cell, filter);
            }
        }
        
        if (found || !filter) {
            row.classList.remove('hidden');
            visibleCount++;
        } else {
            row.classList.add('hidden');
        }
    }

    // 更新搜索结果统计
    updateSearchResults(inputId, visibleCount, rows.length - 1);
}

// 清除搜索高亮
function clearSearchHighlights(table) {
    const highlights = table.querySelectorAll('.search-highlight');
    highlights.forEach(highlight => {
        const parent = highlight.parentNode;
        parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
        parent.normalize(); // 合并相邻的文本节点
    });
}

// 高亮搜索文本
function highlightSearchText(element, searchText) {
    const text = element.textContent;
    const regex = new RegExp(`(${searchText})`, 'gi');
    const highlightedText = text.replace(regex, '<span class="search-highlight">$1</span>');
    element.innerHTML = highlightedText;
}

// 更新搜索结果统计
function updateSearchResults(inputId, visibleCount, totalCount) {
    const input = document.getElementById(inputId);
    const container = input.closest('.search-container');
    let resultCounter = container.querySelector('.search-results-counter');
    
    if (!resultCounter) {
        resultCounter = document.createElement('div');
        resultCounter.className = 'search-results-counter';
        resultCounter.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 5px;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        container.appendChild(resultCounter);
    }
    
    if (input.value.trim()) {
        resultCounter.textContent = `找到 ${visibleCount} 条记录，共 ${totalCount} 条`;
        resultCounter.style.opacity = '1';
    } else {
        resultCounter.style.opacity = '0';
    }
}

// 防抖搜索函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 初始化搜索框
function initializeSearchBox(inputId, tableId) {
    const input = document.getElementById(inputId);
    if (!input) return;
    
    // 创建搜索容器
    const container = document.createElement('div');
    container.className = 'search-container';
    input.parentNode.insertBefore(container, input);
    container.appendChild(input);
    
    // 添加搜索图标
    const searchIcon = document.createElement('i');
    searchIcon.className = 'fas fa-search search-icon';
    container.appendChild(searchIcon);
    
    // 添加清除按钮
    const clearBtn = document.createElement('i');
    clearBtn.className = 'fas fa-times search-clear';
    clearBtn.title = '清除搜索';
    container.appendChild(clearBtn);
    
    // 清除按钮事件
    clearBtn.addEventListener('click', () => {
        input.value = '';
        input.focus();
        searchTable(inputId, tableId);
    });
    
    // 防抖搜索
    const debouncedSearch = debounce(() => searchTable(inputId, tableId), 300);
    
    // 搜索事件
    input.addEventListener('input', debouncedSearch);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            input.value = '';
            searchTable(inputId, tableId);
            input.blur();
        }
    });
    
    // 添加搜索框样式类
    input.classList.add('search-input');
}

// 页面加载时初始化所有搜索框
document.addEventListener('DOMContentLoaded', function() {
    // 初始化各个页面的搜索框
    const searchConfigs = [
        { inputId: 'customerSearch', tableId: 'customerTable' },
        { inputId: 'roomSearch', tableId: 'roomTable' },
        { inputId: 'contractSearch', tableId: 'contractTable' },
        { inputId: 'paymentSearch', tableId: 'paymentTable' },
        { inputId: 'rentPlanSearch', tableId: 'rentPlanTable' }
    ];
    
    searchConfigs.forEach(config => {
        if (document.getElementById(config.inputId)) {
            initializeSearchBox(config.inputId, config.tableId);
        }
    });
});

window.onclick = function(event) {
    const modal = document.getElementById('quickAddModal');
    if (event.target === modal) {
        closeQuickAdd();
    }
}
