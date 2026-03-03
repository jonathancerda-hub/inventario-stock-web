# app.py

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from dotenv import load_dotenv
from odoo_manager import OdooManager
from analytics_db import AnalyticsDB
from authlib.integrations.flask_client import OAuth
import os
import pandas as pd
import io
from datetime import datetime

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
data_manager = OdooManager()
analytics_db = AnalyticsDB()

# Configuración de OAuth2 de Google con Authlib
oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

# Middleware para registrar visitas
@app.before_request
def log_page_visit():
    if 'username' in session and request.endpoint not in ['static', None]:
        # Excluir usuario administrador de analytics (temporalmente desactivado para pruebas)
        excluded_users = []  # jonathan.cerda@agrovetmarket.com - desactivado para pruebas
        if session.get('username').lower() in [email.lower() for email in excluded_users]:
            return  # No registrar visitas del administrador
        
        # Excluir endpoints que no son páginas reales
        excluded_endpoints = ['static', 'export_excel', 'export_excel_exportacion']
        if request.endpoint not in excluded_endpoints:
            analytics_db.log_visit(
                user_email=session.get('username'),
                user_name=session.get('username').split('@')[0],  # Nombre simple del email
                page_url=request.path,
                page_title=request.endpoint,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                referrer=request.referrer,
                method=request.method
            )

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/google-oauth')
def google_oauth():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            flash('No se pudo obtener información del usuario.', 'danger')
            return redirect(url_for('login'))
        
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')
        
        # Verificar si el usuario está autorizado
        if not data_manager.is_user_authorized(email):
            flash('Acceso denegado. Solo usuarios autorizados de @agrovetmarket.com pueden acceder.', 'danger')
            return redirect(url_for('login'))
        
        # Guardar la información del usuario en la sesión
        session['username'] = email
        session['user_name'] = name
        session['user_picture'] = picture
        session['user_info'] = user_info
        
        flash('¡Inicio de sesión exitoso!', 'success')
        return redirect(url_for('inventory'))
        
    except Exception as e:
        print(f"Error en autenticación OAuth2: {e}")
        flash(f'Error durante la autenticación: {str(e)}', 'danger')
        return redirect(url_for('login'))
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado la sesión.', 'info')
    return redirect(url_for('login'))

@app.route('/export/excel/exportacion')
def export_excel_exportacion():
    if 'username' not in session: return redirect(url_for('login'))
    
    selected_filters = {
        'search_term': request.args.get('search_term'),
        'grupo_id': request.args.get('grupo_id', type=int),
        'linea_id': request.args.get('linea_id', type=int),
    }
    inventory_data = data_manager.get_export_inventory(**selected_filters)

    if not inventory_data:
        flash('No hay datos para exportar.', 'warning')
        return redirect(url_for('inventory_export'))
        
    df = pd.DataFrame([{k: v for k, v in item.items() if k not in ['product_id', 'grupo_articulo_id', 'linea_comercial_id']} for item in inventory_data])

    # Formatear columnas numéricas y de fecha
    if 'cantidad_disponible' in df.columns:
        df['cantidad_disponible'] = pd.to_numeric(df['cantidad_disponible'].str.replace(',', ''), errors='coerce')
    if 'fecha_expira' in df.columns:
        df['fecha_expira'] = pd.to_datetime(df['fecha_expira'], format='%d-%m-%Y', errors='coerce')

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventario Exportacion')
        ws = writer.sheets['Inventario Exportacion']
        # Ajustar ancho de columnas automáticamente
        for column_cells in ws.columns:
            length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = length + 2
        # Formato para cantidades y fechas
        from openpyxl.styles import numbers
        if 'cantidad_disponible' in df.columns:
            col_idx = df.columns.get_loc('cantidad_disponible') + 1
            for cell in ws.iter_cols(min_col=col_idx, max_col=col_idx, min_row=2):
                for c in cell:
                    c.number_format = '#,##0'
        if 'fecha_expira' in df.columns:
            col_idx = df.columns.get_loc('fecha_expira') + 1
            for cell in ws.iter_cols(min_col=col_idx, max_col=col_idx, min_row=2):
                for c in cell:
                    c.number_format = 'DD-MM-YYYY'
    output.seek(0)

    filename = f"inventario_exportacion_{datetime.now().strftime('%d-%m-%Y_%H-%M')}.xlsx"
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=filename)

