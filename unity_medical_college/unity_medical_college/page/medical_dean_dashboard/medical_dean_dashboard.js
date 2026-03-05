// Medical Dean Dashboard — NMC compliance & clinical overview
// Gated: only renders when Medical College Settings.enable_medical_module = 1

frappe.pages['medical-dean-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Medical Dean Dashboard',
		single_column: true
	});
	new MedicalDeanDashboard(page);
};

class MedicalDeanDashboard {
	constructor(page) {
		this.page = page;
		this.UD = window.UniversityDashboard;
		this.API_BASE = 'unity_medical_college.unity_medical_college.dashboard_api';
		this.UA_API_BASE = 'university_app.university_app.dashboard_api';
		this.faculty = null;
		this.filters = {};
		this.charts = {};
		this._initialized = false;
		this.init();
	}

	async init() {
		// Gate: check if medical module is enabled
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
		await this.detectScope();
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

	// =========================================================================
	// Scope Detection
	// =========================================================================

	async detectScope() {
		var params = this.UD.getUrlParams();
		if (params.faculty) {
			this.faculty = params.faculty;
		} else {
			var scope = await this.UD.callAPI(this.UA_API_BASE + '.base.get_user_scope').catch(() => ({}));
			if (scope && scope.faculty) {
				this.faculty = scope.faculty;
			}
		}
	}

	// =========================================================================
	// Filters
	// =========================================================================

	setupFilters() {
		var self = this;

		this.page.add_field({
			fieldname: 'academic_year',
			label: __('Academic Year'),
			fieldtype: 'Link',
			options: 'Academic Year',
			change: function () {
				self.filters.academic_year = self.page.fields_dict.academic_year.get_value();
				self.refresh();
			}
		});

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
			if (defaults && defaults.academic_year) {
				this.filters.academic_year = defaults.academic_year;
				this.page.fields_dict.academic_year.set_value(defaults.academic_year);
			}
			if (defaults && defaults.academic_term) {
				this.filters.academic_term = defaults.academic_term;
				this.page.fields_dict.academic_term.set_value(defaults.academic_term);
			}
		} catch (e) {
			console.error('[MedDean] setDefaultFilters error:', e);
		}
	}

	// =========================================================================
	// Layout
	// =========================================================================

	buildLayout() {
		var container = document.createElement('div');
		container.className = 'medical-dean-dashboard dashboard-container';

		// Breadcrumbs
		this.breadcrumbContainer = document.createElement('div');
		container.appendChild(this.breadcrumbContainer);
		this.UD.renderBreadcrumbs(this.breadcrumbContainer, [
			{ label: 'University', route: '/app/university-dashboard' },
			{ label: 'Dean Dashboard', route: '/app/dean-dashboard' },
			{ label: 'Medical Dean Dashboard' }
		]);

		// KPI row (6 cards)
		this.kpiContainer = document.createElement('div');
		this.kpiContainer.className = 'medical-dean-dashboard__kpis';
		container.appendChild(this.kpiContainer);

		// Charts grid
		var chartsGrid = document.createElement('div');
		chartsGrid.className = 'medical-dean-dashboard__charts chart-row';

		this.chartPhase = document.createElement('div');
		this.chartPhase.className = 'chart-container';
		chartsGrid.appendChild(this.chartPhase);

		this.chartAttendance = document.createElement('div');
		this.chartAttendance.className = 'chart-container';
		chartsGrid.appendChild(this.chartAttendance);

		this.chartExamComponents = document.createElement('div');
		this.chartExamComponents.className = 'chart-container';
		chartsGrid.appendChild(this.chartExamComponents);

		this.chartCaseLogs = document.createElement('div');
		this.chartCaseLogs.className = 'chart-container';
		chartsGrid.appendChild(this.chartCaseLogs);

		container.appendChild(chartsGrid);

		$(this.page.body).empty().append(container);
	}

	// =========================================================================
	// Data Refresh
	// =========================================================================

	async refresh() {
		if (!this._initialized) return;

		this.UD.showLoading(this.kpiContainer);

		var faculty = this.faculty;
		var at = this.filters.academic_term;

		try {
			var results = await Promise.all([
				this.UD.callAPI(this.API_BASE + '.clinical_api.get_nmc_attendance_compliance', { faculty: faculty, academic_term: at }),
				this.UD.callAPI(this.API_BASE + '.clinical_api.get_exam_component_pass_rates', { faculty: faculty, academic_term: at }),
				this.UD.callAPI(this.API_BASE + '.clinical_api.get_batch_phase_distribution', { faculty: faculty }),
				this.UD.callAPI(this.API_BASE + '.clinical_api.get_osce_summary', { faculty: faculty, academic_term: at }),
				this.UD.callAPI(this.API_BASE + '.clinical_api.get_case_log_compliance', { faculty: faculty, academic_term: at }),
				this.UD.callAPI(this.API_BASE + '.clinical_api.get_faculty_nmc_compliance_summary', { faculty: faculty }),
				this.UD.callAPI(this.API_BASE + '.clinical_api.get_curriculum_coverage_summary', { academic_term: at }),
			]);

			var [attendance, examRates, phases, osce, caseLogs, facultyCompliance, curriculum] = results;

			this.renderKPIs(attendance, examRates, caseLogs, facultyCompliance, curriculum);
			this.renderPhaseChart(phases);
			this.renderAttendanceChart(attendance);
			this.renderExamChart(examRates);
			this.renderCaseLogChart(caseLogs);
		} catch (err) {
			console.error('[MedDean] refresh error:', err);
			this.UD.showError(this.kpiContainer, __('Failed to load medical data.'));
		}
	}

