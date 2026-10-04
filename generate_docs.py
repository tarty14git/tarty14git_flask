import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from pptx import Presentation
from pptx.util import Inches as PptxInches, Pt as PptxPt

DOCS_DIR = 'docs'
os.makedirs(DOCS_DIR, exist_ok=True)

def generate_word_doc():
    doc = Document()

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("Functional Specification & System Walkthrough Document\n")
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(0, 51, 102)

    run_sub = p_title.add_run("com.cth Enterprise Flask Dynamic Reporting Web Application\n\n")
    run_sub.font.size = Pt(14)
    run_sub.font.italic = True

    # Section 1: Executive Summary
    h1 = doc.add_heading("1. Executive Summary", level=1)
    doc.add_paragraph(
        "The com.cth Enterprise Reporting System is a highly configurable, multi-database Python Flask web application "
        "designed for enterprise-grade dynamic query generation, realtime dashboard analytics, user maintenance, "
        "and configurable authentication (LDAP/Active Directory or Local Database with 2FA OTP support)."
    )

    # Section 2: Architecture & Database Support
    doc.add_heading("2. Architecture & Database Engine Support", level=1)
    doc.add_paragraph(
        "The system is built on a clean MVC architecture using Flask, SQLAlchemy ORM, and Flasgger for Swagger UI API documentation. "
        "It dynamically inspects and supports multiple RDBMS engines configured seamlessly via app.properties or the web front-end:"
    )
    bullet1 = doc.add_paragraph(style='List Bullet')
    bullet1.add_run("Oracle Database (Default Enterprise engine)")
    bullet2 = doc.add_paragraph(style='List Bullet')
    bullet2.add_run("PostgreSQL Database")
    bullet3 = doc.add_paragraph(style='List Bullet')
    bullet3.add_run("Microsoft SQL Server")
    bullet4 = doc.add_paragraph(style='List Bullet')
    bullet4.add_run("SQLite (Embedded / Demo engine)")

    # Section 3: Authentication & Security
    doc.add_heading("3. Authentication & User Maintenance", level=1)
    doc.add_paragraph(
        "The system provides robust security features configurable in real-time from the frontend:"
    )
    doc.add_paragraph("- Dual Mode Authentication: LDAP / Windows Active Directory integration alongside local bcrypt/pbkdf2 password hashing.")
    doc.add_paragraph("- Account Maintenance: Lock/unlock user accounts, automatic locking after 5 failed attempts, password reset, and 90-day password expiration enforcement.")
    doc.add_paragraph("- Two-Factor Authentication (2FA): SMS/Email OTP authentication disabled for demo purposes by default, togglable with a single switch in the admin panel.")

    # Section 4: Dynamic Report Builder
    doc.add_heading("4. Online Dynamic Report Generator", level=1)
    doc.add_paragraph(
        "The main page allows users to inspect available database tables and fields dynamically. Users can build queries, apply filter clauses (WHERE), "
        "order data (ORDER BY), view online interactive results, and export formatted reports directly to Excel (.xlsx) or CSV."
    )

    # Section 5: Realtime Dashboard & Deployment
    doc.add_heading("5. Realtime Dashboard & Cross-Platform Deployment", level=1)
    doc.add_paragraph(
        "Includes a live Chart.js dashboard providing realtime polling of response times, active workflow jobs, user statuses, and audit trail logs. "
        "Packaged for execution across both Windows (start.bat, stop.bat, build.bat) and Linux (start.sh, stop.sh), as well as Docker and Kubernetes (k8s/)."
    )

    # Section 6: Java com.cth JUnit Integration
    doc.add_heading("6. Java JUnit Test Cases Summary", level=1)
    doc.add_paragraph(
        "All Java source files and test suites are packaged under com.cth (e.g., src/main/java/com/cth/tests/ApplicationTestSuite.java) "
        "providing JUnit 5 enterprise validation tests."
    )

    filepath = os.path.join(DOCS_DIR, "CTH_Functional_Specification_and_Instructions.docx")
    doc.save(filepath)
    print(f"Saved {filepath}")

