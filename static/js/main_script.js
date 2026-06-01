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

document.addEventListener('DOMContentLoaded', function() {
    // خواندن روت کانتکست صفحه جهت اطمینان از صحت آدرس‌دهی و جلوگیری از خطای دیگر صفحات
    const contextEl = document.getElementById('trader-page-context');
    if (!contextEl) return;

    // استخراج متغیرها از کانتکست شیلد المنت با لایه امن کستینگ بولین
    const isStaff = contextEl.getAttribute('data-is-staff') === 'true';
    const isManual = contextEl.getAttribute('data-is-manual') === 'true';
    const traderId = parseInt(contextEl.getAttribute('data-trader-id') || '0');
    const csrfToken = contextEl.getAttribute('data-csrf');
    const updateUrl = contextEl.getAttribute('data-update-url');
    const roiElement = document.getElementById('display-roi');

    // محاسبه‌ی نام سورس رمز ارز بر اساس شناسه تریدر (همگام با سیستم جنگو تمپلیت)
    let symbol = "BTCUSDT";
    if (traderId % 5 === 0) symbol = "ADAUSDT";
    else if (traderId % 4 === 0) symbol = "BNBUSDT";
    else if (traderId % 3 === 0) symbol = "SOLUSDT";
    else if (traderId % 2 === 0) symbol = "ETHUSDT";

    // تابع هوشمند پردازش رنگ، سایه درخشندگی (Neon Glow) و تزریق استایل متون درصد
    const updateRoiDisplay = (value) => {
        if (!roiElement) return;
        const numValue = parseFloat(value);
        roiElement.innerText = (numValue >= 0 ? '+' : '') + numValue.toFixed(2) + '%';
        
        if (numValue >= 0) {
            roiElement.style.color = '#00ff88';
            roiElement.style.textShadow = '0 0 12px rgba(0, 255, 136, 0.4), 0 0 25px rgba(0, 255, 136, 0.15)';
        } else {
            roiElement.style.color = '#ff3366';
            roiElement.style.textShadow = '0 0 12px rgba(255, 51, 102, 0.4), 0 0 25px rgba(255, 51, 102, 0.15)';
        }
    };

    // سناریوی اول: حالت مدیریت دستی یا ادمین پلتفرم (اجرای موتور مستقل Chart.js)
    if (isStaff || isManual) {
        const chartCanvas = document.getElementById('traderChart');
        
        if (chartCanvas) {
            const ctx = chartCanvas.getContext('2d');
            
            // پارس امن آرایه برای چلوگیری از بروز خطای برک‌داون فایل جی‌اس
            let chartData;
            try {
                chartData = JSON.parse(contextEl.getAttribute('data-chart-data') || '[0, 5, 10, 8, 15]');
            } catch (e) {
                chartData = [0, 5, 10, 8, 15];
            }
            
            if (chartData && chartData.length > 0) {
                updateRoiDisplay(chartData[chartData.length - 1]);
            }

            const traderChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.map((_, i) => i + 1),
                    datasets: [{
                        data: chartData,
                        borderColor: '#0062ff',
                        backgroundColor: 'rgba(0, 98, 255, 0.05)',
                        fill: true,
                        tension: 0.4,
                        pointRadius: isStaff ? 6 : 0,
                        pointHoverRadius: isStaff ? 9 : 0,
                        pointBackgroundColor: '#00ff88',
                        pointBorderColor: '#ffffff',
                        borderWidth: 2.5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        dragData: isStaff ? {
                            round: 2,
                            onDrag: function(e, datasetIndex, index, value) {
                                if (index === chartData.length - 1) {
                                    updateRoiDisplay(value);
                                }
                            },
                            onDragEnd: function(e, datasetIndex, index, value) {
                                updateRoiDisplay(value);
                            }
                        } : false
                    },
                    scales: {
                        x: { display: false },
                        y: { 
                            display: true, 
                            grid: { color: 'rgba(255, 255, 255, 0.02)' },
                            beginAtZero: false, 
                            min: -100, 
                            max: 1000, 
                            ticks: {
                                stepSize: 200, 
                                display: true,
                                color: '#64748b',
                                font: { size: 10, family: 'Space Grotesk' },
                                callback: function(value) { return value + '%'; }
                            }
                        }
                    }
                }
            });

            // رویداد ادمین: ارسال بردار نقاط دستکاری شده روی چارت به بک‌انند
            if (isStaff && updateUrl) {
                document.getElementById('saveChart')?.addEventListener('click', function() {
                    const updatedData = traderChart.data.datasets[0].data;
                    fetch(updateUrl, {
                        method: "POST",
                        headers: { 
                            "Content-Type": "application/json", 
                            "X-CSRFToken": csrfToken 
                        },
                        body: JSON.stringify({ points: updatedData })
                    })
                    .then(res => res.json())
                    .then(data => { 
                        if(data.status === 'ok') alert("Matrix vectors committed successfully!"); 
                    });
                });
            }
        }
    }

    // سناریوی دوم: کاربر عادی + چارت اتوماتیک لایو (فچ دیتای حمایتی بایننس فقط در صورت نیاز)
    if (!isStaff && !isManual) {
        fetch(`https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=1d&limit=30`)
            .then(res => res.json())
            .then(data => {
                if (data && data.length > 0) {
                    const open = parseFloat(data[0][1]);
                    const close = parseFloat(data[data.length - 1][4]);
                    const change = (((close - open) / open) * 100).toFixed(2);
                    updateRoiDisplay(change);
                }
            })
            .catch(() => { 
                // کنترل خطای برون مرزی یا تایم‌اوت ریکوئست شبکه‌ای بایننس
                if(roiElement && roiElement.innerText === '0%') {
                    updateRoiDisplay(0.00); 
                }
            });
    }
});

