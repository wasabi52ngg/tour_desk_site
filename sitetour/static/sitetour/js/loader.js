document.addEventListener('DOMContentLoaded', function() {
    const loader = document.getElementById('loading-overlay');
    if(!loader) return;

    let loadingTimer;
    let isLoading = false;

    const config = {
        delayBeforeShow: 300,
        minShowTime: 500
    };

    function showLoader() {
        if (!isLoading) {
            isLoading = true;
            loadingTimer = setTimeout(() => {
                loader.style.display = 'flex';
                setTimeout(() => {
                    loader.style.opacity = '1';
                }, 50);
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

    function simulateLoading(duration = 2000) {
        showLoader();
        setTimeout(hideLoader, duration);
    }

    // Тестовая кнопка
    const testButton = document.querySelector('.test-loading-button');
    if(testButton) {
        testButton.addEventListener('click', () => {
            simulateLoading(3000);
        });
    }

    // Основные обработчики
    window.addEventListener('beforeunload', showLoader);
    window.addEventListener('load', () => setTimeout(hideLoader, config.minShowTime));

    document.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            if(link.href !== window.location.href) showLoader();
        });
    });
});