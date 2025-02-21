document.addEventListener('DOMContentLoaded', function() {
    const loader = document.getElementById('loading-overlay');
    if(!loader) return;

    let loadingTimer;
    let isLoading = false;

    const config = {
        delayBeforeShow: 300,
        minShowTime: 500
    };

    // Добавляем проверку кликов внутри сайдбара
    function shouldIgnoreClick(element) {
        return !!element.closest('#sidebar, .dropdown-toggle');
    }

    function showLoader() {
        if (!isLoading) {
            isLoading = true;
            loadingTimer = setTimeout(() => {
                loader.style.display = 'flex';
                requestAnimationFrame(() => {
                    loader.style.opacity = '1';
                });
            }, config.delayBeforeShow);
        }
    }

    function hideLoader() {
        if (isLoading) {
            clearTimeout(loadingTimer);
            isLoading = false;
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 500);
        }
    }

    // Обновляем обработчик ссылок
    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', function(e) {
            if (shouldIgnoreClick(this)) return;
            if(this.href !== window.location.href) showLoader();
        });
    });

    // Остальной код без изменений...
});