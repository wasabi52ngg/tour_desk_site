document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
        const selects = document.querySelectorAll('select[name="tour_choice"], select[name="guide_choice"], select[name="location_choice"]');
        selects.forEach(select => {
        select.addEventListener('change', function() {
            form.submit();
        });
    });
});
