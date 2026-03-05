/**
 * Medical Dashboard Utilities - extends UniversityDashboard (UD) with medical-specific helpers.
 * Requires university_app's dashboard_utils.js to be loaded first.
 */
(function () {
    var UD = window.UniversityDashboard;
    if (!UD) {
        console.warn('UniversityDashboard not found. Medical dashboard utils require university_app.');
        return;
    }

    /**
     * Show an error message inside a container.
     * @param {HTMLElement|jQuery} container
     * @param {string} [message]
     */
    UD.showError = function (container, message) {
        if (container && container.jquery) container = container[0];
        if (!container) return;
        var wrapper = document.createElement('div');
        wrapper.className = 'dashboard-error';
        wrapper.style.cssText = 'padding:24px;text-align:center;color:#e74c3c;';
        var icon = document.createElement('span');
        icon.className = 'fa fa-exclamation-circle';
        icon.style.cssText = 'font-size:1.5em;margin-bottom:8px;display:block;';
        wrapper.appendChild(icon);
        var text = document.createElement('div');
        text.textContent = message || __('Failed to load data.');
        wrapper.appendChild(text);
        container.innerHTML = '';
        container.appendChild(wrapper);
    };

    /**
     * Alias for renderKPIRow - render an array of KPI cards into a container.
     * @param {HTMLElement|jQuery} container
     * @param {Array<Object>} kpis - [{label, value, color, icon}]
     */
    UD.renderKPICards = function (container, kpis) {
        if (container && container.jquery) container = container[0];
        if (!container) return;
        container.innerHTML = '';
        return UD.renderKPIRow(container, kpis);
    };
})();
