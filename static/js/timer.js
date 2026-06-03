    (function() {
        let timeRemaining = {remaining};
        const countdownEl = document.getElementById('countdown');
        if (!countdownEl) return;
        
        if (window.cbt_timer_interval) {
            clearInterval(window.cbt_timer_interval);
        }
        
        function updateTimer() {
            if (timeRemaining <= 0) {
                countdownEl.innerText = "00:00";
                clearInterval(window.cbt_timer_interval);
                const buttons = document.querySelectorAll('button');
                for (let btn of buttons) {
                    if (btn.innerText && btn.innerText.includes('__TIMER_EXPIRED__')) {
                        btn.click();
                        break;
                    }
                }
                return;
            }
            
            let m = Math.floor(timeRemaining / 60);
            let s = timeRemaining % 60;
            
            countdownEl.innerText = 
                String(m).padStart(2, '0') + ":" + 
                String(s).padStart(2, '0');
                
            timeRemaining--;
        }
        
        updateTimer();
        window.cbt_timer_interval = setInterval(updateTimer, 1000);
    })();