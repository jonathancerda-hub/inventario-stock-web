from functools import lru_cache
# odoo_manager.py

import defusedxml.xmlrpc
defusedxml.xmlrpc.monkey_patch()  # B411: protege xmlrpc.client contra XML entity attacks
import xmlrpc.client  # nosec B411 — monkey_patch() aplicado en la línea anterior
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple
from logging_config import get_logger

logger = get_logger('odoo_manager')

class OdooManager:
    # Caché simple para dashboard (máx 32 combinaciones de filtros)
    @lru_cache(maxsize=32)
    def _cached_dashboard_data(self, category_id, line_id, location_id):
        # category_id y line_id deben ser hashables (usar None o int)
        return self._get_dashboard_data_internal(category_id, line_id, location_id)

    def get_dashboard_data(self, category_id: Optional[int] = None, line_id: Optional[int] = None, location_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Obtiene datos agregados para el dashboard con filtros opcionales (cacheado).
        
        Args:
            category_id (int, optional): ID de categoría para filtrar
            line_id (int, optional): ID de línea comercial para filtrar
            location_id (int, optional): ID de ubicación para filtrar
        
        Returns:
            dict: Datos del dashboard con KPIs y gráficos:
                - kpi_total_products: Total de productos únicos
                - kpi_total_quantity: Cantidad total en stock
                - kpi_vence_pronto: Productos por vencer (0-3 meses)
                - chart_labels/chart_data: Top 5 productos con mayor stock
                - exp_chart_labels/exp_chart_data: Productos por vencer
                - category_stock_labels/data: Stock por categoría
                - line_stock_labels/data: Stock por línea comercial
        
        Note:
            Usa caché LRU para guardar hasta 32 combinaciones de filtros.
            Ideal para dashboards que consultan repetidamente los mismos datos.
        """
        # Usar caché para evitar consultas repetidas
        return self._cached_dashboard_data(category_id, line_id, location_id)

    def _get_dashboard_data_internal(self, category_id=None, line_id=None, location_id=None):
        # --- Lógica original de get_dashboard_data aquí ---
        inventory = self.get_stock_inventory(category_id=category_id, line_id=line_id, location_id=location_id)
        if not inventory:
            return {'kpi_total_products': 0, 'kpi_total_quantity': 0, 'chart_labels': [], 'chart_ids': [], 'chart_data': [], 'kpi_vence_pronto': 0, 'exp_chart_labels': [], 'exp_chart_data': [], 'exp_by_line_labels': [], 'exp_by_line_data': [], 'expiring_soon_labels': [], 'expiring_soon_data': [], 'expiring_soon_ids': [], 'category_stock_labels': [], 'category_stock_data': [], 'line_stock_labels': [], 'line_stock_data': []}

        filtered_inventory = inventory

        product_totals = {}
        for item in filtered_inventory:
            product_name, quantity, product_id = item['producto'], float(item['cantidad_disponible'].replace(',', '')), item.get('product_id', 0)
            if product_name in product_totals:
                product_totals[product_name]['quantity'] += quantity
            else:
                product_totals[product_name] = {'quantity': quantity, 'id': product_id}

        total_products = len(product_totals)
        total_quantity = 0
        for item in filtered_inventory:
            if item.get('fecha_expira'):
                try:
                    total_quantity += float(item['cantidad_disponible'].replace(',', ''))
                except Exception:
                    logger.debug("No se pudo convertir cantidad_disponible a float", exc_info=False)
        sorted_products = sorted(product_totals.items(), key=lambda x: x[1]['quantity'], reverse=True)[:5]

        # --- NEW LOGIC for "Top 5 Productos por Vencer (0-3 Meses)" ---
        expiring_soon_products = [
            item for item in filtered_inventory 
            if item.get('meses_expira') is not None and 0 <= item['meses_expira'] <= 3
        ]

        expiring_soon_totals = {}
        for item in expiring_soon_products:
            product_name = item['producto']
            quantity = float(item['cantidad_disponible'].replace(',', ''))
            product_id = item.get('product_id', 0)
            if product_name in expiring_soon_totals:
                expiring_soon_totals[product_name]['quantity'] += quantity
            else:
                expiring_soon_totals[product_name] = {'quantity': quantity, 'id': product_id}
        
        sorted_expiring_soon = sorted(expiring_soon_totals.items(), key=lambda x: x[1]['quantity'], reverse=True)[:5]
        # --- END NEW LOGIC ---

        exp_stats = {"0-3 Meses": 0, "3-6 Meses": 0, "6-9 Meses": 0, "9-12 Meses": 0, ">12 Meses": 0}

        for item in filtered_inventory:
            meses = item.get('meses_expira')
            quantity = float(item['cantidad_disponible'].replace(',', ''))
            if meses is not None:
                if 0 <= meses <= 3:
                    exp_stats["0-3 Meses"] += quantity
                elif 3 < meses <= 6:
                    exp_stats["3-6 Meses"] += quantity
                elif 6 < meses <= 9:
                    exp_stats["6-9 Meses"] += quantity
                elif 9 < meses <= 12:
                    exp_stats["9-12 Meses"] += quantity
                elif meses > 12:
                    exp_stats[">12 Meses"] += quantity

        exp_stats_filtered = {k: v for k, v in exp_stats.items() if v > 0}

        exp_by_line = {}
        for item in inventory:
            meses = item.get('meses_expira')
            quantity = float(item['cantidad_disponible'].replace(',', ''))
            linea = item.get('linea_comercial')
            if meses is not None and 0 <= meses <= 3:
                if linea:
                    exp_by_line[linea] = exp_by_line.get(linea, 0) + quantity

        sorted_exp_by_line = sorted(exp_by_line.items(), key=lambda x: x[1], reverse=True)

        # --- NEW LOGIC for stock by category and line ---
        stock_by_category = {}
        stock_by_line = {}
        for item in filtered_inventory:
            category = item.get('grupo_articulo')
            linea = item.get('linea_comercial')
            quantity = float(item['cantidad_disponible'].replace(',', ''))
            if category:
                stock_by_category[category] = stock_by_category.get(category, 0) + quantity
            if linea:
                stock_by_line[linea] = stock_by_line.get(linea, 0) + quantity
        
        sorted_stock_by_category = sorted(stock_by_category.items(), key=lambda x: x[1], reverse=True)
        sorted_stock_by_line = sorted(stock_by_line.items(), key=lambda x: x[1], reverse=True)
        # --- END NEW LOGIC ---

        return {
            'kpi_total_products': total_products,
            'kpi_total_quantity': int(total_quantity),
            'chart_labels': [p[0] for p in sorted_products],
            'chart_data': [p[1]['quantity'] for p in sorted_products],
            'chart_ids': [p[1]['id'] for p in sorted_products],
            'kpi_vence_pronto': int(exp_stats.get("0-3 Meses", 0)),
            'exp_chart_labels': list(exp_stats_filtered.keys()),
            'exp_chart_data': list(exp_stats_filtered.values()),
            'exp_by_line_labels': [item[0] for item in sorted_exp_by_line],
            'exp_by_line_data': [item[1] for item in sorted_exp_by_line],
            'expiring_soon_labels': [p[0] for p in sorted_expiring_soon],
            'expiring_soon_data': [p[1]['quantity'] for p in sorted_expiring_soon],
            'expiring_soon_ids': [p[1]['id'] for p in sorted_expiring_soon],
            'category_stock_labels': [item[0] for item in sorted_stock_by_category],
            'category_stock_data': [item[1] for item in sorted_stock_by_category],
            'line_stock_labels': [item[0] for item in sorted_stock_by_line],
            'line_stock_data': [item[1] for item in sorted_stock_by_line]
        }

    @staticmethod
    def _get_related_name(data):
        """Extrae el nombre de una tupla de relación de Odoo (id, 'nombre')."""
        return data[1] if isinstance(data, list) and len(data) > 1 else ''

    @staticmethod
    def _transform_location_name(location_name):
        """Transforma nombres largos de ubicaciones a versiones más cortas."""
        transformations = {
            'ALMC/Stock/Corto Vencimiento/VCTO1A3M': '0≥P≤3',
            'ALMC/Stock/Corto Vencimiento/VCTO3A6M': '3>P<6',
            'ALMC/Stock/Corto Vencimiento/VCTO6A9M': '6≥P<9',
            'ALMC/Stock/Corto Vencimiento/VCTO9A12M': '9≥P≤12',
            'ALMC/Stock/Comercial': 'P≥12'
        }
        return transformations.get(location_name, location_name)

    @staticmethod
    def _process_expiration_date(exp_date_str):
        """Procesa una cadena de fecha de expiración y calcula los meses restantes."""
        if not exp_date_str:
            return '', None
        try:
            date_part = exp_date_str.split(' ')[0]
            exp_date_obj = datetime.strptime(date_part, '%Y-%m-%d')
            formatted_exp_date = exp_date_obj.strftime('%d-%m-%Y')
            today = datetime.now()
            return formatted_exp_date, (exp_date_obj.year - today.year) * 12 + (exp_date_obj.month - today.month)
        except (ValueError, TypeError):
            return exp_date_str, None

    def __init__(self) -> None:
        """
        Inicializa el gestor de Odoo con credenciales y establece conexión.
        
        Carga las variables de entorno necesarias para conectarse a Odoo:
        - ODOO_URL: URL del servidor Odoo
        - ODOO_DB: Nombre de la base de datos
        - ODOO_USER: Usuario de Odoo
        - ODOO_PASSWORD: Contraseña de Odoo
        
        También carga la lista blanca de usuarios autorizados desde whitelist.txt
        y establece la conexión inicial con el servidor Odoo vía XML-RPC.
        
        Raises:
            Exception: Si falla la conexión a Odoo después de reintentos
        """
        self.url = os.getenv('ODOO_URL')
        self.db = os.getenv('ODOO_DB')
        self.user = os.getenv('ODOO_USER')
        self.password = os.getenv('ODOO_PASSWORD')
        self.uid = None
        self.models = None
        self.is_connected = False
        self.whitelist = self._load_whitelist()
        self._connect_to_odoo()

    def _connect_to_odoo(self):
        """Establece conexión con Odoo con reintentos y mejor manejo de errores"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries and not self.is_connected:
            try:
                common_url = f'{self.url}/xmlrpc/2/common'
                models_url = f'{self.url}/xmlrpc/2/object'
                common = xmlrpc.client.ServerProxy(common_url)
                
                # Intentar autenticación
                self.uid = common.authenticate(self.db, self.user, self.password, {})
                
                if self.uid:
                    self.models = xmlrpc.client.ServerProxy(models_url)
                    self.is_connected = True
                    logger.info(f"Conexión a Odoo establecida exitosamente (usuario: {self.user})")
                    return
                else:
                    logger.warning("Error de autenticación con Odoo - credenciales incorrectas")
                    break  # No reintentar si las credenciales son incorrectas
                    
            except xmlrpc.client.Fault as e:
                # Error específico de Odoo (típicamente del módulo cs_login_audit_log)
                if 'RuntimeError: object unbound' in str(e) or 'cs_login_audit_log' in str(e):
                    logger.warning(f"Error conocido en módulo Odoo (cs_login_audit_log) - intento {retry_count + 1}/{max_retries}")
                    logger.debug("Este error es del servidor Odoo y no afecta la funcionalidad de la app")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(1)  # Esperar 1 segundo antes de reintentar
                    continue
                else:
                    logger.error(f"Error XML-RPC en Odoo: {str(e)[:200]}")
                    break
                    
            except Exception as e:
                logger.error(f"Error conectando a Odoo: {type(e).__name__}: {str(e)[:200]}")
                break
        
        if not self.is_connected:
            logger.warning("No se pudo establecer conexión con Odoo. La app funcionará en modo limitado.")
            logger.debug("Contacta al administrador de Odoo para revisar el módulo cs_login_audit_log")

    def _load_whitelist(self):
        """Carga la lista blanca de usuarios autorizados desde variable de entorno o whitelist.txt"""
        whitelist = set()
        
        # Prioridad 1: Variable de entorno WHITELIST_EMAILS (para Render y producción)
        env_whitelist = os.getenv('WHITELIST_EMAILS')
        if env_whitelist:
            try:
                for email in env_whitelist.split(','):
                    email = email.strip()
                    if email and not email.startswith('#'):
                        whitelist.add(email.lower())
                logger.info(f"Lista blanca cargada desde variable de entorno: {len(whitelist)} usuarios autorizados")
                return whitelist
            except Exception as e:
                logger.warning(f"Error procesando WHITELIST_EMAILS: {e}")
        
        # Prioridad 2: Archivo whitelist.txt (para desarrollo local)
        whitelist_path = os.path.join(os.path.dirname(__file__), 'whitelist.txt')
        try:
            if os.path.exists(whitelist_path):
                with open(whitelist_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Ignorar líneas vacías y comentarios
                        if line and not line.startswith('#'):
                            whitelist.add(line.lower())
                logger.info(f"Lista blanca cargada desde archivo: {len(whitelist)} usuarios autorizados")
            else:
                logger.warning("Advertencia: No se encontró whitelist.txt ni WHITELIST_EMAILS. Todos los usuarios con credenciales válidas tendrán acceso.")
        except Exception as e:
            logger.warning(f"Error cargando whitelist desde archivo: {e}")
        
        return whitelist

    def is_user_authorized(self, username: str) -> bool:
        """
        Verifica si un usuario está autorizado según la lista blanca.
        
        Args:
            username (str): Email del usuario a verificar
        
        Returns:
            bool: True si el usuario está en whitelist o no hay whitelist configurada,
                  False si hay whitelist y el usuario no está incluido
        
        Note:
            Si whitelist.txt no existe o está vacío, permite acceso a todos los usuarios.
            La comparación es case-insensitive.
        """
        if not self.whitelist:
            # Si no hay whitelist, permitir acceso (modo sin restricción)
            return True
        return username.lower() in self.whitelist

    def authenticate_user(self, username: str, password: str) -> bool:
        """
        Autentica un usuario contra Odoo y verifica autorización.
        
        Args:
            username (str): Email del usuario
            password (str): Contraseña del usuario
        
        Returns:
            bool: True si la autenticación es exitosa y el usuario está autorizado,
                  False en caso contrario
        
        Process:
            1. Verifica conexión a Odoo
            2. Valida que el usuario esté en la whitelist
            3. Autentica contra Odoo usando XML-RPC
            4. Valida que el user_id retornado sea válido
        
        Note:
            Si el usuario no está en la whitelist, rechaza el acceso
            sin intentar autenticar contra Odoo.
        """
        if not self.is_connected: return False
        
        # Verificar primero si el usuario está en la lista blanca
        if not self.is_user_authorized(username):
            logger.warning(f"Acceso denegado: {username} no está en la lista blanca")
            return False
        
        try:
            common_url = f'{self.url}/xmlrpc/2/common'
            common = xmlrpc.client.ServerProxy(common_url)
            user_uid = common.authenticate(self.db, username, password, {})
            if user_uid:
                logger.info(f"Acceso autorizado: {username}")
            return bool(user_uid)
        except Exception as e:
            logger.error(f"Error en autenticación de usuario: {e}")
            return False

    def get_stock_inventory(self, search_term: Optional[str] = None, product_id: Optional[int] = None, category_id: Optional[int] = None, line_id: Optional[int] = None, location_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtiene el inventario de stock desde Odoo con filtros opcionales.
        
        Args:
            search_term (str, optional): Término de búsqueda libre en nombre de producto
            product_id (int, optional): ID específico del producto
            category_id (int, optional): ID del grupo de artículos (categoría)
            line_id (int, optional): ID de la línea comercial nacional
            location_id (int, optional): ID de la ubicación de almacén
        
        Returns:
            list[dict]: Lista de registros de inventario con estructura:
                - product_id: ID del producto
                - producto: Nombre del producto
                - categoria: Categoría del producto
                - linea_comercial: Línea comercial
                - ubicacion: Ubicación en almacén
                - cantidad_disponible: Cantidad disponible formateada
                - fecha_expira: Fecha de expiración (si aplica)
                - meses_expira: Meses hasta expiración
        
        Note:
            Si no se especifica location_id, busca en ubicaciones por defecto:
            - VCTO1A3M, VCTO3A6M, VCTO6A9M, VCTO9A12M, Comercial
            
            Solo retorna productos con cantidad disponible > 0 en ubicaciones internas.
        """
        if not self.is_connected:
            return []
        try:
            domain = [('location_id.usage', '=', 'internal'), ('available_quantity', '>', 0)]
            if location_id:
                domain.append(('location_id', '=', location_id))
            else:
                default_locations = ['ALMC/Stock/Corto Vencimiento/VCTO1A3M', 'ALMC/Stock/Corto Vencimiento/VCTO3A6M', 'ALMC/Stock/Corto Vencimiento/VCTO6A9M', 'ALMC/Stock/Corto Vencimiento/VCTO9A12M', 'ALMC/Stock/Comercial', ]
                # **CORRECCIÓN**: Usamos .display_name para buscar por el nombre completo
                domain.append(('location_id', 'in', default_locations))
            if category_id:
                domain.append(('product_id.categ_id', '=', category_id))
            if line_id:
                domain.append(('product_id.commercial_line_national_id', '=', line_id))
            if product_id:
                domain.append(('product_id', '=', product_id))
            elif search_term:
                search_domain = ['|', ('product_id.default_code', 'ilike', search_term), '|', ('product_id.name', 'ilike', search_term), ('lot_id.name', 'ilike', search_term)]
                domain.extend(search_domain)
            
            # Agregamos los campos requeridos por el usuario: cod_articulo y lugar
            quant_fields = ['product_id', 'available_quantity', 'lot_id', 'location_id']
            stock_quants = self.models.execute_kw(self.db, self.uid, self.password, 'stock.quant', 'search_read', [domain], {'fields': quant_fields})
            
            if not stock_quants: return []

            product_ids = list(set(quant['product_id'][0] for quant in stock_quants))
            lot_ids = list(set(quant['lot_id'][0] for quant in stock_quants if quant.get('lot_id')))
            # Agregamos default_code, name y variantes para construir el nombre personalizado
            # **MEJORA**: Usamos display_name para obtener el nombre completo del producto, simplificando el código.
            product_fields = ['display_name', 'default_code', 'categ_id', 'commercial_line_national_id']
            try:
                product_details = self.models.execute_kw(
                    self.db, self.uid, self.password, 'product.product', 'read', [product_ids],
                    {'fields': product_fields, 'context': {'lang': 'es_PE'}}
                )
                logger.debug(f"Productos obtenidos desde Odoo: {len(product_details)}")
            except Exception as e:
                logger.error(f"Error en consulta de productos a Odoo: {e}")
                product_details = []

            product_map = {prod['id']: prod for prod in product_details}
            lot_map = {}
            if lot_ids:
                lot_details = self.models.execute_kw(self.db, self.uid, self.password, 'stock.lot', 'read', [lot_ids], {'fields': ['expiration_date']})
                lot_map = {lot['id']: lot for lot in lot_details}
            
            inventory_list = []
            for quant in stock_quants:
                prod_id = quant['product_id'][0]
                product_data = product_map.get(prod_id, {})
                lot_data = lot_map.get(quant.get('lot_id', [0])[0]) if quant.get('lot_id') else {}

                # **REFACTOR**: Usamos los nuevos métodos helper para procesar datos.
                exp_date_str = lot_data.get('expiration_date')
                formatted_exp_date, months_to_expire = self._process_expiration_date(exp_date_str)

                inventory_list.append({
                    'product_id': prod_id,
                    'grupo_articulo_id': product_data.get('categ_id', [0, ''])[0],
                    'grupo_articulo': self._get_related_name(product_data.get('categ_id')),
                    'linea_comercial': self._get_related_name(product_data.get('commercial_line_national_id')),
                    'cod_articulo': product_data.get('default_code', ''),
                    'producto': product_data.get('display_name', ''),
                    'lugar': self._transform_location_name(self._get_related_name(quant.get('location_id'))),
                    'fecha_expira': formatted_exp_date,
                    'cantidad_disponible': f"{quant.get('available_quantity', 0):,.2f}",
                    'meses_expira': months_to_expire
                })
            
            inventory_list.sort(key=lambda item: item['meses_expira'] if item['meses_expira'] is not None else float('inf'))
            return inventory_list
        except Exception as e:
            logger.error(f"Error al obtener el inventario de Odoo: {e}")
            return []

    def get_export_inventory(self, search_term: Optional[str] = None, category_id: Optional[int] = None, line_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Obtiene el inventario específico de la ubicación PCP/Exportacion.
        
        Args:
            search_term (str, optional): Término de búsqueda libre en código/nombre de producto
            category_id (int, optional): ID del grupo de artículos (categoría)
            line_id (int, optional): ID de la línea comercial internacional
        
        Returns:
            list[dict]: Lista de registros de inventario de exportación con estructura:
                - producto: Nombre del producto
                - lugar: Ubicación (ALMC/Stock/PCP/Exportacion)
                - fecha_expira: Fecha de expiración
                - cantidad_disponible: Cantidad disponible formateada
                - meses_expira: Meses hasta expiración
        
        Note:
            Solo retorna productos de la ubicación 'ALMC/Stock/PCP/Exportacion'
            con inventory_quantity_auto_apply > 0.
            
            Usa linea comercial INTERNACIONAL (diferente a get_stock_inventory).
        """
        if not self.is_connected:
            return []
        try:
            domain = [
                ('location_id', '=', 'ALMC/Stock/PCP/Exportacion'),
                ('inventory_quantity_auto_apply', '>', 0)
            ]
            if category_id: domain.append(('product_id.categ_id', '=', category_id))
            if line_id: domain.append(('product_id.commercial_line_international_id', '=', line_id))
            if search_term:
                search_domain = ['|', ('product_id.default_code', 'ilike', search_term), '|', ('product_id.name', 'ilike', search_term), ('lot_id.name', 'ilike', search_term)]
                domain.extend(search_domain)
            
            quant_fields = ['product_id', 'location_id', 'inventory_quantity_auto_apply', 'lot_id', 'product_uom_id']
            stock_quants = self.models.execute_kw(self.db, self.uid, self.password, 'stock.quant', 'search_read', [domain], {'fields': quant_fields})
            
            if not stock_quants: return []

            product_ids = list(set(quant['product_id'][0] for quant in stock_quants))
            lot_ids = list(set(quant['lot_id'][0] for quant in stock_quants if quant.get('lot_id')))
            product_fields = ['display_name', 'default_code', 'categ_id', 'commercial_line_international_id']
            # Forzar idioma español (es_PE) en la consulta para evitar '(copiar)'
            product_details = self.models.execute_kw(
                self.db, self.uid, self.password, 'product.product', 'read', [product_ids],
                {'fields': product_fields, 'context': {'lang': 'es_PE'}}
            )
            product_map = {prod['id']: prod for prod in product_details}
            lot_map = {}
            if lot_ids:
                lot_details = self.models.execute_kw(self.db, self.uid, self.password, 'stock.lot', 'read', [lot_ids], {'fields': ['expiration_date']})
                lot_map = {lot['id']: lot for lot in lot_details}
            
            inventory_list = []
            for quant in stock_quants:
                prod_id = quant['product_id'][0]
                product_data = product_map.get(prod_id, {})
                lot_data = lot_map.get(quant.get('lot_id', [0])[0]) if quant.get('lot_id') else {}

                # **REFACTOR**: Usamos los nuevos métodos helper para procesar datos.
                exp_date_str = lot_data.get('expiration_date')
                formatted_exp_date, months_to_expire = self._process_expiration_date(exp_date_str)

                inventory_list.append({
                    'product_id': prod_id, 'grupo_articulo_id': product_data.get('categ_id', [0, ''])[0],
                    'grupo_articulo': self._get_related_name(product_data.get('categ_id')),
                    'linea_comercial': self._get_related_name(product_data.get('commercial_line_international_id')),
                    'cod_articulo': product_data.get('default_code', ''), 'producto': product_data.get('display_name', ''),
                    'um': self._get_related_name(quant.get('product_uom_id')),
                    'lugar': self._transform_location_name(self._get_related_name(quant.get('location_id'))),
                    'lote': self._get_related_name(quant.get('lot_id')),
                    'fecha_expira': formatted_exp_date,
                    'cantidad_disponible': f"{quant.get('inventory_quantity_auto_apply', 0):,.2f}",
                    'meses_expira': months_to_expire
                })
            
            inventory_list.sort(key=lambda item: item['meses_expira'] if item['meses_expira'] is not None else float('inf'))
            return inventory_list
        except Exception as e:
            logger.error(f"Error al obtener el inventario de exportación: {e}")
            return []

    @lru_cache(maxsize=1)
    def _cached_filter_options(self):
        return self._get_filter_options_internal()

    def get_filter_options(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtiene las opciones disponibles para filtros de inventario (cacheado).
        
        Returns:
            dict: Diccionario con opciones de filtrado:
                - productos: Lista de productos [{id, display_name}]
                - grupos: Lista de categorías [{id, display_name}]
                - lineas_nacional: Lista de líneas comerciales nacionales
                - lineas_internacional: Lista de líneas comerciales internacionales
                - lugares: Lista de ubicaciones de almacén
        
        Note:
            Resultados cacheados con @lru_cache para mejorar performance.
            Cache se invalida al reiniciar la aplicación.
        """
        return self._cached_filter_options()

    def _get_filter_options_internal(self):
        if not self.is_connected: return {}
        try:
            default_locations = [
                'ALMC/Stock/Corto Vencimiento/VCTO1A3M', 'ALMC/Stock/Corto Vencimiento/VCTO3A6M',
                'ALMC/Stock/Corto Vencimiento/VCTO6A9M', 'ALMC/Stock/Corto Vencimiento/VCTO9A12M',
                'ALMC/Stock/Comercial'
            ]
            base_domain = [
                ('location_id', 'in', default_locations),
                ('available_quantity', '>', 0)
            ]
            relevant_quants = self.models.execute_kw(
                self.db, self.uid, self.password, 'stock.quant', 'search_read',
                [base_domain], {'fields': ['product_id', 'location_id']}
            )
            if not relevant_quants:
                return {'grupos': [], 'lineas': [], 'lugares': []}
            unique_locations = {quant['location_id'][0]: quant['location_id'][1] for quant in relevant_quants if quant.get('location_id')}
            product_ids = list(set(quant['product_id'][0] for quant in relevant_quants if quant.get('product_id')))
            product_details = self.models.execute_kw(
                self.db, self.uid, self.password, 'product.product', 'read',
                [product_ids], {'fields': ['categ_id', 'commercial_line_national_id']}
            )
            unique_grupos = {prod['categ_id'][0]: prod['categ_id'][1] for prod in product_details if prod.get('categ_id')}
            unique_lineas = {prod['commercial_line_national_id'][0]: prod['commercial_line_national_id'][1] for prod in product_details if prod.get('commercial_line_national_id')}
            lugares = sorted([{'id': id, 'display_name': name} for id, name in unique_locations.items()], key=lambda x: x['display_name'])
            grupos = sorted([{'id': id, 'display_name': name} for id, name in unique_grupos.items()], key=lambda x: x['display_name'])
            lineas = sorted([{'id': id, 'display_name': name} for id, name in unique_lineas.items()], key=lambda x: x['display_name'])
            return {'grupos': grupos, 'lineas': lineas, 'lugares': lugares}
        except Exception as e:
            logger.error(f"Error al obtener opciones de filtro desde Odoo: {e}")
            return {'grupos': [], 'lineas': [], 'lugares': []}

    def get_linea_name(self, line_id):
        """
        Obtiene el nombre de una línea comercial por su ID.
        
        Args:
            line_id (int|str): ID de la línea comercial
        
        Returns:
            str: Nombre de la línea comercial o None si no se encuentra
        
        Note:
            Busca en las opciones de filtro cacheadas, no hace consulta directa a Odoo.
            Útil para mostrar nombres en lugar de IDs en la UI.
        """
        # Busca el nombre de la línea comercial dado su ID (para filtrar en memoria)
        try:
            filter_options = self.get_filter_options()
            for linea in filter_options.get('lineas', []):
                if str(linea['id']) == str(line_id):
                    return linea['display_name']
        except Exception:
            logger.debug("No se pudo obtener el nombre de la línea comercial", exc_info=False)
        return None