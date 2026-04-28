
document.addEventListener('DOMContentLoaded', () => {
    let allArticles = [];
    let currentCat = 'all';
    let currentLang = 'all';

    const updateTimeEl = document.getElementById('update-time');
    const container = document.getElementById('news-container');

    // 读取数据
    fetch('news.json')
        .then(res => {
            if (!res.ok) throw new Error('网络错误');
            return res.json();
        })
        .then(data => {
            updateTimeEl.textContent = `🕒 最后更新：${data.last_updated} · 共 ${data.total} 条`;
            allArticles = data.articles || [];
            renderNews();
        })
        .catch(err => {
            container.innerHTML = '<div class="loading">新闻加载失败，请检查网络或稍后再试。</div>';
            console.error(err);
        });

    // 类别按钮
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentCat = btn.dataset.cat;
            renderNews();
        });
    });

    // 语言筛选
    document.getElementById('lang-filter').addEventListener('change', (e) => {
        currentLang = e.target.value;
        renderNews();
    });

    function renderNews() {
        let filtered = allArticles;

        // 分类筛选
        if (currentCat !== 'all') {
            filtered = filtered.filter(article => article.category === currentCat);
        }

        // 语言筛选（兼容 zh 和 zh_cn）
        if (currentLang !== 'all') {
            filtered = filtered.filter(article => {
                if (currentLang === 'zh') {
                    return article.lang === 'zh' || article.lang === 'zh_cn';
                }
                return article.lang === currentLang;
            });
        }

        if (!filtered.length) {
            container.innerHTML = '<div class="loading">没有匹配的新闻 🧐</div>';
            return;
        }

        container.innerHTML = filtered.map(article => {
            let summary = article.summary || '';
            if (summary.length > 120) summary = summary.substring(0, 120) + '...';
            summary = summary.replace(/<\/?[^>]+(>|$)/g, "");

            return `
            <div class="card">
                <div class="card-header">
                    <span class="tag ${article.category === '财报' ? 'finance' : ''}">${article.category}</span>
                    <span class="source-name">${article.source}</span>
                </div>
                <div class="card-title">
                    <a href="${article.url}" target="_blank" rel="noopener">${article.title}</a>
                </div>
                <div class="card-summary">${summary || '暂无摘要'}</div>
                <div class="card-footer">
                    <span>${article.published || '未知时间'}</span>
                    <span>${article.lang === 'zh' || article.lang === 'zh_cn' ? '🇨🇳 中文' : '🌐 English'}</span>
                </div>
            </div>`;
        }).join('');
    }
});
