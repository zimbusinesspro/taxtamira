document.addEventListener('DOMContentLoaded', () => {
    const languageSwitcher = document.getElementById('language-switcher');
    const currentLang = localStorage.getItem('language') || 'en';

    // Function to update content
    const updateContent = (lang) => {
        const elements = document.querySelectorAll('[data-i18n]');
        elements.forEach(element => {
            const key = element.getAttribute('data-i18n');
            if (translations[lang] && translations[lang][key]) {
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    element.placeholder = translations[lang][key];
                } else {
                    element.innerHTML = translations[lang][key];
                }
            }
        });
        document.documentElement.lang = lang === 'sn' ? 'sn' : 'en-US';
        localStorage.setItem('language', lang);

        // Update switcher active state if it's a select
        if (languageSwitcher && languageSwitcher.tagName === 'SELECT') {
            languageSwitcher.value = lang;
        }
    };

    // Initialize content
    updateContent(currentLang);

    // Event listener for language switcher
    if (languageSwitcher) {
        languageSwitcher.addEventListener('change', (e) => {
            updateContent(e.target.value);
        });
    }

    // Support for button-based switching if needed
    window.setLanguage = (lang) => {
        updateContent(lang);
    };
});
