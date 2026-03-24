import json
import zipfile
import argparse
import shutil
import pandas as pd
from pathlib import Path


CSS = """
/* Base styles and typography */
body {
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    background-color: #f5f7fa;
    color: #2d3748;
    line-height: 1.6;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
    margin-left: 260px;
}

h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #1a202c;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 3px solid #3182ce;
}

h2 {
    font-size: 2rem;
    font-weight: 600;
    color: #2d3748;
    margin: 2rem 0;
    text-align: center;
}

h3 {
    font-size: 1.5rem;
    color: #2d3748;
    margin: 1.5rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
}

/* Plot container styling */
.plot-container {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    margin: 2rem 0;
}

.plot-controls {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin: 1.5rem 0;
}

.plot-toggle {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    background-color: #e2e8f0;
    color: #2d3748;
}

.plot-toggle:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.plot-toggle.active {
    background-color: #3182ce;
    color: white;
}

.phenotype-section {
    margin-bottom: 3rem;
    text-align: center;
}

.plot-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 1.5rem 0;
}

.plot-image {
    max-width: 800px;
    width: 100%;
    height: auto;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    cursor: pointer;
}

.plot-image.enlarged {
    max-width: 1200px;
}

/* Results table styling */
.table-container {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    margin: 2rem 0;
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 1rem 0;
}

th {
    background-color: #2d3748;
    color: white;
    font-weight: 600;
    padding: 1rem;
    text-align: left;
    position: sticky;
    top: 0;
}

td {
    padding: 1rem;
    border-bottom: 1px solid #e2e8f0;
    font-size: 0.95rem;
}

tr:hover {
    background-color: #f7fafc;
}

/* Pagination controls */
.pagination-controls {
    margin-top: 1rem;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
}

.pagination-button {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 8px;
    background-color: #3182ce;
    color: white;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.pagination-button:hover:not(:disabled) {
    background-color: #2c5282;
    transform: translateY(-1px);
}

.pagination-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

#page-info {
    font-weight: 500;
    color: #2d3748;
}

/* Sidebar styling */
.side-menu {
    position: fixed;
    left: 0;
    top: 0;
    width: 250px;
    height: 100vh;
    background-color: #2d3748;
    padding: 2rem 0;
    color: white;
    overflow-y: auto;
    box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
    z-index: 1000;
}

.side-menu a {
    display: block;
    padding: 1rem 1.5rem;
    color: #e2e8f0;
    text-decoration: none;
    transition: all 0.2s ease;
    font-weight: 500;
}

.side-menu a:hover {
    background-color: #4a5568;
    padding-left: 2rem;
}

.side-menu .submenu {
    background-color: #1a202c;
    overflow: hidden;
}

.cohort-group {
    border-bottom: 1px solid #4a5568;
}

.cohort-group > a {
    background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http://www.w3.org/2000/svg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23ffffff%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.4-12.8z%22/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 1rem center;
    background-size: 0.8em auto;
}

.subcohorts {
    background-color: #1a202c;
    transition: all 0.3s ease;
}

.subcohort-link {
    padding-left: 2.5rem !important;
    font-size: 0.95rem;
    color: #cbd5e0 !important;
}

.subcohort-link:hover {
    background-color: #4a5568;
    padding-left: 3rem !important;
}

/* Menu toggle for mobile */
.menu-toggle {
    display: none;
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 1001;
    padding: 0.5rem;
    background-color: #2d3748;
    border-radius: 4px;
    cursor: pointer;
}

.menu-toggle span {
    display: block;
    width: 25px;
    height: 3px;
    background-color: white;
    margin: 5px 0;
    transition: all 0.3s ease;
}

@media (max-width: 1024px) {
    .side-menu {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }

    .side-menu.active {
        transform: translateX(0);
    }

    .menu-toggle {
        display: block;
    }

    .container {
        margin-left: 0;
        padding: 1rem;
    }

    .plot-image {
        max-width: 100%;
    }

    .plot-image.enlarged {
        max-width: 100%;
    }
}
"""

