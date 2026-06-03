    (function() {
        if (window.cbt_monitored) return;
        window.cbt_monitored = true;
        
        const triggerStrike = () => {
            const buttons = document.querySelectorAll('button');
            for (let btn of buttons) {
                if (btn.innerText && btn.innerText.includes('__TRIGGER_STRIKE__')) {
                    btn.click();
                    break;
                }
            }
        };
        
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                triggerStrike();
            }
        });
        
        window.addEventListener('blur', () => {
            triggerStrike();
        });
    })();