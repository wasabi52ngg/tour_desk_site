document.addEventListener('DOMContentLoaded', function () {
    const loader = document.getElementById('loading-overlay');
    if (!loader) return;

    let showTimer;
    let isLoading = false;

    const config = {
        delayBeforeShow: 300,
        minShowTime: 500
    };

    // Функции управления лоадером
    window.showLoader = () => {
        if (isLoading) return;
        isLoading = true;
        showTimer = setTimeout(() => {
            loader.style.display = 'flex';
            requestAnimationFrame(() => {
                loader.style.opacity = '1';
            });
        }, config.delayBeforeShow);
    };

    window.hideLoader = () => {
        if (!isLoading) return;
        clearTimeout(showTimer);
        isLoading = false;
        loader.style.opacity = '0';
        setTimeout(() => {
            loader.style.display = 'none';
        }, config.minShowTime);
    };
});