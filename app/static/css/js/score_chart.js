document.addEventListener("DOMContentLoaded", function () {

    // ── Animated score counter ──
    const scoreEl = document.querySelector(".score-number");
    if (scoreEl) {
        const target = parseFloat(scoreEl.textContent);
        let current = 0;
        const duration = 1200;
        const stepTime = 16;
        const steps = duration / stepTime;
        const increment = target / steps;

        const counter = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(counter);
            }
            scoreEl.textContent = Math.round(current);
        }, stepTime);
    }

    // ── Radar chart ──
    const radarCanvas = document.getElementById("radarChart");
    if (!radarCanvas) return;

    const scores   = JSON.parse(radarCanvas.dataset.scores);
    const maxes    = JSON.parse(radarCanvas.dataset.maxes);
    const labels   = JSON.parse(radarCanvas.dataset.labels);
    const percents = scores.map((s, i) => Math.round((s / maxes[i]) * 100));

    new Chart(radarCanvas, {
        type: "radar",
        data: {
            labels: labels,
            datasets: [{
                label: "Your Resume",
                data: percents,
                backgroundColor: "rgba(37, 99, 235, 0.12)",
                borderColor: "rgba(37, 99, 235, 0.9)",
                borderWidth: 2,
                pointBackgroundColor: "rgba(37, 99, 235, 1)",
                pointRadius: 5,
                pointHoverRadius: 7,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    min: 0,
                    max: 100,
                    ticks: {
                        stepSize: 25,
                        display: false
                    },
                    grid: { color: "rgba(0,0,0,0.06)" },
                    pointLabels: {
                        font: { size: 11, family: "'DM Sans', sans-serif" },
                        color: "#475569"
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => ` ${ctx.raw}%`
                    }
                }
            }
        }
    });

    // ── Animate progress bars ──
    document.querySelectorAll(".progress-bar div").forEach(bar => {
        const width = bar.style.width;
        bar.style.width = "0%";
        setTimeout(() => {
            bar.style.transition = "width 0.8s ease";
            bar.style.width = width;
        }, 300);
    });
});