/* ===================================================
   توابع شیلد محافظتی و مدیریت مودال تخصیص بودجه کپی کلاینت
   =================================================== */
function openCopyFormDetail() {
    const modal = document.getElementById('copyModalContainer');
    if (modal) modal.style.display = 'flex';
}

function closeCopyFormDetail() {
    const modal = document.getElementById('copyModalContainer');
    if (modal) modal.style.display = 'none';
}

// ناوبری بستن لایه مودال با کلیک روی فضای تاریک و شیشه‌ای پس‌زمینه
window.addEventListener('click', function(event) {
    const modal = document.getElementById('copyModalContainer');
    if (modal && event.target === modal) {
        closeCopyFormDetail();
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const priceRows = document.querySelectorAll('.cyber-table-row');
    
    // شبیه‌ساز فلش افکت مارکت برای زنده نشان دادن دیتای جدول
    setInterval(() => {
        // انتخاب تصادفی یک ردیف برای اعمال پالس نوری
        const randomIndex = Math.floor(Math.random() * priceRows.length);
        const targetRow = priceRows[randomIndex];
        
        if(targetRow) {
            const priceSpan = targetRow.querySelector('.price-td span');
            priceSpan.style.transition = 'text-shadow 0.2s ease, color 0.2s ease';
            priceSpan.style.color = '#38bdf8';
            priceSpan.style.textShadow = '0 0 10px #38bdf8';
            
            setTimeout(() => {
                priceSpan.style.color = '#ffffff';
                priceSpan.style.textShadow = 'none';
            }, 400);
        }
    }, 3000); // هر ۳ ثانیه یک نود شبکه رندوم پالس می‌زند
});

/**
 * ==========================================================================
 * CYBERPUNK REAL-TIME PORTFOLIO TRACKER (SAFE INDEPENDENT NODE)
 * ==========================================================================
 */
document.addEventListener('DOMContentLoaded', function() {
    // احاطه کردن کل منطق اسکریپت درون try-catch برای تضمین عدم سرایت خطا به بقیه فایل‌ها
    try {
        const contextElem = document.getElementById('cyber-js-context');
        if (!contextElem) return; // اگر المان‌های این صفحه نبودند، اسکریپت متوقف شود

        // استخراج آدرس‌ها و توکن امنیتی از کانتینر HTML
        const syncUrl = contextElem.getAttribute('data-sync-url') || '/trading/update-pnl-ajax/';
        const csrfToken = contextElem.getAttribute('data-csrf-token') || '';

        // ۱. استخراج اطلاعات پوزیشن‌ها از ساختار جدول DOM (جایگزین حلقه جنگو)
        const traderRows = document.querySelectorAll('.trader-node-row');
        const traderState = [];

        traderRows.forEach(row => {
            const id = row.getAttribute('data-id');
            const entryRoi = parseFloat(row.getAttribute('data-entry-roi')) || 0;
            const investment = parseFloat(row.getAttribute('data-investment')) || 0;
            const currentPnl = parseFloat(row.getAttribute('data-last-pnl')) || 0;
            const loopCounter = parseInt(row.getAttribute('data-loop-counter')) || 1;

            // تشخیص زوج یا فرد بودن مارکت‌ها برای همگام‌سازی جفت ارز بایننس
            let symbol = "BTCUSDT";
            if (loopCounter % 5 === 0) symbol = "ADAUSDT";
            else if (loopCounter % 4 === 0) symbol = "BNBUSDT";
            else if (loopCounter % 3 === 0) symbol = "SOLUSDT";
            else if (loopCounter % 2 === 0) symbol = "ETHUSDT";

            traderState.push({
                id: id,
                entryRoi: entryRoi,
                symbol: symbol,
                currentPnl: currentPnl,
                investment: investment,
                isManual: false,
                lastPrice: 0
            });
        });

        // ۲. تابع به‌روزرسانی نمایشی سطر هر تریدر (سود/زیان و ارزش فعلی)
        function updateUI(item) {
            const invElem = document.getElementById(`investment-val-${item.id}`);
            const profitElem = document.getElementById(`profit-val-${item.id}`);
            if (!invElem || !profitElem) return;

            const displayPnl = Math.max(item.currentPnl, -100);
            const currentPositionValue = item.investment * (1 + (displayPnl / 100));
            
            // نمایش قیمت لحظه‌ای پوزیشن با فرمت پولی
            invElem.innerText = `$${Math.max(0, currentPositionValue).toLocaleString(undefined, {
                minimumFractionDigits: 2, 
                maximumFractionDigits: 2
            })}`;
            
            // استایل‌دهی نئونی به درصد سود/ضرر
            profitElem.innerText = (displayPnl >= 0 ? '+' : '') + displayPnl.toFixed(2) + '%';
            profitElem.style.color = displayPnl >= 0 ? "#00ff88" : "#ff3366";
            profitElem.setAttribute('data-last-pnl', displayPnl.toFixed(4));
        }

        // ۳. تابع آپدیت کارت بالانس اصلی و میانگین سود سبد (Live Portfolio PnL)
        function updateTotalPortfolio() {
            const balanceElem = document.getElementById('total-balance-display');
            const totalPnlElem = document.getElementById('total-pnl-display');
            if (!balanceElem) return;

            const walletCash = parseFloat(balanceElem.getAttribute('data-initial-balance')) || 0;
            let currentInvestmentsValue = 0;
            let sumPnlPercent = 0;

            traderState.forEach(t => {
                const limitedPnl = Math.max(t.currentPnl, -100);
                const positionValue = t.investment * (1 + (limitedPnl / 100));
                
                currentInvestmentsValue += positionValue;
                sumPnlPercent += limitedPnl;
            });

            const totalEquity = Math.max(0, walletCash + currentInvestmentsValue);

            // رندر عدد کل روی کارت اعتباری دارک پلتفرم
            balanceElem.innerText = `$${totalEquity.toLocaleString(undefined, {
                minimumFractionDigits: 2, 
                maximumFractionDigits: 2
            })}`;

            // رندر درصد کلی مانیتورینگ PnL سبد
            if (totalPnlElem) {
                const avgPnl = traderState.length > 0 ? (sumPnlPercent / traderState.length) : 0;
                const displayAvg = Math.max(0, avgPnl);
                
                totalPnlElem.innerText = displayAvg.toFixed(2) + '%';
                totalPnlElem.style.color = displayAvg > 0 ? "#00ff88" : "#94a3b8";
            }
        }

        // ۴. متد ارسال بک‌گراند دیتا به بک‌اند بدون بارگذاری مجدد (AJAX Sync)
        async function syncToServer(id, pnl) {
            try {
                if (!syncUrl) return;
                await fetch(syncUrl, { 
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json', 
                        'X-CSRFToken': csrfToken 
                    },
                    body: JSON.stringify({ id: id, pnl: pnl.toFixed(4) })
                });
            } catch (e) { 
                console.warn("Matrix background sync paused temporarily."); 
            }
        }

        // ۵. پروتکل چرخه‌ای دریافت قیمت لایو تیکرها از صرافی بایننس
        async function tick() {
            for (let item of traderState) {
                try {
                    // استعلام آخرین وضعیت تریدر از پورت اختصاصی سرور خودت
                    const responseSync = await fetch(`/trading/get-latest-pnl/${item.id}/`);
                    const serverData = await responseSync.json();
                    
                    const currentTraderRoi = serverData.trader_roi; 
                    item.isManual = serverData.is_manual;
                    let calculatedUserPnl = currentTraderRoi - item.entryRoi;

                    // اگر پوزیشن بر روی حالت اتوماتیک صرافی قرار داشت
                    if (!item.isManual) {
                        const resBinance = await fetch(`https://api.binance.com/api/v3/ticker/price?symbol=${item.symbol}`);
                        const dataBinance = await resBinance.json();
                        const freshPrice = parseFloat(dataBinance.price);

                        if (item.lastPrice > 0) {
                            calculatedUserPnl += ((freshPrice - item.lastPrice) / item.lastPrice) * 100;
                        }
                        item.lastPrice = freshPrice;
                    }

                    item.currentPnl = calculatedUserPnl;
                    updateUI(item);
                    syncToServer(item.id, item.currentPnl);

                } catch (e) { 
                    console.error(`Tick connection lost for node sequence: ${item.symbol}`, e); 
                }
            }
            updateTotalPortfolio();
        }

        // کانفینگ و لودینگ اولیه پورتفولیو مانیتورینگ
        if (traderState.length > 0) {
            traderState.forEach(item => updateUI(item));
            updateTotalPortfolio();
            tick(); 
            // اجرای جادوی ریل‌تایم هر ۳ ثانیه یک‌بار
            setInterval(tick, 3000);
        }

        // ۶. اینترسپتور دکمه توقف فوری پوزیشن کپی‌ترید (STOP BUTTON INTERCEPTOR)
        document.addEventListener('click', function(e) {
            if (e.target && e.target.classList.contains('stop-copy-btn')) {
                const id = e.target.getAttribute('data-id');
                const profitElem = document.getElementById(`profit-val-${id}`);
                const finalPnl = profitElem ? profitElem.getAttribute('data-last-pnl') : "0";
                
                if (confirm("Are you sure you want to stop terminating this copy trading link?")) {
                    const input = document.getElementById(`live-pnl-input-${id}`);
                    const form = document.getElementById(`stop-form-${id}`);
                    if (input && form) { 
                        input.value = finalPnl; 
                        form.submit(); 
                    }
                }
            }
        });

    } catch (globalError) {
        console.error("Critical recovery protocol engaged. Portfolio Core Isolated: ", globalError);
    }
});


