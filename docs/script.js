document.addEventListener('DOMContentLoaded', () => {
    let allArticles = [];
    let currentCat = 'all';
    let currentLang = 'all';

    fetch('news.json')
        .then(res => res.json())
        .then(data => {
            document.getElementById('update-time').textContent = 
                `🕒 最后更新：${data.last_updated} · 共 ${data.total} 条`;
            allArticles = data.articles;
            renderNews();
        })
        .catch(err => {
            document.getElementById('news-container').innerHTML = 
                '<p>新闻加载失败，请稍后再试。</p>';
        });

    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelector('.filter-btn.active').classList.remove('active');
            e.target.classList.add('active');
            currentCat = e.target.dataset.cat;
            renderNews();
        });
    });

    document.getElementById('lang-filter').addEventListener('change', (e) => {
        currentLang = e.target.value;
        renderNews();
    });

    function renderNews() {
        const container = document.getElementById('news-container');
        container.innerHTML = '';
        
        let filtered = allArticles;
        if (currentCat !== 'all') {
            filtered = filtered.filter(a => a.category === currentCat);
        }
        if (currentLang !== 'all') {
            filtered = filtered.filter(a => a.lang === currentLang);
        }

        filtered.forEach(article => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <div class="card-header">
                    <span class="tag ${article.category === '财报' ? 'finance' : ''}">${article.category}</span>
                    <span style="font-size:0.75rem; color:#999;">${article.source}</span>
                </div>
                <div class="card-title">
                    <a href="${article.url}" target="_blank" rel="noopener">${article.title}</a>
                </div>
                <div class="card-summary">${article.summary || '暂无摘要'}</div>
                <div class="card-footer">
                    <span>${article.published ? article.published : ''}</span>
                    <span>${article.lang === 'zh' ? '🇨🇳 中文' : '🌐 English'}</span>
                </div>
            `;
            container.appendChild(card);
        });

        if (filtered.length === 0) {
            container.innerHTML = '<p style="text-align:center; margin-top:2rem;">没有匹配的新闻</p>';
        }
    }
});
