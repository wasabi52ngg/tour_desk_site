document.addEventListener('DOMContentLoaded', function() {
    const loader = document.getElementById('loading-overlay');
    if (!loader) return;

    let showTimer; // Таймер для показа лоадера
    let isLoading = false;
    const config = {
        delayBeforeShow: 300, // Задержка перед показом (300ms)
        minShowTime: 500      // Минимальное время отображения (500ms)
    };

    // Элементы для игнорирования
    const ignoreSelectors = [
        '#djDebug',
        '[data-no-loader]',
        '.dropdown-toggle',
        '#sidebar'
    ];

    function shouldTriggerLoader(element) {
        return !ignoreSelectors.some(selector =>
            element.closest(selector)
        ) && (
            element.tagName === 'A' ||
            element.closest('button') ||
            element.closest('form')
        );
    }

    function showLoader() {
        if (!isLoading) {
            isLoading = true;

            // Запускаем таймер показа с задержкой из config
            showTimer = setTimeout(() => {
                loader.style.display = 'flex';
                requestAnimationFrame(() => {
                    loader.style.opacity = '1';
                });
            }, config.delayBeforeShow);
        }
    }

    function hideLoader() {
        if (isLoading) {
            // Отменяем таймер показа если он еще не сработал
            clearTimeout(showTimer);

            isLoading = false;
            loader.style.opacity = '0';

            // Гарантированное время отображения
            setTimeout(() => {
                loader.style.display = 'none';
            }, config.minShowTime);
        }
    }

    function handleUserAction(e) {
        if (shouldTriggerLoader(e.target)) {
            showLoader();
        }
    }

    function handleFinishLoading() {
        // Вызывается при успешной загрузке
        hideLoader();
    }

    // Обработчики событий
    document.body.addEventListener('click', function(e) {
        if (e.target.tagName === 'A') {
            handleUserAction(e);
        }
    });

    document.body.addEventListener('submit', handleUserAction);

    window.addEventListener('beforeunload', showLoader);
    window.addEventListener('load', handleFinishLoading);
    window.addEventListener('error', handleFinishLoading);
    window.addEventListener('unhandledrejection', handleFinishLoading);

    // Отмена при переходе по якорю
    window.addEventListener('hashchange', handleFinishLoading);
});