@app.route('/export/excel')
def export_excel():
    if 'username' not in session: return redirect(url_for('login'))
    
    selected_filters = {
        'search_term': request.args.get('search_term'),
        'product_id': request.args.get('product_id', type=int),
        'grupo_id': request.args.get('grupo_id', type=int),
        'linea_id': request.args.get('linea_id', type=int),
        'lugar_id': request.args.get('lugar_id', type=int)
    }
    
    inventory_data = data_manager.get_stock_inventory(**selected_filters)
    
    exp_status = request.args.get('exp_status')
    if exp_status and inventory_data:
        if exp_status == 'vence_pronto':
            inventory_data = [item for item in inventory_data if item['meses_expira'] is not None and 0 <= item['meses_expira'] <= 3]
        elif exp_status == 'advertencia':
            inventory_data = [item for item in inventory_data if item['meses_expira'] is not None and 4 <= item['meses_expira'] <= 7]
        elif exp_status == 'ok':
            inventory_data = [item for item in inventory_data if item['meses_expira'] is not None and 8 <= item['meses_expira'] <= 12]
        elif exp_status == 'largo_plazo':
            inventory_data = [item for item in inventory_data if item['meses_expira'] is not None and item['meses_expira'] > 12]

    if not inventory_data:
        flash('No hay datos para exportar.', 'warning')
        return redirect(url_for('inventory'))
    
    export_df_data = [{k: v for k, v in item.items() if k not in ['product_id', 'grupo_articulo_id', 'linea_comercial_id']} for item in inventory_data]
    df = pd.DataFrame(export_df_data)

    # Formatear columnas numéricas y de fecha
    if 'cantidad_disponible' in df.columns:
        df['cantidad_disponible'] = pd.to_numeric(df['cantidad_disponible'].astype(str).str.replace(',', ''), errors='coerce')
    if 'fecha_expira' in df.columns:
        df['fecha_expira'] = pd.to_datetime(df['fecha_expira'], format='%d-%m-%Y', errors='coerce')

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventario')
        ws = writer.sheets['Inventario']
        # Ajustar ancho de columnas automáticamente
        for column_cells in ws.columns:
            length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = length + 2
        # Formato para cantidades y fechas
        from openpyxl.styles import numbers
        if 'cantidad_disponible' in df.columns:
            col_idx = df.columns.get_loc('cantidad_disponible') + 1
            for cell in ws.iter_cols(min_col=col_idx, max_col=col_idx, min_row=2):
                for c in cell:
                    c.number_format = '#,##0'
        if 'fecha_expira' in df.columns:
            col_idx = df.columns.get_loc('fecha_expira') + 1
            for cell in ws.iter_cols(min_col=col_idx, max_col=col_idx, min_row=2):
                for c in cell:
                    c.number_format = 'DD-MM-YYYY'
    output.seek(0)
    
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M")
    filename = f"inventario_stock_{timestamp}.xlsx"
    
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=filename)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session: return redirect(url_for('login'))

    if request.method == 'POST':
        return redirect(url_for('dashboard', 
            category_id=request.form.get('category_id'),
            linea_id=request.form.get('linea_id'),
            lugar_id=request.form.get('lugar_id')
        ))

    selected_category_id = request.args.get('category_id', type=int)
    selected_linea_id = request.args.get('linea_id', type=int)
    selected_lugar_id = request.args.get('lugar_id', type=int)

    import time
    start_time = time.time()
    dashboard_data = data_manager.get_dashboard_data(
        category_id=selected_category_id,
        linea_id=selected_linea_id,
        lugar_id=selected_lugar_id
    )
    elapsed = time.time() - start_time
    
    # **OPTIMIZACIÓN**: Usamos la función get_filter_options para ser más eficientes
    filter_options = data_manager.get_filter_options()
    available_categories = filter_options.get('grupos', [])
    available_lineas = filter_options.get('lineas', [])
    available_lugares = filter_options.get('lugares', [])

    if not dashboard_data:
        flash('No hay datos de inventario para mostrar en el dashboard.', 'warning')
        return redirect(url_for('inventory'))
    
    return render_template('dashboard.html', 
        data=dashboard_data, 
        categories=available_categories, 
        lineas=available_lineas,
        lugares=available_lugares,
        selected_category_id=selected_category_id,
        selected_linea_id=selected_linea_id,
        selected_lugar_id=selected_lugar_id,
        backend_time=f"{elapsed:.3f} s"
    )

