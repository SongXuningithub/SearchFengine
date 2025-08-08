// 主要的JavaScript功能
document.addEventListener('DOMContentLoaded', function() {
    // 初始化搜索建议功能
    initializeSearchSuggestions();
    
    // 初始化平滑滚动
    initializeSmoothScroll();
});

function initializeSearchSuggestions() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        let suggestionTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(suggestionTimeout);
            const query = this.value.trim();
            
            if (query.length < 2) {
                hideSuggestions(input);
                return;
            }
            
            suggestionTimeout = setTimeout(() => {
                fetchSuggestions(query, input);
            }, 300);
        });
        
        // 点击外部隐藏建议
        document.addEventListener('click', function(e) {
            if (!input.contains(e.target)) {
                hideSuggestions(input);
            }
        });
    });
}

function fetchSuggestions(query, input) {
    fetch(`/api/suggest?q=${encodeURIComponent(query)}&max=5`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.suggestions.length > 0) {
                showSuggestions(input, data.suggestions);
            } else {
                hideSuggestions(input);
            }
        })
        .catch(error => {
            console.error('Error fetching suggestions:', error);
        });
}

function showSuggestions(input, suggestions) {
    let suggestionsContainer = input.parentNode.querySelector('.search-suggestions');
    
    if (!suggestionsContainer) {
        suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'search-suggestions';
        input.parentNode.appendChild(suggestionsContainer);
    }
    
    suggestionsContainer.innerHTML = suggestions.map(suggestion => `
        <div class="suggestion-item" onclick="selectSuggestion('${suggestion}', this)">
            ${suggestion}
        </div>
    `).join('');
    
    suggestionsContainer.style.display = 'block';
}

function hideSuggestions(input) {
    const suggestionsContainer = input.parentNode.querySelector('.search-suggestions');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }
}

function selectSuggestion(suggestion, element) {
    const input = element.closest('.search-input-wrapper').querySelector('.search-input');
    input.value = suggestion;
    hideSuggestions(input);
    
    // 自动提交搜索
    const form = input.closest('.search-form');
    if (form) {
        form.submit();
    }
}

function initializeSmoothScroll() {
    // 平滑滚动到锚点
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// 工具函数
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

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatDate(timestamp) {
    return new Date(timestamp * 1000).toLocaleDateString('zh-CN');
}
