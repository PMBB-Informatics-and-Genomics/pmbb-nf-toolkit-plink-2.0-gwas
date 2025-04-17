import os
import pandas as pd
import glob
from pathlib import Path
import argparse

class PlinkReportGenerator:
    def __init__(self, output_dir="plink_reports", phenotypes=None, cohorts=None):
        """Initialize the report generator with output directory, phenotypes, and cohorts."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create directory for plots if it doesn't exist
        (self.output_dir / "Plots").mkdir(exist_ok=True)
        
        self.phenotypes = phenotypes
        self.cohorts = cohorts

    def read_data(self, top_hits_csv):
        """Read the required CSV files and discover plots."""
        try:
            print(f"Reading data from {top_hits_csv}")
            self.hits_data = pd.read_csv(top_hits_csv)
            print("Columns in CSV:", self.hits_data.columns.tolist())
            self.discover_plots()
        except FileNotFoundError:
            print(f"Error: Could not find the file {top_hits_csv}")
            raise
        except KeyError as e:
            print(f"Error: Column {e} not found in the CSV file")
            print("Available columns:", self.hits_data.columns.tolist())
            raise
        except Exception as e:
            print(f"Error reading data: {str(e)}")
            raise

    def discover_plots(self):
        """Discover and catalog available plots."""
        self.available_plots = {}
        plots_dir = Path("Plots")
        
        if not plots_dir.exists():
            print("Warning: Plots directory not found")
            return
        
        plot_files = glob.glob("Plots/*.png")
        print(f"Found {len(plot_files)} plot files")
        
        for plot_file in plot_files:
            filename = os.path.basename(plot_file)
            parts = filename.replace('.png', '').split('.')
            
            if len(parts) >= 3:
                cohort = parts[0]
                pheno = parts[1]
                plot_type = parts[2]
                
                if cohort not in self.available_plots:
                    self.available_plots[cohort] = {}
                if pheno not in self.available_plots[cohort]:
                    self.available_plots[cohort][pheno] = []
                
                self.available_plots[cohort][pheno].append({
                    'type': plot_type,
                    'path': plot_file
                })

    def generate_css(self):
        """Generate enhanced CSS content for styling."""
        css = """
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

        /* Main title styling */
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

        /* Plot controls styling */
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

        /* Responsive sidebar for smaller screens */
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
        css_path = self.output_dir / "styles.css"
        css_path.write_text(css)
        return css_path.relative_to(self.output_dir)

    def create_sidebar(self):
        """Generate HTML for the sidebar navigation."""
        sidebar = '<div class="side-menu">\n'
        sidebar += '  <a href="index.html">Home</a>\n'
        sidebar += '  <a href="phenotype_summary.html">Phenotype Summary</a>\n'
        sidebar += '  <a href="#" onclick="toggleSubmenu(\'results-filter-submenu\')">Results Filter</a>\n'
        
        # Add phenotype groups
        sidebar += '  <div id="results-filter-submenu" class="submenu">\n'
        for pheno in self.phenotypes:
            sidebar += f'    <div class="cohort-group">\n'
            sidebar += f'      <a href="#" onclick="toggleSubCohorts(\'{pheno}\')">{pheno}</a>\n'
            sidebar += f'      <div id="{pheno}-subcohorts" class="subcohorts" style="display: none;">\n'
            for cohort in self.cohorts:
                # Link to "pheno.cohort.html"
                sidebar += f'        <a href="{pheno}.{cohort}.html" class="subcohort-link">{cohort}</a>\n'
            sidebar += '      </div>\n'
            sidebar += '    </div>\n'
        sidebar += '  </div>\n'
        
        sidebar += '  <a href="method_summary.html">Analysis Logs</a>\n'
        sidebar += '</div>\n'
        return sidebar

    def generate_page_template(self, content, title="PLINK 2.0 Results Report"):
        """
        Generate the complete HTML page. 
        NOTE: We do *not* make this an f-string for the embedded JavaScript to avoid conflicts.
        """
        css_path = self.generate_css()
        
        # Instead of an f-string, just use normal triple quotes to avoid curly-brace confusion
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>""" + title + """</title>
    <link rel="stylesheet" href=\"""" + str(css_path) + """\">
