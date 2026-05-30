/**
 * SMARTTRADE CORE NETWORK - SYSTEM ANIMATIONS & COMPONENT LOGIC
 * Optimized for High-Fidelity Crypto UI Operations
 */

document.addEventListener('DOMContentLoaded', () => {
    // Execution Core Ignition
    SmartTradeCore.initNavbarGlow();
    SmartTradeCore.initLiveCounters();
    SmartTradeCore.initCardParallax();
});

const SmartTradeCore = {

    /**
     * 1. افکت تغییر ظاهر هدر هنگام اسکرول صفحه (Glassmorphic Scroll FX)
     */
    initNavbarGlow: function() {
        const navbar = document.querySelector('.cyber-navbar');
        if (!navbar) return;

        window.addEventListener('scroll', () => {
            if (window.scrollY > 20) {
                navbar.style.background = 'rgba(6, 8, 10, 0.9)';
                navbar.style.padding = '12px 0';
                navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.3)';
                navbar.style.borderColor = 'rgba(0, 255, 204, 0.1)';
            } else {
                navbar.style.background = 'rgba(6, 8, 10, 0.75)';
                navbar.style.padding = '16px 0';
                navbar.style.boxShadow = 'none';
                navbar.style.borderColor = 'var(--border-cyber)';
            }
        });
    },

    /**
     * 2. انیمیشن نرم شمارنده اعداد آماری صرافی (Premium Telemetry Counter)
     */
    initLiveCounters: function() {
        const metrics = document.querySelectorAll('.telemetry-metric-value');
        
        metrics.forEach(metric => {
            const rawText = metric.textContent.trim();
            
            // نادیده گرفتن مقادیری که زمان هستند (مثل execution speed کمتر از ۱۲ میکروثانیه)
            if (rawText.includes('<') || rawText.includes('Microseconds')) return;

            // استخراج عدد خالص از متن (حذف کاما و علامت دلار برای محاسبات انیمیشن)
            const targetNumber = parseFloat(rawText.replace(/[^0-9.]/g, ''));
            if (isNaN(targetNumber)) return;

            let startTimestamp = null;
            const duration = 2000; // مدت زمان انیمیشن به میلی‌ثانیه

            const step = (timestamp) => {
                if (!startTimestamp) startTimestamp = timestamp;
                const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                
                // فرمول Ease-Out Cubic برای نرم‌تر شدن انیمیشن در انتها
                const easeProgress = 1 - Math.pow(1 - progress, 3);
                const currentVal = Math.floor(easeProgress * targetNumber);

                // بازسازی فرمت پولی یا عددی اولیه برای نمایش تراز شده
                if (rawText.startsWith('$')) {
                    metric.textContent = '$' + currentVal.toLocaleString();
                } else {
                    metric.textContent = currentVal.toLocaleString();
                }

                if (progress < 1) {
                    window.requestAnimationFrame(step);
                } else {
                    metric.textContent = rawText; // تضمین نمایش دقیق مقدار نهایی بک‌اند
                }
            };

            // اجرای انیمیشن شمارش
            window.requestAnimationFrame(step);
        });
    },

    /**
     * 3. افکت سه بعدی و حرکت نرم کارت‌های مزایا با حرکت موس (Quantum Cards Parallax)
     */
    initCardParallax: function() {
        const cards = document.querySelectorAll('.quantum-feature-card');
        
        // این افکت فقط روی دسکتاپ فعال می‌شود تا در موبایل باعث افت فریم نشود
        if (window.innerWidth < 992) return;

        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left; // موقعیت X موس داخل کارت
                const y = e.clientY - rect.top;  // موقعیت Y موس داخل کارت

                // محاسبه زاویه چرخش بر اساس موقعیت موس
                const xc = rect.width / 2;
                const yc = rect.height / 2;
                const tiltX = (yc - y) / 12;
                const tiltY = (x - xc) / 12;

                // اعمال استایل تغییر زاویه کارت و جابجایی نور نئونی پس‌زمینه آن
                card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateY(-8px)`;
                
                const gradientBg = card.querySelector('::before');
                card.style.setProperty('--x', `${x}px`);
                card.style.setProperty('--y', `${y}px`);
            });

            // بازگرداندن کارت به حالت اولیه پس از خروج موس
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
            });
        });
    }
};