JS = """
function toggleMenu() {
    const sideMenu = document.querySelector('.side-menu');
    sideMenu.classList.toggle('active');
}

function toggleSubmenu(id) {
    const submenu = document.getElementById(id);
    submenu.style.display = (submenu.style.display === 'none') ? 'block' : 'none';
}

function toggleSubCohorts(pheno) {
    const subCohortsDiv = document.getElementById(`${pheno}-subcohorts`);
    subCohortsDiv.style.display = (subCohortsDiv.style.display === 'none') ? 'block' : 'none';
}

let currentPage = 1;
let rowsPerPage = 10;

function updateRowsPerPage(value) {
    rowsPerPage = parseInt(value);
    currentPage = 1;
    showCurrentPage();
}

function showCurrentPage() {
    const startIdx = (currentPage - 1) * rowsPerPage;
    const endIdx = startIdx + rowsPerPage;
    const table = document.getElementById('results-table');
    if (!table) return;
    const tbody = table.querySelector('tbody');
    const allRows = Array.from(tbody.getElementsByTagName('tr'));
    allRows.forEach(row => row.style.display = 'none');
    allRows.slice(startIdx, endIdx).forEach(row => { row.style.display = ''; });
    updatePaginationInfo(allRows.length);
}

function updatePaginationInfo(total) {
    const totalPages = Math.ceil(total / rowsPerPage);
    const pageInfo = document.getElementById('page-info');
    const prevButton = document.getElementById('prev-page');
    const nextButton = document.getElementById('next-page');
    if (pageInfo) pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    if (prevButton) prevButton.disabled = (currentPage <= 1);
    if (nextButton) nextButton.disabled = (currentPage >= totalPages);
}

function previousPage() {
    if (currentPage > 1) { currentPage--; showCurrentPage(); }
}

function nextPage() {
    const table = document.getElementById('results-table');
    if (!table) return;
    const tbody = table.querySelector('tbody');
    const totalRows = tbody.getElementsByTagName('tr').length;
    const totalPages = Math.ceil(totalRows / rowsPerPage);
    if (currentPage < totalPages) { currentPage++; showCurrentPage(); }
}

function togglePlotType(phenotype, plotType) {
    const section = document.querySelector(`[data-phenotype="${phenotype}"]`);
    if (!section) return;
    const buttons = section.querySelectorAll('.plot-toggle');
    const plots = section.querySelectorAll('.plot-wrapper');
    buttons.forEach(btn => {
        btn.classList.toggle('active', btn.textContent.toLowerCase().includes(plotType));
    });
    plots.forEach(plot => {
        plot.style.display = (plot.dataset.plotType === plotType) ? 'block' : 'none';
    });
}

function toggleImageSize(img) {
    img.classList.toggle('enlarged');
}

document.addEventListener('DOMContentLoaded', () => {
    showCurrentPage();
});
"""