</head>
<body>
    <div class="menu-toggle" onclick="toggleMenu()">
        <span></span>
        <span></span>
        <span></span>
    </div>
    """ + self.create_sidebar() + """
    <div class="container">
        <h1 class="text-3xl font-bold mb-4">""" + title + """</h1>
        """ + content + """
    </div>
    <script>
        function toggleMenu() {
            const sideMenu = document.querySelector('.side-menu');
            sideMenu.classList.toggle('active');
        }

        function toggleSubmenu(id) {
            const submenu = document.getElementById(id);
            submenu.style.display = (submenu.style.display === 'none') ? 'block' : 'none';
        }
        
        // This function expands/collapses each phenotype group
        function toggleSubCohorts(pheno) {
            const subCohortsDiv = document.getElementById(`${pheno}-subcohorts`);
            subCohortsDiv.style.display = (subCohortsDiv.style.display === 'none') ? 'block' : 'none';
        }

        // Table pagination functions (no multi-phenotype filter needed here)
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

            // Hide all rows
            allRows.forEach(row => row.style.display = 'none');

            // Show only rows for current page
            allRows.slice(startIdx, endIdx).forEach(row => {
                row.style.display = '';
            });

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
            if (currentPage > 1) {
                currentPage--;
                showCurrentPage();
            }
        }

        function nextPage() {
            const table = document.getElementById('results-table');
            if (!table) return;
            const tbody = table.querySelector('tbody');
            const totalRows = tbody.getElementsByTagName('tr').length;
            const totalPages = Math.ceil(totalRows / rowsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                showCurrentPage();
            }
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

        // Initialize pagination on page load
        document.addEventListener('DOMContentLoaded', () => {
            showCurrentPage();
        });
    </script>
</body>
</html>
"""
        return html

    def generate_cohort_pheno_page(self, cohort, pheno):
        """Generate a results page for a specific cohort and phenotype."""
        print(f"Generating page for cohort: {cohort}, phenotype: {pheno}")
        
        cohort_pheno_data = self.hits_data[
            (self.hits_data['COHORT'] == cohort) &
            (self.hits_data['PHENO'] == pheno)
        ]
        
        if cohort_pheno_data.empty:
            print(f"Warning: No data found for cohort {cohort}, phenotype {pheno}")
            return
        
        headers = cohort_pheno_data.columns.tolist()

        # Build plot section
        plot_content = ""
        if cohort in self.available_plots and pheno in self.available_plots[cohort]:
            plots = self.available_plots[cohort][pheno]
            plot_content = '<div class="plot-container">\n'
            plot_content += f'<h3>Plots for {pheno} in {cohort}</h3>\n'
            plot_content += '<div class="plot-controls">\n'
            plot_content += f'<button class="plot-toggle active" onclick="togglePlotType(\'{pheno}\', \'manhattan\')">Manhattan Plot</button>\n'
            plot_content += f'<button class="plot-toggle" onclick="togglePlotType(\'{pheno}\', \'qq\')">QQ Plot</button>\n'
            plot_content += '</div>\n'
            plot_content += '<div class="plot-grid">\n'
            
            plot_dict = {'manhattan': None, 'qq': None}
            for plt in plots:
                pt = plt['type'].lower()
                if 'manhattan' in pt:
                    plot_dict['manhattan'] = plt
                elif 'qq' in pt:
                    plot_dict['qq'] = plt

            for pt_type, plt_obj in plot_dict.items():
                if plt_obj:
                    display = 'block' if pt_type == 'manhattan' else 'none'
                    plot_content += f'''
                    <div class="plot-wrapper plot-{pt_type}" data-plot-type="{pt_type}" style="display: {display}">
                        <img src="{plt_obj['path']}" 
                             alt="{cohort} {pheno} {pt_type} Plot" 
                             class="plot-image"
                             onclick="toggleImageSize(this)">
                    </div>
                    '''
            
            plot_content += '</div>\n</div>\n'

        # Build table content
        table_html = """
        <div class="table-container">
            <table id="results-table">
                <thead>
                    <tr>
        """
        for header in headers:
            table_html += f"<th>{header}</th>"
        table_html += "</tr></thead><tbody>\n"

        for _, row in cohort_pheno_data.iterrows():
            table_html += "<tr>"
            for col in headers:
                table_html += f"<td>{row[col]}</td>"
            table_html += "</tr>\n"

        table_html += "</tbody></table></div>\n"

        pagination_controls = """
        <div class="pagination-controls">
            <button id="prev-page" class="pagination-button" onclick="previousPage()">Previous</button>
            <span id="page-info">Page 1</span>
            <button id="next-page" class="pagination-button" onclick="nextPage()">Next</button>
        </div>
        """

        content = f"""
        <h2>Results for Phenotype: {pheno} in Cohort: {cohort}</h2>
        {plot_content}
        <h3>Top Hits</h3>
        {table_html}
        {pagination_controls}
        """

        page = self.generate_page_template(content, f"PLINK Results - {pheno} in {cohort}")
        
        output_file = self.output_dir / f"{pheno}.{cohort}.html"
        output_file.write_text(page)
        print(f"Generated page: {output_file}")

    def generate_index_page(self):
        """Generate the main index page."""
        content = """
        <div id="default-view" class="my-4">
            <p style="text-align: left;">
                This report presents the comprehensive findings from an Exome-Wide Association Study (PLINK 2.0) analysis 
                conducted using the state-of-the-art PLINK 2.0 Nextflow pipeline. The analysis performed both single-variant 
                and gene-based association tests to identify statistically significant genetic associations with the 
                specified phenotypes.
            </p>
            
            <h2 style="text-align: left;">Getting Started</h2>
            <ul style="text-align: left;">
                <li>Select a population group from the Results Filter in the side menu (AFR_ALL, EUR_ALL, etc.).</li>
                <li>Explore the Phenotype Summary to view distributions of traits across populations.</li>
                <li>Dive into specific results using the Manhattan and QQ plots.</li>
                <li>Refer to the Analysis Logs for detailed explanations of data and visualizations.</li>
            </ul>
            
            <h2 style="text-align: left;">Key Terms</h2>
            <ul style="text-align: left;">
                <li><b>AFR</b>: African ancestry</li>
                <li><b>EUR</b>: European ancestry</li>
                <li><b>AMR</b>: Admixed American ancestry</li>
                <li><b>EAS</b>: East Asian ancestry</li>
                <li><b>MAF</b>: Minor Allele Frequency</li>
                <li><b>pLoF</b>: predicted Loss of Function variants</li>
            </ul>
        </div>
        """
        page = self.generate_page_template(content, "PLINK 2.0 Results Report")
        index_file = self.output_dir / "index.html"
        index_file.write_text(page)
        print(f"Generated page: {index_file}")

    def generate_method_summary(self):
        """Generate the method summary page."""
        content = """
        <div id="method-summary">
            <h2>PLINK 2.0 Methods Summary</h2>
            <h3>Software Versions</h3>
            <p>SAIGE Version: wzhou88/saige:1.2.0</p>
            <p>Python .exe: /opt/conda/bin/python</p>
            <p>Plink: plink/2.0-20210505</p>

            <h3>Workflow Set-Up</h3>
            <p>Cohorts: AMR_ALL,AMR_F,AMR_M,AFR_ALL,AFR_F,AFR_M,EAS_ALL,EAS_F,EAS_M,EUR_ALL,EUR_F,EUR_M</p>
            <p>Binary Phenotypes: T2D, AAA</p>
            <p>Quantitative Phenotypes: BMI_median, LDL_median</p>
            
            <!-- Add more method details as needed -->
        </div>
        """
        page = self.generate_page_template(content, "Analysis Logs")
        method_file = self.output_dir / "method_summary.html"
        method_file.write_text(page)
        print(f"Generated page: {method_file}")

    def generate_all_reports(self):
        """Generate all HTML reports."""
        print("Generating reports...")
        
        # Generate index page
        print("Generating index page...")
        self.generate_index_page()
        
        # Generate pages for each (phenotype, cohort)
        print("Generating (Phenotype, Cohort) pages...")
        for pheno in self.phenotypes:
            for cohort in self.cohorts:
                print(f"Generating page for {pheno} in {cohort}...")
                self.generate_cohort_pheno_page(cohort, pheno)
        
        # Generate method summary
        print("Generating method summary...")
        self.generate_method_summary()
        
        # Copy plots to output directory
        self.copy_plots()
        
        print("Report generation complete!")

    def copy_plots(self):
        """Copy plots to the output directory."""
        plots_dir = self.output_dir / "Plots"
        plots_dir.mkdir(exist_ok=True)
        
        for source_plot in glob.glob("Plots/*.png"):
            plot_name = os.path.basename(source_plot)
            target_plot = plots_dir / plot_name
            
            try:
                with open(source_plot, 'rb') as src, open(target_plot, 'wb') as dst:
                    dst.write(src.read())
            except Exception as e:
                print(f"Error copying plot {source_plot}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Generate PLINK reports.")
    parser.add_argument("--phenotypes", nargs="+", required=True, help="List of phenotypes")
    parser.add_argument("--cohorts", nargs="+", required=True, help="List of cohorts")
    parser.add_argument("--top_hits_csv", required=True, help="Path to the top hits CSV file")
    parser.add_argument("--output_dir", default="plink_reports", help="Output directory for reports")
    
    args = parser.parse_args()
    
    generator = PlinkReportGenerator(
        output_dir=args.output_dir,
        phenotypes=args.phenotypes,
        cohorts=args.cohorts
    )
    generator.read_data(args.top_hits_csv)
    generator.generate_all_reports()

if __name__ == "__main__":
    main()