@app.route('/exportacion', methods=['GET', 'POST'])
def inventory_export():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    filter_options = data_manager.get_filter_options()
    
    selected_filters = {
        'search_term': request.values.get('search_term'),
        'grupo_id': request.values.get('grupo_id', type=int),
        'linea_id': request.values.get('linea_id', type=int)
    }

    stock_data = data_manager.get_export_inventory(**selected_filters)
    
    return render_template(
        'export_inventory.html',
        inventory=stock_data, 
        filter_options=filter_options,
        selected_filters=selected_filters
    )

@app.route('/')
def index():
    # Mostrar el dashboard como página principal si hay sesión, sino ir a login
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/analytics')
def analytics():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Verificar permisos de administrador
    admin_emails = [
        'jonathan.cerda@agrovetmarket.com',
        'ena.fernandez@agrovetmarket.com'
    ]
    
    if session.get('username').lower() not in [email.lower() for email in admin_emails]:
        flash('No tienes permisos para acceder a esta sección.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Obtener período solicitado
    days = request.args.get('period', 30, type=int)
    
    # Recopilar todas las estadísticas
    total_visits = analytics_db.get_total_visits(days)
    unique_users = analytics_db.get_unique_users(days)
    
    # Obtener total de usuarios autorizados desde el whitelist
    total_allowed_users = len(data_manager.whitelist) if data_manager.whitelist else 0
    
    stats = {
        'total_visits': total_visits,
        'unique_users': unique_users,
        'total_allowed_users': total_allowed_users,
        'visits_by_user': analytics_db.get_visits_by_user(days),
        'visits_by_page': analytics_db.get_visits_by_page(days),
        'visits_by_day': analytics_db.get_visits_by_day(days),
        'visits_by_hour': analytics_db.get_visits_by_hour(min(days, 7)),
        'recent_visits': analytics_db.get_recent_visits(50)
    }
    
    return render_template('analytics.html', stats=stats, period=days)

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Verificar si el usuario tiene permiso de descarga
    download_whitelist = os.getenv('DOWNLOAD_WHITELIST', '').split(',') if os.getenv('DOWNLOAD_WHITELIST') else []
    can_download = session.get('username', '').lower() in [email.strip().lower() for email in download_whitelist]
    
    filter_options = data_manager.get_filter_options()
    
    if request.method == 'POST':
        selected_filters = {
            'search_term': request.form.get('search_term'),
            'product_id': request.form.get('product_id', type=int),
            'grupo_id': request.form.get('grupo_id', type=int),
            'linea_id': request.form.get('linea_id', type=int),
            'lugar_id': request.form.get('lugar_id', type=int)
        }
    else: # GET request
        selected_filters = {
            'search_term': request.args.get('search_term'),
            'product_id': request.args.get('product_id', type=int),
            'grupo_id': request.args.get('grupo_id', type=int),
            'linea_id': request.args.get('linea_id', type=int),
            'lugar_id': request.args.get('lugar_id', type=int)
        }

    stock_data = data_manager.get_stock_inventory(**selected_filters)

    exp_status = request.args.get('exp_status')
    if exp_status and stock_data:
        if exp_status == '0-3':
            stock_data = [item for item in stock_data if item['meses_expira'] is not None and 0 <= item['meses_expira'] <= 3]
        elif exp_status == '3-6':
            stock_data = [item for item in stock_data if item['meses_expira'] is not None and 3 < item['meses_expira'] <= 6]
        elif exp_status == '6-9':
            stock_data = [item for item in stock_data if item['meses_expira'] is not None and 6 < item['meses_expira'] <= 9]
        elif exp_status == '9-12':
            stock_data = [item for item in stock_data if item['meses_expira'] is not None and 9 < item['meses_expira'] <= 12]
        elif exp_status == '>12':
            stock_data = [item for item in stock_data if item['meses_expira'] is not None and item['meses_expira'] > 12]
    
    selected_filters['exp_status'] = exp_status
    
    return render_template(
        'inventory.html', 
        inventory=stock_data, 
        filter_options=filter_options,
        selected_filters=selected_filters,
        can_download=can_download
    )

if __name__ == '__main__':
    app.run(debug=True)