class PlinkReportGenerator:
    def __init__(self, manifest_path, output_zip):
        with open(manifest_path) as f:
            self.manifest = json.load(f)

        self.output_zip = Path(output_zip)
        self.report_name = self.output_zip.stem
        self.output_dir = Path(self.report_name)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / 'Plots').mkdir(exist_ok=True)

        self.cohort_list = self.manifest['cohort_list']
        self.bin_pheno_list = self.manifest.get('bin_pheno_list', [])
        self.quant_pheno_list = self.manifest.get('quant_pheno_list', [])
        self.all_phenos = self.bin_pheno_list + self.quant_pheno_list

        self.top_hits_df = pd.read_csv(self.manifest['top_hits_csv'])
        self.pheno_summaries_df = pd.read_csv(self.manifest['pheno_summaries_csv'])

    def _plot_rel_path(self, src_path):
        """Return the HTML-relative path for a plot file (Plots/<filename>)."""
        return f"Plots/{Path(src_path).name}"

    def _write_css(self):
        (self.output_dir / 'styles.css').write_text(CSS)

    def _create_sidebar(self):
        sidebar = '<div class="side-menu">\n'
        sidebar += '  <a href="index.html">Home</a>\n'
        sidebar += '  <a href="phenotype_summary.html">Phenotype Summary</a>\n'
        sidebar += "  <a href=\"#\" onclick=\"toggleSubmenu('results-filter-submenu')\">Results Filter</a>\n"
        sidebar += '  <div id="results-filter-submenu" class="submenu">\n'
        for pheno in self.all_phenos:
            sidebar += '    <div class="cohort-group">\n'
            sidebar += f"      <a href=\"#\" onclick=\"toggleSubCohorts('{pheno}')\">{pheno}</a>\n"
            sidebar += f'      <div id="{pheno}-subcohorts" class="subcohorts" style="display: none;">\n'
            for cohort in self.cohort_list:
                sidebar += f'        <a href="{pheno}.{cohort}.html" class="subcohort-link">{cohort}</a>\n'
            sidebar += '      </div>\n'
            sidebar += '    </div>\n'
        sidebar += '  </div>\n'
        sidebar += '  <a href="method_summary.html">Analysis Logs</a>\n'
        sidebar += '</div>\n'
        return sidebar

    def _page_template(self, content, title="PLINK 2.0 Results Report"):
        return (
            '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
            '    <meta charset="UTF-8">\n'
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'    <title>{title}</title>\n'
            '    <link rel="stylesheet" href="styles.css">\n'
            '</head>\n<body>\n'
            '    <div class="menu-toggle" onclick="toggleMenu()">'
            '<span></span><span></span><span></span></div>\n'
            + self._create_sidebar()
            + '    <div class="container">\n'
            f'        <h1>{title}</h1>\n'
            + content
            + '    </div>\n'
            '<script>\n' + JS + '\n</script>\n'
            '</body>\n</html>\n'
        )

    def _df_to_html_table(self, df, table_id='results-table'):
        """Render a DataFrame as an HTML table string."""
        headers = df.columns.tolist()
        header_html = ''.join(f'<th>{h}</th>' for h in headers)
        rows_html = ''.join(
            '<tr>' + ''.join(f'<td>{row[c]}</td>' for c in headers) + '</tr>\n'
            for _, row in df.iterrows()
        )
        return (
            f'<div class="table-container"><table id="{table_id}">'
            f'<thead><tr>{header_html}</tr></thead>'
            f'<tbody>{rows_html}</tbody>'
            '</table></div>\n'
        )

    def _pagination_controls(self):
        return (
            '<div class="pagination-controls">'
            '<button id="prev-page" class="pagination-button" onclick="previousPage()">Previous</button>'
            '<span id="page-info">Page 1</span>'
            '<button id="next-page" class="pagination-button" onclick="nextPage()">Next</button>'
            '</div>\n'
        )

    def generate_index_page(self):
        content = """
        <div id="default-view">
            <p style="text-align: left;">
                This report presents the comprehensive findings from a PLINK 2.0 Genome-Wide Association Study (GWAS)
                analysis. The pipeline performed single-variant association tests to identify statistically significant
                genetic associations with the specified phenotypes.
            </p>
            <h2 style="text-align: left;">Getting Started</h2>
            <ul style="text-align: left;">
                <li>Select a population group from the <b>Results Filter</b> in the side menu.</li>
                <li>Explore the <b>Phenotype Summary</b> to view trait distributions and sample counts across cohorts.</li>
                <li>Dive into specific results using the Manhattan and QQ plots.</li>
                <li>Refer to <b>Analysis Logs</b> for the full set of pipeline parameters used.</li>
            </ul>
            <h2 style="text-align: left;">Key Terms</h2>
            <ul style="text-align: left;">
                <li><b>MAF</b>: Minor Allele Frequency</li>
                <li><b>HWE</b>: Hardy-Weinberg Equilibrium</li>
                <li><b>GWAS</b>: Genome-Wide Association Study</li>
                <li><b>QQ Plot</b>: Quantile-Quantile plot for assessing genomic inflation</li>
            </ul>
        </div>
        """
        (self.output_dir / 'index.html').write_text(
            self._page_template(content, 'PLINK 2.0 Results Report')
        )
        print("  index.html")

    def generate_phenotype_summary(self):
        # Phenotype summary statistics table
        table_html = self._df_to_html_table(self.pheno_summaries_df, table_id='pheno-summary-table')

        # Per-phenotype plots (barplots, violinplots)
        plot_sections = ''
        for pheno, plots in self.manifest.get('pheno_summary_plots', {}).items():
            imgs = ''.join(
                f'<div class="plot-wrapper">'
                f'<img src="{self._plot_rel_path(p)}" alt="{pheno} summary plot" '
                f'class="plot-image" onclick="toggleImageSize(this)"></div>\n'
                for p in plots
            )
            plot_sections += (
                f'<div class="plot-container"><h3>{pheno}</h3>'
                f'<div class="plot-grid">{imgs}</div></div>\n'
            )

        content = (
            '<h2>Phenotype Summary Statistics</h2>\n'
            + table_html
            + '<h2>Phenotype Distribution Plots</h2>\n'
            + (plot_sections if plot_sections else '<p>No phenotype summary plots found.</p>')
        )
        (self.output_dir / 'phenotype_summary.html').write_text(
            self._page_template(content, 'Phenotype Summary')
        )
        print("  phenotype_summary.html")

    def generate_cohort_pheno_page(self, cohort, pheno):
        gwas_plots = self.manifest['gwas_plots'].get(cohort, {}).get(pheno, {})

        # Plot section
        plot_content = ''
        if gwas_plots:
            plot_content = f'<div class="plot-container" data-phenotype="{pheno}">\n'
            plot_content += f'<h3>Plots for {pheno} in {cohort}</h3>\n'
            plot_content += (
                '<div class="plot-controls">'
                f'<button class="plot-toggle active" onclick="togglePlotType(\'{pheno}\', \'manhattan\')">Manhattan Plot</button>'
                f'<button class="plot-toggle" onclick="togglePlotType(\'{pheno}\', \'qq\')">QQ Plot</button>'
                '</div>\n'
            )
            for pt_type, display in [('manhattan', 'block'), ('qq', 'none')]:
                src = gwas_plots.get(pt_type)
                if src:
                    plot_content += (
                        f'<div class="plot-wrapper" data-plot-type="{pt_type}" style="display: {display}">'
                        f'<img src="{self._plot_rel_path(src)}" alt="{cohort} {pheno} {pt_type}" '
                        f'class="plot-image" onclick="toggleImageSize(this)"></div>\n'
                    )
            plot_content += '</div>\n'

        # Top hits table
        if 'COHORT' in self.top_hits_df.columns and 'PHENO' in self.top_hits_df.columns:
            df = self.top_hits_df[
                (self.top_hits_df['COHORT'] == cohort) &
                (self.top_hits_df['PHENO'] == pheno)
            ]
        else:
            df = pd.DataFrame()

        if df.empty:
            table_html = '<div class="table-container"><p>No significant hits found above the p-value threshold.</p></div>\n'
            pagination = ''
        else:
            table_html = self._df_to_html_table(df)
            pagination = self._pagination_controls()

        content = (
            f'<h2>Results for Phenotype: {pheno} in Cohort: {cohort}</h2>\n'
            + plot_content
            + '<h3>Top Hits</h3>\n'
            + table_html
            + pagination
        )
        (self.output_dir / f'{pheno}.{cohort}.html').write_text(
            self._page_template(content, f'PLINK Results - {pheno} in {cohort}')
        )
        print(f"  {pheno}.{cohort}.html")

    def generate_method_summary(self):
        params = self.manifest.get('params', {})

        def fmt(v):
            if isinstance(v, list):
                return ', '.join(str(x) for x in v) or '—'
            if isinstance(v, dict):
                return '<br>'.join(f'{k} → {val}' for k, val in v.items())
            return str(v) if v is not None else '—'

        def fmt_key(k):
            return k.replace('_', ' ').title()

        body = ''
        for section_key, section_data in params.items():
            if not isinstance(section_data, dict):
                continue
            rows = ''.join(
                f'<tr><td><b>{fmt_key(k)}</b></td><td>{fmt(v)}</td></tr>\n'
                for k, v in section_data.items()
            )
            body += (
                f'<h3>{fmt_key(section_key)}</h3>'
                '<div class="table-container"><table>'
                '<thead><tr><th>Parameter</th><th>Value</th></tr></thead>'
                f'<tbody>{rows}</tbody>'
                '</table></div>\n'
            )

        content = (
            '<div id="method-summary">'
            '<h2>PLINK 2.0 Methods Summary</h2>'
            + body
            + '</div>\n'
        )
        (self.output_dir / 'method_summary.html').write_text(
            self._page_template(content, 'Analysis Logs')
        )
        print("  method_summary.html")

    def _copy_assets(self):
        # Collect all plot source paths from manifest
        all_plot_sources = set()
        for plots in self.manifest.get('pheno_summary_plots', {}).values():
            all_plot_sources.update(plots)
        for cohort_plots in self.manifest.get('gwas_plots', {}).values():
            for pheno_plots in cohort_plots.values():
                all_plot_sources.update(pheno_plots.values())

        for src in all_plot_sources:
            src_path = Path(src)
            if src_path.exists():
                shutil.copy(src_path, self.output_dir / 'Plots' / src_path.name)
            else:
                print(f"  Warning: plot not found: {src}")

        shutil.copy(self.manifest['top_hits_csv'],
                    self.output_dir / 'plink2_all_suggestive.csv')
        shutil.copy(self.manifest['pheno_summaries_csv'],
                    self.output_dir / 'pheno_summaries.csv')

    def _create_zip(self):
        with zipfile.ZipFile(self.output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in self.output_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.output_dir.parent)
                    zf.write(file_path, arcname)
        print(f"Report written to {self.output_zip}")

    def generate_all(self):
        print("Generating PLINK 2.0 report...")
        self._write_css()
        self.generate_index_page()
        self.generate_phenotype_summary()
        for pheno in self.all_phenos:
            for cohort in self.cohort_list:
                self.generate_cohort_pheno_page(cohort, pheno)
        self.generate_method_summary()
        self._copy_assets()
        self._create_zip()
        print("Done.")


def main():
    parser = argparse.ArgumentParser(
        description="Generate a portable PLINK 2.0 GWAS HTML report zip from a manifest file."
    )
    parser.add_argument('--manifest', required=True,
                        help='Path to results_manifest.json')
    parser.add_argument('--output_zip', default='Plink_2.0_GWAS_Report.zip',
                        help='Output zip file path (default: Plink_2.0_GWAS_Report.zip)')
    args = parser.parse_args()

    generator = PlinkReportGenerator(args.manifest, args.output_zip)
    generator.generate_all()


if __name__ == '__main__':
    main()
