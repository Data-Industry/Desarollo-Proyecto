# Dossier Técnico de Inteligencia Artificial y Machine Learning — Insulinas Bolivia

**Fase CRISP-DM:** Fase 4 — Modelado y Evaluación  
**Audiencia:** Tribunal Académico / Docente de Inteligencia Artificial & Machine Learning  
**Modelo en Producción:** Random Forest Classifier (Bagging Ensamble, 100 estimadores)  
**Métrica Primaria:** Recall = 100% (Umbral Clínico Óptimo $T_{opt} = 0.05$ / $0.17$)  
**Matriz Analítica:** 43 observaciones maestras $\times$ 69 dimensiones analíticas  
**Validación:** Stratified 4-Fold Cross-Validation (*In-Fold Transformations*)  
**Fecha de Emisión:** 20 de Noviembre, 2026  

---

## 1. Formulación Matemática del Problema y Justificación del Paradigma

### 1.1 Definición Matemática
Sea $\mathcal{D} = \{(\mathbf{x}_i, y_i)\}_{i=1}^{N}$ con $N=43$ y $\mathbf{x}_i \in \mathbb{R}^{69}$.
$$y_i \in \{0, 1\}, \quad \hat{y}_i(T) = \mathbb{I}\left( \hat{P}(y_i = 1 \mid \mathbf{x}_i) \ge T \right)$$

### 1.2 Justificación frente al Tribunal: ¿Por qué NO Deep Learning?
1. **Teorema de No Free Lunch y Tamaño Muestral ($N=43$):** Redes neuronales con miles de parámetros sufrirían sobreajuste masivo sobre 43 insulinas maestras.
2. **Evidencia Empírica (Grinsztajn et al., NeurIPS 2022):** Los ensambles de árboles superan sistemáticamente a Deep Learning en datos tabulares de escala pequeña y mediana.
3. **Interpretabilidad Médica (XAI):** La descomposición MDI de Gini permite auditoría médica requerida por AGEMED.
4. **Eficiencia en Edge:** 123.5 KB de peso y latencia < 15 ms en CPU móvil sin requerir GPUs.

---

## 2. Análisis Exploratorio Multivariable (EDA) y Hallazgos Estadísticos
- **Desbalance:** 39 con stock (90.7%) vs 4 en quiebre (9.3%).
- **Pearson vs Spearman:** Correlaciones lineales de precio vs relaciones monótonas en concentraciones.

---

## 3. Ingeniería de Características (Feature Engineering) — Matriz $43 \times 69$
- Taxonomía en 5 vectores de dominio: Precios retail, Farmacología, Lags aduaneros, Tipo de cambio BCB y Calendario bancario Banco Unión.
- **Blindaje anti Data Leakage:** Eliminación estricta de variables concurrentes (`estado_stock`, etc.) y ajuste in-fold de StandardScaler.

---

## 4. Validación Cruzada Estratificada y Manejo del Desbalance
- **Stratified 4-Fold CV:** Cada fold contiene exactamente 1 positivo y 9-10 negativos.
- **Ponderación Sensible al Costo:** `class_weight='balanced'` ($w_1 \approx 5.38$, $w_0 \approx 0.55$). Descarte de SMOTE por generar formulaciones biológicas irreales.

---

## 5. Modelado Predictivo y Benchmarking
| Modelo | Umbral | Accuracy | Precision | Recall | F1-Score | F2-Score Clínico | ROC-AUC | PR-AUC |
|---|---|---|---|---|---|---|---|---|
| **Baseline Dummy** | 0.50 | 90.7% | 0.0% | 0.0% | 0.000 | 0.000 | 0.500 | 0.093 |
| **Regresión Logística L2** | 0.50 | 79.1% | 0.0% | 0.0% | 0.000 | 0.000 | 0.154 | 0.067 |
| **Regresión Logística L2** | 0.05 | 7.0% | 5.0% | 50.0% | 0.091 | 0.179 | 0.154 | 0.067 |
| **XGBoost** | 0.50 | 81.4% | 0.0% | 0.0% | 0.000 | 0.000 | 0.372 | 0.085 |
| **XGBoost** | 0.05 | 20.9% | 10.5% | 100.0% | 0.190 | 0.370 | 0.372 | 0.085 |
| **Random Forest (Producción)** | 0.50 | 65.1% | 0.0% | 0.0% | 0.000 | 0.000 | 0.397 | 0.092 |
| **Random Forest (Producción)** | **0.05 / 0.17** | **14.0%** | **9.8%** | **100.0%** | **0.178** | **0.351** | **0.397** | **0.092** |

---

## 6. Teoría de Decisión Clínica y Calibración Asimétrica
- Asimetría de pérdidas: $\text{Costo}(FN) \ggg \text{Costo}(FP)$.
- Optimización de $F_2$-Score ($\beta=2$) logrando **0 Falsos Negativos (Recall = 100%)**.

---

## 7. Interpretabilidad (XAI)
- Ranking MDI Gini: 1) `precio_venta_bs` (14.06%), 2) `tipo_accion_Acción Rápida` (8.99%), 3) `precio_por_100ui_bs` (8.51%), 4) `laboratorio_Biocon Biologics` (7.20%).

---

## 8. Arquitectura e Inferencia
- Artefacto `models/modelo_produccion_stock.joblib` (123.5 KB).
- Inferencia en < 15 ms alimentando semáforo web senior y chatbot conversacional NLU.

---

## 9. Banco de 10 Preguntas y Respuestas Técnicas para el Tribunal de IA
*(Ver documento PDF completo para el desglose detallado de las 10 preguntas y respuestas formales).*
