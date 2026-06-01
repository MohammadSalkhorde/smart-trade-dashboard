/**
 * SMARTTRADE CORE NETWORK - ANTI-CRASH RUNTIME MECHANISM
 * Isolated Render Blocks for Guaranteed Crypto UI Operations
 */

document.addEventListener('DOMContentLoaded', () => {
    // Ignition with micro-delay to ensure DOM elements have layout dimensions
    setTimeout(() => {
        SmartTradeCore.initNavbarGlow();
        SmartTradeCore.initLiveCounters();
        SmartTradeCore.initFixedCardGlow(); 
        SmartTradeCore.initTraderMatrixEngine(); 
    }, 50);
});

const SmartTradeCore = {

    initNavbarGlow: function() {
        const navbar = document.querySelector('.cyber-navbar');
        if (!navbar) return;

        window.addEventListener('scroll', () => {
            if (window.scrollY > 20) {
                navbar.style.background = 'rgba(6, 8, 10, 0.95)';
                navbar.style.padding = '12px 0';
                navbar.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.5)';
                navbar.style.borderColor = 'rgba(255, 255, 255, 0.16)';
            } else {
                navbar.style.background = 'rgba(6, 8, 10, 0.9)';
                navbar.style.padding = '16px 0';
                navbar.style.boxShadow = 'none';
                navbar.style.borderColor = 'var(--border-cyber)';
            }
        });
    },

    initLiveCounters: function() {
        const metrics = document.querySelectorAll('.telemetry-metric-value');
        metrics.forEach(metric => {
            try {
                const rawText = metric.textContent.trim();
                if (rawText.includes('<') || rawText.includes('Microseconds')) return;

                const targetNumber = parseFloat(rawText.replace(/[^0-9.]/g, ''));
                if (isNaN(targetNumber)) return;

                let startTimestamp = null;
                const duration = 1800; 

                const step = (timestamp) => {
                    if (!startTimestamp) startTimestamp = timestamp;
                    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
                    const easeProgress = 1 - Math.pow(1 - progress, 3);
                    const currentVal = Math.floor(easeProgress * targetNumber);

                    if (rawText.startsWith('$')) {
                        metric.textContent = '$' + currentVal.toLocaleString();
                    } else {
                        metric.textContent = currentVal.toLocaleString();
                    }

                    if (progress < 1) {
                        window.requestAnimationFrame(step);
                    } else {
                        metric.textContent = rawText; 
                    }
                };
                window.requestAnimationFrame(step);
            } catch (e) {
                console.error("Counter Error:", e);
            }
        });
    },

    initFixedCardGlow: function() {
        const cards = document.querySelectorAll('.quantum-feature-card, .card-trader-node');
        if (window.innerWidth < 992) return;

        cards.forEach(card => {
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left; 
                const y = e.clientY - rect.top;  
                card.style.setProperty('--x', `${x}px`);
                card.style.setProperty('--y', `${y}px`);
            });
        });
    },

    initTraderMatrixEngine: function() {
        // ۱. بخش مدیریت کارت‌ها و پاپ‌آپ‌ها
        const cardNodes = document.querySelectorAll('.card-trader-node');
        cardNodes.forEach(card => {
            try {
                const detailUrl = card.getAttribute('data-url');
                const triggerBtn = card.querySelector('.btn-replicate-trigger');
                const overlayForm = card.querySelector('.cyber-overlay-form-panel');
                const closeBtn = card.querySelector('.btn-close-cyber');
                
                card.addEventListener('click', function() { if (detailUrl) window.location.href = detailUrl; });
                
                if (triggerBtn && overlayForm) {
                    triggerBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        document.querySelectorAll('.cyber-overlay-form-panel').forEach(form => form.style.display = 'none');
                        overlayForm.style.display = 'block';
                    });
                }
                if (closeBtn && overlayForm) { closeBtn.addEventListener('click', function(e) { e.stopPropagation(); overlayForm.style.display = 'none'; }); }
                if (overlayForm) { overlayForm.addEventListener('click', function(e) { e.stopPropagation(); }); }
            } catch (err) { console.error("Card Core Error:", err); }
        });

        const btnCreateStrategy = document.getElementById('btnCreateStrategy');
        if (btnCreateStrategy) {
            btnCreateStrategy.addEventListener('click', function(e) {
                e.stopPropagation();
                const modalElement = document.getElementById('statusModal');
                if (modalElement) { new bootstrap.Modal(modalElement).show(); }
            });
        }

        // ۲. رندر قطاری چارت‌ها (Queue) با تفکیک کامل لوکال (دستی) و API (اتوماتیک)
        const roiNodes = Array.from(document.querySelectorAll('.roi-loading-text'));
        
        roiNodes.forEach((node, index) => {
            // ایجاد تأخیر ۶۰ میلی‌ثانیه‌ای پله‌ای برای جلوگیری از Rate Limit بایننس و کرش گرافیکی مرورگر
            setTimeout(() => {
                try {
                    const isManual = node.getAttribute('data-manual') === 'true';
                    const manualRoi = parseFloat(node.getAttribute('data-roi'));
                    const symbol = node.getAttribute('data-symbol') || 'BTCUSDT';
                    const parentCard = node.closest('.card-trader-node');
                    const chartWrapper = parentCard ? parentCard.querySelector('.chart-clean-wrapper-cyber') : null;
                    const canvas = parentCard ? parentCard.querySelector('.trader-mini-canvas') : null;

                    if (!canvas) return;

                    // ---------------------------------------------
                    // وضعیت دستی (داده‌ها کاملاً از جنگو دریافت می‌شود)
                    // ---------------------------------------------
                    if (isManual) {
                        const val = isNaN(manualRoi) ? 0 : manualRoi;
                        node.innerText = (val >= 0 ? '+' : '') + val.toFixed(2) + '%';
                        const isProfit = val >= 0;
                        node.style.color = isProfit ? '#00ff88' : '#ff3366';
                        if (chartWrapper) { chartWrapper.style.borderColor = isProfit ? 'rgba(0,255,136,0.2)' : 'rgba(255,51,102,0.2)'; }
                        
                        const rawData = canvas.getAttribute('data-history');
                        let localChartData = null;
                        try { if (rawData) localChartData = JSON.parse(rawData); } catch(e) {}
                        
                        SmartTradeCore.renderMiniChart(canvas, isProfit, localChartData);

                    // ---------------------------------------------
                    // وضعیت اتوماتیک (دریافت لایو از API بایننس)
                    // ---------------------------------------------
                    } else {
                        fetch(`https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=1d&limit=30`)
                            .then(res => {
                                if (!res.ok) throw new Error('Network or Rate-Limit issue');
                                return res.json();
                            })
                            .then(data => {
                                if (!data || data.length === 0) return;
                                
                                const openPrice = parseFloat(data[0][1]); 
                                const closePrice = parseFloat(data[data.length - 1][4]); 
                                const change = parseFloat((((closePrice - openPrice) / openPrice) * 100).toFixed(2));
                                
                                node.innerText = (change >= 0 ? '+' : '') + change + '%';
                                const isProfit = change >= 0;
                                node.style.color = isProfit ? '#00ff88' : '#ff3366';
                                if (chartWrapper) { chartWrapper.style.borderColor = isProfit ? 'rgba(0,255,136,0.2)' : 'rgba(255,51,102,0.2)'; }

                                const historyData = data.map(candle => parseFloat(candle[4]));
                                SmartTradeCore.renderMiniChart(canvas, isProfit, historyData);
                            })
                            .catch((err) => { 
                                console.warn(`Fallback triggered for ${symbol}:`, err);
                                node.innerText = '+0.00%'; 
                                node.style.color = '#00ff88';
                                SmartTradeCore.renderMiniChart(canvas, true, null);
                            });
                    }
                } catch (err) {
                    console.error("Critical Node Loop Error:", err);
                }
            }, index * 60);
        });
    },

    renderMiniChart: function(canvas, isProfit, customData = null) {
        if (!canvas) return;

        try {
            let chartData = [];
            if (customData && customData.length > 0) {
                chartData = customData;
            } else {
                const rawData = canvas.getAttribute('data-history');
                try { if (rawData) chartData = JSON.parse(rawData); } catch(e) {}
            }

            // لایه محافظتی بک‌آپ (Fallback Data)
            if (!chartData || chartData.length <= 1) {
                chartData = isProfit ? [10, 14, 12, 19, 17, 25, 22, 30] : [30, 25, 28, 18, 20, 12, 15, 8];
            }

            const lineColor = isProfit ? '#00ff88' : '#ff3366';
            const glowColor = isProfit ? 'rgba(0, 255, 136, 0.03)' : 'rgba(255, 51, 102, 0.03)';

            // 🌟 راهکار اصلی: جایگزینی فیزیکی گره DOM برای خلاص شدن قطعی از ارور Canvas is already in use
            const parent = canvas.parentNode;
            const newCanvas = document.createElement('canvas');
            newCanvas.className = canvas.className;
            if (canvas.id) newCanvas.id = canvas.id;
            newCanvas.setAttribute('data-history', JSON.stringify(chartData));
            
            parent.replaceChild(newCanvas, canvas);

            if (typeof Chart === 'undefined') {
                console.error("Chart.js is totally missing from this document!");
                return;
            }

            // رندر فوق‌سریع و بدون انیمیشن جهت لود پایدار ۱۰۰٪ همزمان کارت‌ها
            new Chart(newCanvas, {
                type: 'line',
                data: {
                    labels: chartData.map((_, i) => i),
                    datasets: [{
                        data: chartData,
                        borderColor: lineColor,
                        borderWidth: 2,
                        fill: true,
                        backgroundColor: glowColor,
                        pointRadius: 0,
                        pointHoverRadius: 0,
                        tension: 0.35
                    }]
                },
                options: { 
                    maintainAspectRatio: false,
                    responsive: true,
                    animation: false,
                    plugins: { legend: { display: false }, tooltip: { enabled: false } }, 
                    scales: { 
                        x: { display: false }, 
                        y: { display: false, grace: '5%' } 
                    }
                }
            });
        } catch (chartError) {
            console.error("Hard Render Engine Crash:", chartError);
        }
    }
};