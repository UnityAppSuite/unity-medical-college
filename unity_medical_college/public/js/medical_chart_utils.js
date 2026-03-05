/**
 * Medical Chart Utilities - extends UniversityDashboard (UD) with medical-specific chart helpers.
 * Requires university_app's chart_utils.js to be loaded first.
 */
(function () {
    var UD = window.UniversityDashboard;
    if (!UD) {
        console.warn('UniversityDashboard not found. Medical chart utils require university_app.');
        return;
    }

    /**
     * Alias for createBarChart.
     * @param {HTMLElement|jQuery} container
     * @param {Object} config - {title, labels, datasets, colors, height}
     */
    UD.renderBarChart = function (container, config) {
        return UD.createBarChart(container, config);
    };

    /**
     * Render a donut chart. Accepts either config.values or config.datasets[0].values.
     * @param {HTMLElement|jQuery} container
     * @param {Object} config - {title, labels, datasets:[{values}], colors, height}
     */
    UD.renderDonutChart = function (container, config) {
        var values = config.values;
        if (!values && config.datasets && config.datasets[0]) {
            values = config.datasets[0].values;
        }
        return UD.createDonutChart(container, {
            title: config.title,
            labels: config.labels,
            values: values,
            colors: config.colors,
            height: config.height
        });
    };
})();
