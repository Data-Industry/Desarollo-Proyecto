"""Motor Conversacional (Chatbot) en Lenguaje Natural para Jubilados y Cuidadores (US-38 / SCRUM-53).

Brinda asistencia conversacional empática y accesible a adultos mayores y familiares
cuidadores en Santa Cruz de la Sierra. Interpreta consultas ciudadanas sobre insulinas,
marcas comerciales, formatos, principios activos, anillos urbanos y dosis, ofreciendo
comparativas de precios entre farmacias (Farmacorp, Farmacias Chávez, Farmacias Telchi),
ahorro estimado en Bolivianos y semáforo preventivo de abastecimiento sin tecnicismos
complejos ni jerga de Machine Learning.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parents[2]
DATA_PROCESSED_DIR = PROJECT_DIR / "data" / "processed"


def normalizar_texto(texto: str) -> str:
    """Convierte texto a minúsculas y elimina diacríticos/tildes para matching tolerante."""
    if not texto:
        return ""
    texto = texto.lower().strip()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    return texto


class AsistenteInsulina:
    """Motor del Asistente Conversacional para Jubilados y Cuidadores en Santa Cruz."""

    # Mapeo exhaustivo de marcas y sinónimos comerciales presentes en Santa Cruz
    MARCAS_CONOCIDAS: Dict[str, List[str]] = {
        "Lantus": ["lantus", "glargina sanofi", "lantus solostar"],
        "Basalog": ["basalog", "basalog one", "glargina biocon"],
        "Toujeo": ["toujeo", "glargina 300", "toujeo solostar"],
        "Apidra": ["apidra", "glulisina", "apidra solostar"],
        "Novolin N": ["novolin n", "novolin nph", "nph novo", "novolin verde"],
        "Novolin R": ["novolin r", "novolin regular", "novolin cristalina", "cristalina", "regular"],
        "Novolin 70/30": ["novolin 70/30", "novolin 70 30", "novolin mezcla", "novolin bifasica"],
        "Humodar NPH": ["humodar nph", "humodar n", "humodar verde"],
        "Humodar R": ["humodar r", "humodar regular", "humodar cristalina"],
        "Humodar C25": ["humodar c25", "humodar 25", "humodar mezcla"],
        "Densulin N": ["densulin n", "densulin nph"],
        "Densulin R": ["densulin r", "densulin regular"],
        "Densulent": ["densulent"],
        "Glaripen": ["glaripen"],
        "Glaritus": ["glaritus"],
        "Glinux N": ["glinux n", "glinux"],
        "Insugen": ["insugen", "insugen n", "insugen r"],
        "Asparpen": ["asparpen", "asparta"],
    }

    # Principios activos y tipos de acción
    PRINCIPIOS_ACTIVOS: Dict[str, List[str]] = {
        "Insulina Glargina": ["glargina", "glargine", "lenta", "prolongada", "basal"],
        "Insulina Humana NPH (N)": ["nph", "intermedia", "humana n", "isofana"],
        "Insulina Humana Regular (R)": ["regular", "cristalina", "rapida", "humana r", "corriente"],
        "Insulina Humana Mixta / Bifásica": ["mixta", "bifasica", "70/30", "70 30", "c25"],
        "Insulina Glulisina": ["glulisina"],
        "Insulina Asparta": ["asparta", "aspart"],
    }

    # Formatos de presentación
    FORMATOS_PRESENTACION: Dict[str, List[str]] = {
        "Vial / Frasco Ampolla": ["frasco", "vial", "ampolla", "frasco ampolla", "botellita"],
        "Cartucho para Pluma Reutilizable": ["cartucho", "repuesto", "penfill", "refill", "lapicero recargable"],
        "Lapicero Prellenado (Pluma)": ["lapicera", "pluma", "lapicero", "prellenado", "descartable", "solostar"],
    }

    # Cadenas de farmacias en Santa Cruz
    CADENAS_FARMACIA: Dict[str, List[str]] = {
        "Farmacorp": ["farmacorp", "corporacion"],
        "Farmacias Chávez": ["chavez", "farmacias chavez", "farmacia chavez"],
        "Farmacias Telchi": ["telchi", "farmacias telchi", "farmacia telchi"],
    }

    def __init__(
        self,
        df_master: Optional[pd.DataFrame] = None,
        df_geo: Optional[pd.DataFrame] = None,
        df_preds: Optional[pd.DataFrame] = None,
    ) -> None:
        """Inicializa el asistente con los datasets maestros del proyecto."""
        if df_master is not None:
            self.df_master = df_master.copy()
        else:
            master_file = DATA_PROCESSED_DIR / "insulinas_master.csv"
            self.df_master = pd.read_csv(master_file) if master_file.exists() else pd.DataFrame()

        if df_geo is not None:
            self.df_geo = df_geo.copy()
        else:
            geo_file = DATA_PROCESSED_DIR / "farmacias_geolocalizadas.csv"
            self.df_geo = pd.read_csv(geo_file) if geo_file.exists() else pd.DataFrame()

        if df_preds is not None:
            self.df_preds = df_preds.copy()
        else:
            preds_file = DATA_PROCESSED_DIR / "predicciones_probabilidad_stock.csv"
            self.df_preds = pd.read_csv(preds_file) if preds_file.exists() else pd.DataFrame()

    def extraer_entidades(self, texto: str) -> Dict[str, Any]:
        """Extrae marcas, principios activos, formatos, anillos urbanos y dosis del mensaje."""
        normalizado = normalizar_texto(texto)
        entidades: Dict[str, Any] = {
            "marca": None,
            "principio_activo": None,
            "formato": None,
            "anillo": None,
            "cadena_farmacia": None,
            "dosis_diaria_ui": None,
        }

        # 1. Extracción de Marca Comercial
        for marca_oficial, sinonimos in self.MARCAS_CONOCIDAS.items():
            for sinonimo in sinonimos:
                patron = r"\b" + re.escape(normalizar_texto(sinonimo)) + r"\b"
                if re.search(patron, normalizado):
                    entidades["marca"] = marca_oficial
                    break
            if entidades["marca"]:
                break

        # 2. Extracción de Principio Activo
        for principio_oficial, sinonimos in self.PRINCIPIOS_ACTIVOS.items():
            for sinonimo in sinonimos:
                patron = r"\b" + re.escape(normalizar_texto(sinonimo)) + r"\b"
                if re.search(patron, normalizado):
                    entidades["principio_activo"] = principio_oficial
                    break
            if entidades["principio_activo"]:
                break

        # 3. Extracción de Formato
        for formato_oficial, sinonimos in self.FORMATOS_PRESENTACION.items():
            for sinonimo in sinonimos:
                patron = r"\b" + re.escape(normalizar_texto(sinonimo)) + r"\b"
                if re.search(patron, normalizado):
                    entidades["formato"] = formato_oficial
                    break
            if entidades["formato"]:
                break

        # 4. Extracción de Anillo Urbano (Santa Cruz de la Sierra: 1 al 8)
        # Casos especiales: "centro", "casco viejo" -> Anillo 1
        if re.search(r"\b(centro|casco viejo|plaza 24|plaza principal)\b", normalizado):
            entidades["anillo"] = 1
        else:
            match_anillo = re.search(r"\b([1-8])(?:er|do|ro|to|vo|mo)?\s+anillo\b", normalizado)
            if match_anillo:
                entidades["anillo"] = int(match_anillo.group(1))
            else:
                match_anillo_inv = re.search(r"\banillo\s+([1-8])\b", normalizado)
                if match_anillo_inv:
                    entidades["anillo"] = int(match_anillo_inv.group(1))

        # 5. Extracción de Cadena de Farmacia
        for cadena_oficial, sinonimos in self.CADENAS_FARMACIA.items():
            for sinonimo in sinonimos:
                patron = r"\b" + re.escape(normalizar_texto(sinonimo)) + r"\b"
                if re.search(patron, normalizado):
                    entidades["cadena_farmacia"] = cadena_oficial
                    break
            if entidades["cadena_farmacia"]:
                break

        # 6. Extracción de Dosis Diaria (UI o Unidades)
        match_dosis = re.search(r"\b(\d{1,3})\s*(?:ui|unidades|unidad|u)\b", normalizado)
        if match_dosis:
            dosis_val = float(match_dosis.group(1))
            if 1 <= dosis_val <= 150:
                entidades["dosis_diaria_ui"] = dosis_val

        return entidades

    def detectar_intencion(self, texto: str, entidades: Dict[str, Any]) -> str:
        """Determina la intención comunicativa de la consulta ciudadana."""
        normalizado = normalizar_texto(texto)

        # 1. Alerta médica / Intención de prescripción o dosificación médica (Desvío seguro)
        patron_medico = (
            r"\b(cuanta dosis|que dosis|dosis me pongo|dosis me debo poner|dosis tomar|dosis usar|"
            r"cuanto me inyecto|como inyectarme|recetame|recetar|prescribir|me cambio de insulina|"
            r"puedo cambiar|puedo sustituir|sustituir|cambiar de insulina|cambiar mi|"
            r"glucosa alta|azucar alta|hiperglucemia|hipoglucemia|sintomas|efectos secundarios|curar)\b"
        )
        if re.search(patron_medico, normalizado):
            return "CONSULTA_MEDICA_DESVIO"

        # 2. Saludo o solicitud de ayuda / orientación general
        if re.search(r"^(hola|buen dia|buenas tardes|buenas|buenos dias|que haces|que puedes hacer|ayuda|como funciona|quien eres)\b", normalizado):
            # Si solo saluda sin mencionar producto específico
            if not entidades["marca"] and not entidades["principio_activo"] and not entidades["anillo"] and not entidades["dosis_diaria_ui"]:
                return "SALUDO_Y_AYUDA"

        # 3. Cálculo de presupuesto o gasto mensual
        if entidades["dosis_diaria_ui"] is not None or re.search(r"\b(calculadora|presupuesto|cuanto gasto|al mes|para 30 dias|cuantos frascos|alcanza)\b", normalizado):
            return "CALCULAR_PRESUPUESTO_DOSIS"

        # 4. Consulta de sucursales o ubicación por anillo urbano
        if entidades["anillo"] is not None or re.search(r"\b(sucursales|sucursal|donde queda|direccion|cerca|ubicacion|donde hay farmacia|por mi casa)\b", normalizado):
            return "CONSULTAR_SUCURSALES_ANILLO"

        # 5. Consulta sobre estado de disponibilidad / quiebre de stock / semáforo
        if re.search(r"\b(hay stock|esta disponible|se agoto|quiebre|agotado|hay insulina|tienen stock|esta en falta|falta|semaforo|abastecimiento)\b", normalizado):
            return "CONSULTAR_DISPONIBILIDAD_STOCK"

        # 6. Consulta de precios y comparación económica (por defecto cuando menciona marca o precio)
        if entidades["marca"] or entidades["principio_activo"] or re.search(r"\b(precio|precios|cuanto cuesta|cuanto sale|mas barata|mas economica|ahorro|farmacorp|chavez|telchi)\b", normalizado):
            return "CONSULTAR_PRECIO_COMPARATIVO"

        return "CONSULTA_GENERAL"

    def responder(self, mensaje: str) -> Dict[str, Any]:
        """Procesa una consulta en lenguaje natural y genera una respuesta empática y fundamentada."""
        entidades = self.extraer_entidades(mensaje)
        intencion = self.detectar_intencion(mensaje, entidades)

        if intencion == "CONSULTA_MEDICA_DESVIO":
            return self._generar_desvio_medico()

        if intencion == "SALUDO_Y_AYUDA":
            return self._generar_saludo_ayuda()

        if intencion == "CALCULAR_PRESUPUESTO_DOSIS":
            return self._generar_respuesta_presupuesto(entidades)

        if intencion == "CONSULTAR_SUCURSALES_ANILLO":
            return self._generar_respuesta_sucursales(entidades)

        if intencion == "CONSULTAR_DISPONIBILIDAD_STOCK":
            return self._generar_respuesta_stock(entidades)

        if intencion == "CONSULTAR_PRECIO_COMPARATIVO":
            return self._generar_respuesta_precios(entidades)

        # Consulta general no categorizada
        if entidades.get("marca") or entidades.get("principio_activo"):
            return self._generar_respuesta_precios(entidades)
        return self._generar_saludo_ayuda(intencion="CONSULTA_GENERAL")

    # =========================================================================
    # GENERADORES DE RESPUESTAS EMPÁTICAS Y CIUDADANAS (ZERO ML JARGON)
    # =========================================================================

    def _generar_saludo_ayuda(self, intencion: str = "SALUDO_Y_AYUDA") -> Dict[str, Any]:
        """Respuesta cálida y accesible para la orientación de adultos mayores."""
        texto = (
            "¡Hola! Con mucho gusto le ayudo. 🩺\n\n"
            "Soy su Asistente de Insulina para Santa Cruz de la Sierra. Le puedo informar de manera sencilla sobre:\n"
            "• 💰 **Comparación de precios:** Cuánto cuesta su insulina y cuál farmacia la tiene más económica (Farmacorp, Chávez o Telchi).\n"
            "• 🚦 **Disponibilidad:** Si hay stock seguro hoy en farmacias o si conviene comprar con anticipación.\n"
            "• 📍 **Sucursales por anillo:** Farmacias cercanas a su hogar (del 1er al 8vo anillo o centro).\n"
            "• 🧮 **Presupuesto mensual:** Cuántos frascos necesita y cuánto dinero ahorrará al mes según su dosis diaria.\n\n"
            "¿Qué marca de insulina utiliza (por ejemplo: Lantus, Novolin N, Novolin R o Basalog) o qué consulta desea realizar?"
        )
        return {
            "intencion": intencion,
            "entidades": {},
            "respuesta_texto": texto,
            "medicamentos_encontrados": [],
            "mejor_opcion": {},
            "semaforo": "INFORMATIVO",
            "sucursales_recomendadas": [],
        }

    def _generar_desvio_medico(self) -> Dict[str, Any]:
        """Deriva éticamente las dudas de salud a profesionales médicos."""
        texto = (
            "⚠️ **Aviso de Salud Importante:**\n\n"
            "Como asistente de información de precios y farmacias, **no puedo indicar dosis, recetar medicamentos ni aconsejar cambios de insulina**.\n\n"
            "Su dosis y tipo de insulina deben ser indicados únicamente por su médico o especialista endocrinólogo. Por favor, consulte con su centro de salud o médico de cabecera antes de modificar su tratamiento.\n\n"
            "Si ya conoce la marca o dosis recetada por su médico, con gusto le ayudo a buscar el mejor precio en las farmacias de Santa Cruz. 🩺"
        )
        return {
            "intencion": "CONSULTA_MEDICA_DESVIO",
            "entidades": {},
            "respuesta_texto": texto,
            "medicamentos_encontrados": [],
            "mejor_opcion": {},
            "semaforo": "ALERTA_SALUD",
            "sucursales_recomendadas": [],
        }

    def _filtrar_medicamentos(self, entidades: Dict[str, Any]) -> pd.DataFrame:
        """Filtra el dataset maestro según marca, principio activo o formato."""
        if self.df_master.empty:
            return pd.DataFrame()

        df_res = self.df_master.copy()

        # Filtrar por marca comercial
        if entidades.get("marca"):
            marca_patron = normalizar_texto(entidades["marca"])
            df_res = df_res[df_res["marca_comercial"].astype(str).apply(
                lambda x: marca_patron in normalizar_texto(x)
            )]

        # Filtrar por principio activo si no se especificó marca o como filtro adicional
        if entidades.get("principio_activo") and df_res.empty:
            df_res = self.df_master.copy()
            pa_patron = normalizar_texto(entidades["principio_activo"])
            df_res = df_res[df_res["principio_activo"].astype(str).apply(
                lambda x: pa_patron in normalizar_texto(x)
            )]

        # Filtrar por formato si se indicó
        if entidades.get("formato") and not df_res.empty:
            formato_patron = normalizar_texto(entidades["formato"])
            sub_formato = df_res[df_res["formato_presentacion"].astype(str).apply(
                lambda x: formato_patron in normalizar_texto(x)
            )]
            if not sub_formato.empty:
                df_res = sub_formato

        return df_res

    def _generar_respuesta_precios(self, entidades: Dict[str, Any]) -> Dict[str, Any]:
        """Compara precios entre farmacias y destaca la mejor opción y el ahorro."""
        df_meds = self._filtrar_medicamentos(entidades)

        if df_meds.empty:
            marca_solicitada = entidades.get("marca") or "la insulina consultada"
            texto = (
                f"No encontré registros con el nombre '{marca_solicitada}' en el catálogo de farmacias de Santa Cruz.\n\n"
                "Le sugiero verificar el nombre en la caja de su medicamento (por ejemplo: Lantus, Novolin N, Novolin R, Basalog, Apidra o Toujeo) "
                "o escribir si busca insulina NPH, Glargina o Cristalina."
            )
            return {
                "intencion": "CONSULTAR_PRECIO_COMPARATIVO",
                "entidades": entidades,
                "respuesta_texto": texto,
                "medicamentos_encontrados": [],
                "mejor_opcion": {},
                "semaforo": "ROJO",
                "sucursales_recomendadas": [],
            }

        # Consolidar precios por farmacia
        marca_principal = df_meds["marca_comercial"].iloc[0]
        presentacion = df_meds["formato_presentacion"].iloc[0]
        principio = df_meds["principio_activo"].iloc[0]

        precios_por_farmacia: Dict[str, Dict[str, Any]] = {}
        for _, row in df_meds.iterrows():
            cadena = str(row["farmacia"])
            precio = float(row["precio_venta_bs"])
            estado = str(row["estado_stock"])
            # Tomar el menor precio si hay varias presentaciones de la misma cadena
            if cadena not in precios_por_farmacia or precio < precios_por_farmacia[cadena]["precio"]:
                precios_por_farmacia[cadena] = {
                    "precio": precio,
                    "estado": estado,
                    "disponible": estado.lower() in ["disponible", "ultimas unidades"],
                }

        # Evaluar mejor opción y ahorro
        disponibles = {k: v for k, v in precios_por_farmacia.items() if v["disponible"]}
        comparables = disponibles if disponibles else precios_por_farmacia

        mejor_cadena = min(comparables.keys(), key=lambda c: comparables[c]["precio"])
        precio_min = comparables[mejor_cadena]["precio"]
        precio_max = max(comparables[c]["precio"] for c in comparables)
        ahorro = precio_max - precio_min

        # Determinar semáforo de disponibilidad
        if any(v["estado"].lower() == "disponible" for v in precios_por_farmacia.values()):
            semaforo = "VERDE"
            semaforo_icono = "🟢"
            semaforo_mensaje = "Stock Seguro: Hay disponibilidad confirmada en farmacias."
        elif any(v["estado"].lower() == "ultimas unidades" for v in precios_por_farmacia.values()):
            semaforo = "AMARILLO"
            semaforo_icono = "🟡"
            semaforo_mensaje = "Precaución: Quedan pocas unidades. Le recomendamos consultar antes de ir."
        else:
            semaforo = "ROJO"
            semaforo_icono = "🔴"
            semaforo_mensaje = "Agotado: No se observó stock disponible en los catálogos en línea."

        # Construir redacción clara y respetuosa
        lineas = [
            f"🩺 **Información de {marca_principal}** ({presentacion} • {principio}):\n",
            f"{semaforo_icono} **Disponibilidad:** {semaforo_mensaje}\n",
            "💵 **Comparativa de Precios en Santa Cruz:**",
        ]

        for cad, datos in precios_por_farmacia.items():
            disp_txt = "Disponible" if datos["disponible"] else "Agotado temporalmente"
            lineas.append(f"• **{cad}:** Bs {datos['precio']:.2f} ({disp_txt})")

        lineas.append("")
        if ahorro > 0:
            lineas.append(
                f"💡 **Recomendación de Ahorro:**\n"
                f"La opción más económica es **{mejor_cadena}** a **Bs {precio_min:.2f}**. "
                f"¡Comprando allí se ahorra **Bs {ahorro:.2f}** frente a la farmacia más cara!"
            )
        else:
            lineas.append(f"💡 El mejor precio disponible es en **{mejor_cadena}** a **Bs {precio_min:.2f}**.")

        lineas.append("\n🗓️ *Consejo para jubilados:* Si cobra su renta en el Banco Unión a fin de mes, recuerde comprar con 3 a 5 días de anticipación para evitar filas y asegurar su medicamento.")

        return {
            "intencion": "CONSULTAR_PRECIO_COMPARATIVO",
            "entidades": entidades,
            "respuesta_texto": "\n".join(lineas),
            "medicamentos_encontrados": df_meds[["marca_comercial", "farmacia", "precio_venta_bs", "estado_stock"]].to_dict(orient="records"),
            "mejor_opcion": {
                "farmacia": mejor_cadena,
                "precio_bs": precio_min,
                "ahorro_bs": ahorro,
            },
            "semaforo": semaforo,
            "sucursales_recomendadas": [],
        }

    def _generar_respuesta_stock(self, entidades: Dict[str, Any]) -> Dict[str, Any]:
        """Responde a consultas centradas en si hay o no stock y el estado del semáforo preventivo."""
        df_meds = self._filtrar_medicamentos(entidades)

        if df_meds.empty:
            return self._generar_respuesta_precios(entidades)

        marca = df_meds["marca_comercial"].iloc[0]

        farmacias_con_stock = []
        farmacias_agotadas = []
        for _, row in df_meds.iterrows():
            cadena = str(row["farmacia"])
            estado = str(row["estado_stock"])
            precio = float(row["precio_venta_bs"])
            if estado.lower() in ["disponible", "ultimas unidades"]:
                farmacias_con_stock.append(f"• **{cadena}:** Con stock disponible a Bs {precio:.2f}")
            else:
                farmacias_agotadas.append(f"• **{cadena}:** Agotado en catálogo en línea")

        if farmacias_con_stock:
            semaforo = "VERDE"
            lineas = [
                f"🟢 **¡Buenas noticias! Hay stock de {marca} en Santa Cruz.**\n",
                "Farmacias donde puede encontrarla hoy:",
                *farmacias_con_stock,
            ]
            if farmacias_agotadas:
                lineas.append("\nFarmacias que reportan faltante temporal:")
                lineas.extend(farmacias_agotadas)
        else:
            semaforo = "ROJO"
            lineas = [
                f"🔴 **Alerta de Stock:** En este momento {marca} aparece como **agotada** en los catálogos en línea consultados.",
                "Le sugerimos consultar con su médico si puede sustituirla por otra presentación equivalente o llamar directamente a la farmacia antes de trasladarse.",
            ]

        lineas.append("\n🚦 *¿Qué significa el Semáforo?* Verde confirma stock en farmacias; Amarillo aconseja prevenir; y Rojo avisa falta generalizada.")

        return {
            "intencion": "CONSULTAR_DISPONIBILIDAD_STOCK",
            "entidades": entidades,
            "respuesta_texto": "\n".join(lineas),
            "medicamentos_encontrados": df_meds[["marca_comercial", "farmacia", "estado_stock"]].to_dict(orient="records"),
            "mejor_opcion": {},
            "semaforo": semaforo,
            "sucursales_recomendadas": [],
        }

    def _generar_respuesta_sucursales(self, entidades: Dict[str, Any]) -> Dict[str, Any]:
        """Informa sucursales de farmacias verificadas según anillo urbano en Santa Cruz."""
        anillo = entidades.get("anillo")
        cadena = entidades.get("cadena_farmacia")

        if self.df_geo.empty:
            texto = "No disponemos temporalmente del directorio de sucursales geolocalizadas."
            return {
                "intencion": "CONSULTAR_SUCURSALES_ANILLO",
                "entidades": entidades,
                "respuesta_texto": texto,
                "medicamentos_encontrados": [],
                "mejor_opcion": {},
                "semaforo": "INFORMATIVO",
                "sucursales_recomendadas": [],
            }

        df_suc = self.df_geo.copy()

        # Filtrar por cadena si se especificó
        if cadena:
            df_suc = df_suc[df_suc["farmacia"].str.contains(cadena, case=False, na=False)]

        # Filtrar por anillo
        if anillo is not None:
            df_suc_anillo = df_suc[df_suc["anillo_asignado"] == float(anillo)]
            if not df_suc_anillo.empty:
                df_suc = df_suc_anillo
            else:
                # Si no hay en ese anillo exacto, buscar en anillos contiguos
                anillos_cercanos = [float(anillo - 1), float(anillo + 1)]
                df_suc = df_suc[df_suc["anillo_asignado"].isin(anillos_cercanos)]

        # Limitar a 5 sucursales más representativas
        sucursales_lista = df_suc.head(5).to_dict(orient="records")

        if not sucursales_lista:
            texto = (
                f"No encontramos sucursales registradas directamente en el {anillo}to anillo.\n"
                "Las farmacias con mayor número de sucursales se encuentran sobre el 2do y 3er anillo."
            )
            return {
                "intencion": "CONSULTAR_SUCURSALES_ANILLO",
                "entidades": entidades,
                "respuesta_texto": texto,
                "medicamentos_encontrados": [],
                "mejor_opcion": {},
                "semaforo": "INFORMATIVO",
                "sucursales_recomendadas": [],
            }

        etiqueta_lugar = f"en el {anillo}do anillo / cercanías" if anillo else "principales en Santa Cruz"
        lineas = [
            f"📍 **Sucursales de Farmacias {etiqueta_lugar}:**\n",
            "Aquí tiene las direcciones confirmadas para que no camine de más:\n",
        ]

        for s in sucursales_lista:
            anillo_txt = f"{int(s['anillo_asignado'])}to Anillo" if pd.notna(s.get("anillo_asignado")) else "Ubicación céntrica"
            lineas.append(f"• **{s['farmacia']} - {s['nombre_sucursal']}** ({anillo_txt}):")
            lineas.append(f"  Dirección: {s['direccion']}\n")

        lineas.append("💡 *Recomendación:* Llame a la sucursal o pida que le reserven su insulina antes de salir de casa.")

        return {
            "intencion": "CONSULTAR_SUCURSALES_ANILLO",
            "entidades": entidades,
            "respuesta_texto": "\n".join(lineas),
            "medicamentos_encontrados": [],
            "mejor_opcion": {},
            "semaforo": "VERDE",
            "sucursales_recomendadas": sucursales_lista,
        }

    def _generar_respuesta_presupuesto(self, entidades: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula los frascos necesarios al mes y el ahorro estimado en Bolivianos."""
        dosis = entidades.get("dosis_diaria_ui") or 30.0  # Dosis típica por defecto
        dosis_mensual = dosis * 30.0

        df_meds = self._filtrar_medicamentos(entidades)
        if df_meds.empty:
            df_meds = self.df_master[self.df_master["marca_comercial"].str.contains("Lantus", case=False, na=False)]
            if df_meds.empty:
                df_meds = self.df_master.head(3)

        marca = df_meds["marca_comercial"].iloc[0] if not df_meds.empty else "Insulina"
        volumen_total_ui = float(df_meds["unidades_totales_ui"].iloc[0]) if not df_meds.empty and pd.notna(df_meds["unidades_totales_ui"].iloc[0]) else 1000.0

        frascos_necesarios = int(-(-dosis_mensual // volumen_total_ui))  # Ceiling division

        # Precios
        precios = df_meds["precio_venta_bs"].dropna().tolist()
        if precios:
            p_min = min(precios)
            p_max = max(precios)
            gasto_min = p_min * frascos_necesarios
            gasto_max = p_max * frascos_necesarios
            ahorro_mensual = gasto_max - gasto_min
        else:
            p_min = 120.0
            gasto_min = p_min * frascos_necesarios
            ahorro_mensual = 0.0

        lineas = [
            f"🧮 **Cálculo de Presupuesto Mensual ({marca}):**\n",
            f"• **Dosis diaria indicada:** {dosis:.0f} UI al día.",
            f"• **Consumo en 30 días:** {dosis_mensual:.0f} UI.",
            f"• **Frascos o cartuchos necesarios:** {frascos_necesarios} unidad(es) de {volumen_total_ui:.0f} UI cada una.\n",
            f"💰 **Gasto mensual estimado:** Bs {gasto_min:.2f} comprando en la farmacia más económica.",
        ]

        if ahorro_mensual > 0:
            lineas.append(f"🎉 **¡Ahorro mensual potencial:** Al elegir la farmacia más conveniente, se ahorra **Bs {ahorro_mensual:.2f} cada mes** frente a la más cara!")

        lineas.append("\n⚠️ *Nota:* Este es un cálculo económico orientativo. Use únicamente la dosis prescrita por su médico.")

        return {
            "intencion": "CALCULAR_PRESUPUESTO_DOSIS",
            "entidades": entidades,
            "respuesta_texto": "\n".join(lineas),
            "medicamentos_encontrados": df_meds[["marca_comercial", "farmacia", "precio_venta_bs"]].to_dict(orient="records"),
            "mejor_opcion": {
                "frascos_mes": frascos_necesarios,
                "gasto_mensual_min_bs": gasto_min,
                "ahorro_mensual_bs": ahorro_mensual,
            },
            "semaforo": "VERDE",
            "sucursales_recomendadas": [],
        }