/**
 * ==========================================================================
 * SMARTTRADE PREMIUM AUTH LAYER - ISOLATED PROTOCOL
 * ==========================================================================
 */
document.addEventListener('DOMContentLoaded', function() {
    try {
        const forgotBtn = document.getElementById('forgot-password-btn');
        const modalElement = document.getElementById('forgotModal');
        const modalBody = document.getElementById('forgotModalBody');

        if (!forgotBtn || !modalElement || !modalBody) return;

        // وهله‌سازی اصولی کامپوننت مودال بوت‌استرپ
        const bootstrapForgotModal = new bootstrap.Modal(modalElement);

        forgotBtn.addEventListener('click', function(e) {
            e.preventDefault();

            // همگام‌سازی استخراج فیلد نام کاربری یا ایمیل
            const accountInput = document.querySelector('input[name*="username"]') || 
                                 document.querySelector('input[name*="email"]') || 
                                 document.querySelector('input[type="text"]');
            
            const accountValue = accountInput ? accountInput.value.trim() : "";

            // ایمن‌سازی درخت DOM: انتقال لایه مودال به روت بادی برای فرار از z-index کانتینرها
            if (modalElement.parentElement !== document.body) {
                document.body.appendChild(modalElement);
            }

            if (accountValue === "") {
                // رندر حالت خطای عدم وارد کردن شناسه کاربری
                modalBody.innerHTML = `
                    <div class="mb-4 d-inline-flex align-items-center justify-content-center" 
                         style="width: 74px; height: 74px; background: rgba(255, 51, 102, 0.1); color: #ff3366; border-radius: 50%; font-size: 2rem; border: 1px solid rgba(255, 51, 102, 0.2);">
                        <i class="bi bi-exclamation-triangle-fill"></i>
                    </div>
                    <h4 class="fw-bold text-white mb-2">Identifier Required</h4>
                    <p class="text-muted small mb-4" style="line-height: 1.6;">Please input your network account email or username inside the login field first to request a recovery link.</p>
                    <button type="button" class="btn btn-premium-submit w-100 py-2.5 rounded-pill" data-bs-dismiss="modal" style="background: #ff3366; box-shadow: 0 10px 25px rgba(255, 51, 102, 0.3);">
                        Return to Authentication
                    </button>
                `;
            } else {
                // رندر تاییدیه ارسال موفق لینک ریکاوری به مقصد کاربر
                modalBody.innerHTML = `
                    <div class="mb-4 d-inline-flex align-items-center justify-content-center" 
                         style="width: 74px; height: 74px; background: rgba(0, 163, 255, 0.1); color: #00a3ff; border-radius: 50%; font-size: 2rem; border: 1px solid rgba(0, 163, 255, 0.2);">
                        <i class="bi bi-shield-check"></i>
                    </div>
                    <h4 class="fw-bold text-white mb-2">Transmission Dispatched</h4>
                    <p class="text-muted small mb-4" style="line-height: 1.6;">Secure link assigned. If an account matches, recovery data will route to:<br><span class="fw-bold text-info" style="word-break: break-all;">${escapeHtml(accountValue)}</span></p>
                    <button type="button" class="btn btn-premium-submit w-100 py-2.5 rounded-pill" data-bs-dismiss="modal">
                        Acknowledge Protocol
                    </button>
                `;
            }

            bootstrapForgotModal.show();
        });

        // تابع کمکی برای پاکسازی استرینگ ورودی و جلوگیری از XSS در جاوااسکریپت تکست پرووایدر
        function escapeHtml(str) {
            return str.replace(/&/g, "&amp;")
                      .replace(/</g, "&lt;")
                      .replace(/>/g, "&gt;")
                      .replace(/"/g, "&quot;")
                      .replace(/'/g, "&#039;");
        }

    } catch (err) {
        console.error("Auth UI interaction module halted.", err);
    }
});

/**
 * ==========================================================================
 * SMARTTRADE - PREMIUM INTERACTION SECURITY MODULE
 * ==========================================================================
 */
document.addEventListener('DOMContentLoaded', function() {
    try {
        const registerForm = document.getElementById('premium-register-form');
        const passwordFields = document.querySelectorAll('input[type="password"]');

        if (!registerForm) return;

        // ماژول امنیتی ۱: بهبود تعامل بصری زمان تایپ پسورد (میتوان در صورت نیاز دکمه چشمک اضافه کرد)
        passwordFields.forEach(field => {
            field.addEventListener('focus', function() {
                this.parentElement.style.boxShadow = "0 0 15px rgba(0, 163, 255, 0.08)";
            });
            
            field.addEventListener('blur', function() {
                this.parentElement.style.boxShadow = "none";
            });
        });

        // ماژول امنیتی ۲: انیمیشن کلیک نرم روی دکمه سابمیت برای ملو کردن فرآیند پردازش شبکه
        registerForm.addEventListener('submit', function() {
            const submitBtn = this.querySelector('.btn-register-action');
            if (submitBtn) {
                submitBtn.style.pointerEvents = 'none';
                submitBtn.style.opacity = '0.85';
                const labelSpan = submitBtn.querySelector('span');
                if (labelSpan) {
                    labelSpan.innerText = 'Syncing Node Framework...';
                }
            }
        });

    } catch (error) {
        console.warn("Register UI enhancement caught localized exception.", error);
    }
});