def generate_excel_doc():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "System Test Matrix & Specs"

    # Header Styling
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="003366", end_color="003366", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")
    border = Border(
        left=Side(style='thin', color='DDDDDD'),
        right=Side(style='thin', color='DDDDDD'),
        top=Side(style='thin', color='DDDDDD'),
        bottom=Side(style='thin', color='DDDDDD')
    )

    headers = ["Module / Feature", "Requirement Description", "Supported Tech Stack", "Test Status", "JUnit Test Case"]
    ws.append(headers)

    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align

    rows = [
        ["Database Config", "Support Oracle, Postgres, SQL Server, SQLite", "Flask-SQLAlchemy, cx_Oracle, psycopg2", "PASSED", "testDatabaseEngineConfiguration"],
        ["LDAP Auth", "Toggleable LDAP / Active Directory vs Local Auth", "ldap3, Flask Session", "PASSED", "testLdapAuthenticationSwitch"],
        ["User Maintenance", "Lock/unlock, 5-attempt lock, password reset", "Flask, Werkzeug Security", "PASSED", "testUserLockUnlock"],
        ["2FA OTP", "SMS / Email 2FA toggle switch (disabled for demo)", "Python OTP Generator", "PASSED", "testTwoFactorToggle"],
        ["Dynamic Reports", "Inspect tables/fields, generate & export online", "pandas, openpyxl, SQLAlchemy Inspect", "PASSED", "testDynamicReportQueryBuilder"],
        ["Realtime Dashboard", "Chart.js, response time metrics, workflow logs", "Bootstrap 5, Chart.js", "PASSED", "testDashboardStats"],
        ["Cross-Platform", "Windows (.bat) & Linux (.sh) start/stop/build scripts", "Waitress, Gunicorn, Bash, Batch", "PASSED", "testDeploymentScripts"]
    ]

    for row in rows:
        ws.append(row)

    for r in range(2, len(rows) + 2):
        for c in range(1, len(headers) + 1):
            ws.cell(row=r, column=c).border = border

    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 40
    ws.column_dimensions['C'].width = 35
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 35

    filepath = os.path.join(DOCS_DIR, "CTH_System_Test_Matrix_and_Requirements.xlsx")
    wb.save(filepath)
    print(f"Saved {filepath}")

def generate_powerpoint_doc():
    prs = Presentation()

    # Slide 1: Title
    blank_slide_layout = prs.slide_layouts[0]
    slide1 = prs.slides.add_slide(blank_slide_layout)
    title = slide1.shapes.title
    subtitle = slide1.placeholders[1]

    title.text = "com.cth Enterprise Reporting System"
    subtitle.text = "Configurable Flask Application with Oracle/Postgres/SQL Server Support\nWalkthrough & Architecture Overview"

    # Slide 2: Key Features
    layout2 = prs.slide_layouts[1]
    slide2 = prs.slides.add_slide(layout2)
    slide2.shapes.title.text = "Key System Features & Capabilities"
    tf2 = slide2.placeholders[1].text_frame
    tf2.text = "Multi-Database Engine Support: Oracle, PostgreSQL, SQL Server, SQLite"
    p = tf2.add_paragraph()
    p.text = "Configurable Authentication: Toggle LDAP/Active Directory or Local Auth"
    p = tf2.add_paragraph()
    p.text = "User Maintenance: Account Lock/Unlock, Password Expiration & Reset"
    p = tf2.add_paragraph()
    p.text = "2FA Mechanism: Email/SMS OTP togglable for demo/production"
    p = tf2.add_paragraph()
    p.text = "Dynamic Report Builder: Inspect DB metadata, query fields, export Excel/CSV"

    # Slide 3: Deployment & Realtime Analytics
    slide3 = prs.slides.add_slide(layout2)
    slide3.shapes.title.text = "Realtime Dashboard & Cross-Platform Deployment"
    tf3 = slide3.placeholders[1].text_frame
    tf3.text = "Realtime Dashboard: Live Chart.js response time polling and active workflow logs"
    p = tf3.add_paragraph()
    p.text = "Windows Execution: build.bat, start.bat, stop.bat using Waitress"
    p = tf3.add_paragraph()
    p.text = "Linux Execution: start.sh, stop.sh using Gunicorn"
    p = tf3.add_paragraph()
    p.text = "Containerization & K8s: Dockerfile, docker-compose.yml, and Kubernetes manifests"
    p = tf3.add_paragraph()
    p.text = "Swagger UI & Java com.cth JUnit test suite integration"

    filepath = os.path.join(DOCS_DIR, "CTH_Application_Walkthrough_Presentation.pptx")
    prs.save(filepath)
    print(f"Saved {filepath}")

if __name__ == '__main__':
    generate_word_doc()
    generate_excel_doc()
    generate_powerpoint_doc()
