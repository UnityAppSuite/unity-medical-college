// Clinical Coordinator Dashboard — posting strength, case logs, OSCE
// Gated: only renders when Medical College Settings.enable_medical_module = 1

frappe.pages['clinical-coordinator-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Clinical Coordinator Dashboard',
		single_column: true
	});
	new ClinicalCoordinatorDashboard(page);
};

class ClinicalCoordinatorDashboard {
	constructor(page) {
		this.page = page;
		this.UD = window.UniversityDashboard;
		this.API_BASE = 'unity_medical_college.unity_medical_college.dashboard_api';
		this.UA_API_BASE = 'university_app.university_app.dashboard_api';
		this.filters = {};
		this._initialized = false;
		this.init();
	}

	async init() {
		try {
			var enabled = await this.UD.callAPI(this.API_BASE + '.clinical_api.check_medical_enabled');
			if (!enabled) {
				this._showNotConfigured();
				return;
			}
		} catch (e) {
			this._showNotConfigured();
			return;
		}

		this.page.set_secondary_action(__('Refresh'), () => this.refresh());
		this.setupFilters();
		this._initialized = true;
		this.buildLayout();
		await this.setDefaultFilters();
		this.refresh();
	}

	_showNotConfigured() {
		$(this.page.body).html(
			'<div style="padding:60px;text-align:center;">' +
			'<h3 style="color:#888;">' + __('Medical Module Not Configured') + '</h3>' +
			'<p>' + __('Enable the Medical Module in Medical College Settings to use this dashboard.') + '</p>' +
			'<a href="/app/medical-college-settings" class="btn btn-primary">' + __('Open Settings') + '</a>' +
			'</div>'
		);
	}

	setupFilters() {
		var self = this;

		this.page.add_field({
			fieldname: 'academic_term',
			label: __('Academic Term'),
			fieldtype: 'Link',
			options: 'Academic Term',
			change: function () {
				self.filters.academic_term = self.page.fields_dict.academic_term.get_value();
				self.refresh();
			}
		});
	}

	async setDefaultFilters() {
		try {
			var defaults = await this.UD.callAPI(this.UA_API_BASE + '.base.get_current_academic_period');
			if (defaults && defaults.academic_term) {
				this.filters.academic_term = defaults.academic_term;
				this.page.fields_dict.academic_term.set_value(defaults.academic_term);
			}
		} catch (e) {}
	}

	buildLayout() {
		var container = document.createElement('div');
		container.className = 'clinical-coordinator-dashboard dashboard-container';

		// Breadcrumbs
		this.breadcrumbContainer = document.createElement('div');
		container.appendChild(this.breadcrumbContainer);
		this.UD.renderBreadcrumbs(this.breadcrumbContainer, [
			{ label: 'University', route: '/app/university-dashboard' },
			{ label: 'Medical Dean Dashboard', route: '/app/medical-dean-dashboard' },
			{ label: 'Clinical Coordinator' }
		]);

		// KPI row (3 cards)
		this.kpiContainer = document.createElement('div');
		this.kpiContainer.className = 'clinical-coordinator-dashboard__kpis';
		container.appendChild(this.kpiContainer);

		// Dept posting strength table
		this.postingTableSection = document.createElement('div');
		this.postingTableSection.className = 'dashboard-section';
		container.appendChild(this.postingTableSection);

		$(this.page.body).empty().append(container);
	}

	async refresh() {
		if (!this._initialized) return;

		this.UD.showLoading(this.kpiContainer);

		var at = this.filters.academic_term;

		try {
			var results = await Promise.all([
				this.UD.callAPI(this.API_BASE + '.clinical_api.get_clinical_posting_summary', { academic_term: at }),
				this.UD.callAPI(this.API_BASE + '.clinical_api.get_osce_summary', { academic_term: at }),
				this.UD.callAPI(this.API_BASE + '.clinical_api.get_year_down_risk_count', { academic_term: at }),
			]);

			var [postings, osce, yearDown] = results;

			this.renderKPIs(postings, osce, yearDown);
			this.renderPostingTable(postings);
		} catch (err) {
			console.error('[ClinCoord] refresh error:', err);
			this.UD.showError(this.kpiContainer, __('Failed to load clinical data.'));
		}
	}

	renderKPIs(postings, osce, yearDown) {
		var kpis = [
			{
				label: __('Active Clinical Postings'),
				value: postings && postings.success ? (postings.total_active || 0) : '—',
				sublabel: __('Students in rotation today'),
				color: 'blue',
				icon: 'fa fa-hospital-o'
			},
			{
				label: __('OSCE Not Yet Assessed'),
				value: osce && osce.success ? (osce.pending_count || 0) : '—',
				sublabel: __('Awaiting OSCE station scoring'),
				color: osce && osce.pending_count > 0 ? 'orange' : 'green',
				icon: 'fa fa-stethoscope'
			},
			{
				label: __('Year-Down Risk'),
				value: yearDown && yearDown.success ? (yearDown.at_risk_count || 0) : '—',
				sublabel: __('Supplementary in ≥2 subjects (NMC)'),
				color: yearDown && yearDown.at_risk_count > 0 ? 'red' : 'green',
				icon: 'fa fa-exclamation-circle'
			},
		];

		this.UD.renderKPICards(this.kpiContainer, kpis);
	}

	renderPostingTable(data) {
		if (!data || !data.success || !data.by_department || !data.by_department.length) {
			$(this.postingTableSection).html(
				'<div class="dashboard-section-title">' + __('Department Posting Strength') + '</div>' +
				'<p class="text-muted">' + __('No active postings found.') + '</p>'
			);
			return;
		}

		var rows = data.by_department.map(d =>
			'<tr><td>' + frappe.utils.escape_html(d.department) + '</td><td class="text-right">' + d.count + '</td></tr>'
		).join('');

		$(this.postingTableSection).html(
			'<div class="dashboard-section-title">' + __('Department-wise Current Posting Strength') + '</div>' +
			'<table class="table table-bordered table-condensed">' +
			'<thead><tr><th>' + __('Department') + '</th><th class="text-right">' + __('Students Today') + '</th></tr></thead>' +
			'<tbody>' + rows + '</tbody>' +
			'</table>'
		);
	}
}