	// =========================================================================
	// KPI Cards
	// =========================================================================

	renderKPIs(attendance, examRates, caseLogs, facultyCompliance, curriculum) {
		var totalStudents = attendance && attendance.total || 0;
		var eligibleCount = attendance && attendance.eligible_count || 0;
		var eligibilityPct = totalStudents > 0 ? Math.round(eligibleCount / totalStudents * 100) : 0;

		var kpis = [
			// Row 1 — Clinical / NMC
			{
				label: __('Student Eligibility Rate'),
				value: attendance && attendance.success ? eligibilityPct + '%' : '—',
				sublabel: __('Theory ≥75% | Clinical ≥80% (NMC MSR 2023)'),
				color: eligibilityPct >= 90 ? 'green' : eligibilityPct >= 75 ? 'orange' : 'red',
				icon: '<i class="fa fa-id-card"></i>',
				onClick: function() { frappe.set_route('List', 'MBBS Clinical Posting', {status: 'Active'}); }
			},
			{
				label: __('Attendance Defaulters'),
				value: attendance && attendance.success ? (attendance.ineligible_count || 0) : '—',
				sublabel: __('Students below NMC threshold'),
				color: (attendance && attendance.ineligible_count > 0) ? 'red' : 'green',
				icon: '<i class="fa fa-exclamation-triangle"></i>',
				onClick: function() { frappe.set_route('List', 'MBBS Clinical Posting'); }
			},
			{
				label: __('Faculty NMC Compliance'),
				value: facultyCompliance && facultyCompliance.success ? facultyCompliance.compliance_pct + '%' : '—',
				sublabel: __('Depts meeting MSR 2023 faculty norms'),
				color: facultyCompliance && facultyCompliance.compliance_pct === 100 ? 'green'
					: facultyCompliance && facultyCompliance.compliance_pct >= 80 ? 'orange' : 'red',
				icon: '<i class="fa fa-users"></i>',
				onClick: function() { frappe.set_route('List', 'NMC Faculty Compliance'); }
			},
			// Row 2 — Academics / CBME
			{
				label: __('Theory Exam Pass %'),
				value: examRates && examRates.success ? examRates.theory_pass_pct + '%' : '—',
				sublabel: __('NMC pass mark: 50%'),
				color: examRates && examRates.theory_pass_pct >= 75 ? 'green' : 'orange',
				icon: '<i class="fa fa-book"></i>',
				onClick: function() { frappe.set_route('List', 'MBBS Exam Component'); }
			},
			{
				label: __('Practical Pass %'),
				value: examRates && examRates.success ? examRates.practical_pass_pct + '%' : '—',
				sublabel: __('NMC pass mark: 50%'),
				color: examRates && examRates.practical_pass_pct >= 75 ? 'green' : 'orange',
				icon: '<i class="fa fa-flask"></i>',
				onClick: function() { frappe.set_route('List', 'MBBS Exam Component'); }
			},
			{
				label: __('Curriculum Coverage'),
				value: curriculum && curriculum.success ? curriculum.coverage_pct + '%' : '—',
				sublabel: __('Sessions delivered vs planned (CBME)'),
				color: curriculum && curriculum.coverage_pct >= 80 ? 'green'
					: curriculum && curriculum.coverage_pct >= 60 ? 'orange' : 'red',
				icon: '<i class="fa fa-book-open"></i>',
				onClick: function() { frappe.set_route('List', 'Curriculum Map'); }
			},
		];

		this.UD.renderKPICards(this.kpiContainer, kpis);
	}

	// =========================================================================
	// Charts
	// =========================================================================

	renderPhaseChart(data) {
		if (!data || !data.success || !data.phases || !data.phases.length) return;
		this.UD.renderBarChart(this.chartPhase, {
			title: __('Batch Phase Distribution'),
			labels: data.phases.map(p => p.phase),
			datasets: [{ name: __('Students'), values: data.phases.map(p => p.count) }],
			colors: ['#4197ff']
		});
	}

	renderAttendanceChart(data) {
		if (!data || !data.success || !data.department_breakdown || !data.department_breakdown.length) return;
		var depts = data.department_breakdown;
		this.UD.renderBarChart(this.chartAttendance, {
			title: __('Attendance Defaulters by Department'),
			labels: depts.map(d => d.department),
			datasets: [
				{ name: __('Below Theory'), values: depts.map(d => d.below_theory) },
				{ name: __('Below Clinical'), values: depts.map(d => d.below_clinical) }
			],
			colors: ['#ff5858', '#ff8c00']
		});
	}

	renderExamChart(data) {
		if (!data || !data.success || !data.total) return;
		this.UD.renderBarChart(this.chartExamComponents, {
			title: __('Exam Component Pass Rates'),
			labels: [__('Theory'), __('Practical'), __('Viva'), __('Overall')],
			datasets: [{
				name: __('Pass %'),
				values: [data.theory_pass_pct, data.practical_pass_pct, data.viva_pass_pct, data.overall_pass_pct]
			}],
			colors: ['#36b37e']
		});
	}

	renderCaseLogChart(data) {
		if (!data || !data.success) return;
		this.UD.renderDonutChart(this.chartCaseLogs, {
			title: __('CBME Case Log Completion'),
			labels: [__('Submitted'), __('Pending')],
			datasets: [{ values: [data.submitted || 0, Math.max(0, (data.expected || 0) - (data.submitted || 0))] }],
			colors: ['#36b37e', '#ff5858']
		});
	}
}
