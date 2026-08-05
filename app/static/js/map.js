/**
 * Colombia SVG Map — Interactive heatmap
 * Reads data from window.__mapData and colors departments by participation count.
 */
(function () {
    "use strict";

    var data = window.__mapData || {};
    var tooltip = document.getElementById("mapTooltip");
    var tooltipDept = document.getElementById("tooltipDept");
    var tooltipCount = document.getElementById("tooltipCount");
    var svg = document.getElementById("svgColombia");
    if (!svg) return;

    // Find max for scale
    var maxCount = 0;
    var keys = Object.keys(data);
    for (var i = 0; i < keys.length; i++) {
        if (data[keys[i]] > maxCount) maxCount = data[keys[i]];
    }

    // Color scale thresholds (5 levels)
    function getLevel(count) {
        if (count === 0) return 0;
        if (maxCount === 0) return 0;
        var pct = count / maxCount;
        if (pct < 0.15) return 1;
        if (pct < 0.35) return 2;
        if (pct < 0.65) return 3;
        return 4;
    }

    // Apply colors
    var paths = svg.querySelectorAll(".dept-path");
    for (var j = 0; j < paths.length; j++) {
        var path = paths[j];
        var dept = path.getAttribute("data-dept");
        var count = data[dept] || 0;
        var level = getLevel(count);

        // Remove old fill classes
        path.classList.remove("dept-fill-0", "dept-fill-1", "dept-fill-2", "dept-fill-3", "dept-fill-4");
        path.classList.add("dept-fill-" + level);

        // Store count on element for tooltip
        path.setAttribute("data-count", count);

        // Hover events
        (function (p, d, c) {
            p.addEventListener("mouseenter", function (e) {
                tooltipDept.textContent = d;
                tooltipCount.textContent = c + " participacion" + (c !== 1 ? "es" : "");
                tooltip.classList.add("visible");
                p.classList.add("active");
            });

            p.addEventListener("mousemove", function (e) {
                var rect = svg.getBoundingClientRect();
                var x = e.clientX - rect.left + 12;
                var y = e.clientY - rect.top - 10;

                // Keep tooltip in bounds
                if (x + 160 > rect.width) x = x - 180;
                if (y < 0) y = y + 30;

                tooltip.style.left = x + "px";
                tooltip.style.top = y + "px";
            });

            p.addEventListener("mouseleave", function () {
                tooltip.classList.remove("visible");
                p.classList.remove("active");
            });
        })(path, dept, count);
    }
})();
