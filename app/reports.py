import io
import pandas as pd
from flask import Blueprint, request, jsonify, render_template, send_file, session
from sqlalchemy import text
from app.models import db, ReportConfig
from app.db_inspector import get_database_tables, get_table_columns
from app.auth import log_audit

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/view', methods=['GET'])
def reports_page():
    if not session.get('user_id'):
        return render_template('login.html')
    return render_template('reports.html')

@reports_bp.route('/api/metadata/tables', methods=['GET'])
def list_tables():
    tables = get_database_tables()
    return jsonify({'success': True, 'tables': tables})

@reports_bp.route('/api/metadata/tables/<table_name>/columns', methods=['GET'])
def list_columns(table_name):
    columns = get_table_columns(table_name)
    return jsonify({'success': True, 'columns': columns})

@reports_bp.route('/api/reports/generate', methods=['POST'])
def generate_report():
    data = request.get_json(silent=True) or request.form
    table_name = data.get('table_name')
    fields = data.get('fields', [])
    where_clause = data.get('where_clause', '').strip()
    order_by = data.get('order_by', '').strip()

    if not table_name or not fields:
        return jsonify({'success': False, 'message': 'Table name and at least one field are required.'}), 400

    if isinstance(fields, str):
        fields = [f.strip() for f in fields.split(',') if f.strip()]

    # Sanitize field and table names to prevent SQL injection
    field_str = ", ".join([f"`{f}`" if db.engine.name == 'mysql' else f'"{f}"' for f in fields])
    sql = f"SELECT {field_str} FROM \"{table_name}\""
    if db.engine.name in ['sqlite', 'mysql']:
        sql = f"SELECT {field_str} FROM `{table_name}`"

    if where_clause:
        sql += f" WHERE {where_clause}"
    if order_by:
        sql += f" ORDER BY {order_by}"

    try:
        with db.engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = [dict(row._mapping) for row in result]

        log_audit('REPORT_GENERATED', f"Generated report for table {table_name}")
        return jsonify({'success': True, 'data': rows, 'columns': fields, 'sql': sql})
    except Exception as e:
        return jsonify({'success': False, 'message': f"Query Execution Error: {str(e)}"}), 500

@reports_bp.route('/api/reports/export', methods=['POST'])
def export_report():
    data = request.get_json(silent=True) or {}
    table_name = data.get('table_name')
    fields = data.get('fields', [])
    where_clause = data.get('where_clause', '').strip()
    order_by = data.get('order_by', '').strip()
    export_format = data.get('format', 'excel').lower()

    if not table_name or not fields:
        return jsonify({'success': False, 'message': 'Table and fields required.'}), 400

    field_str = ", ".join([f"`{f}`" if db.engine.name == 'mysql' else f'"{f}"' for f in fields])
    sql = f"SELECT {field_str} FROM \"{table_name}\""
    if db.engine.name in ['sqlite', 'mysql']:
        sql = f"SELECT {field_str} FROM `{table_name}`"

    if where_clause:
        sql += f" WHERE {where_clause}"
    if order_by:
        sql += f" ORDER BY {order_by}"

    try:
        df = pd.read_sql_query(text(sql), db.engine)
        output = io.BytesIO()

        if export_format == 'csv':
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(output, mimetype='text/csv', as_attachment=True, download_name=f"{table_name}_report.csv")
        else:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='ReportData')
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"{table_name}_report.xlsx"
            )
    except Exception as e:
        return jsonify({'success': False, 'message': f"Export Error: {str(e)}"}), 500

@reports_bp.route('/api/reports/config', methods=['GET', 'POST'])
def handle_report_configs():
    if request.method == 'GET':
        configs = ReportConfig.query.all()
        return jsonify({'success': True, 'reports': [c.to_dict() for c in configs]})

    data = request.get_json(silent=True) or {}
    name = data.get('name')
    table_name = data.get('table_name')
    fields = data.get('fields', [])

    if not name or not table_name or not fields:
        return jsonify({'success': False, 'message': 'Name, table, and fields required.'}), 400

    if isinstance(fields, list):
        fields = ",".join(fields)

    config = ReportConfig(
        name=name,
        description=data.get('description', ''),
        table_name=table_name,
        selected_fields=fields,
        where_clause=data.get('where_clause', ''),
        order_by=data.get('order_by', ''),
        created_by=session.get('username', 'system')
    )
    db.session.add(config)
    db.session.commit()

    log_audit('REPORT_CONFIG_SAVED', f"Saved report configuration {name}")
    return jsonify({'success': True, 'message': 'Report configuration saved successfully.', 'report': config.to_dict()})
