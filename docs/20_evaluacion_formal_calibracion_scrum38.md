# SCRUM-38 / US-41 — Evaluación formal y calibración

## 1. Objetivo

Evaluar de forma reproducible los modelos actuales sin modificar los artefactos productivos, separando estrictamente ajuste, calibración, selección de threshold y validación externa.

## 2. Dataset utilizado

- Archivo: `data/processed/dataset_analitico_modelado.csv`.
- SHA-256: `e3c3d8cd82dd6fc95472c320bd60a5b28c74f67d05af8d671221e467145da685`.
- Registros: 43; clase 0: 35; clase 1: 8.
- Python 3.12.4; scikit-learn 1.7.2; joblib 1.4.2; XGBoost NO_DISPONIBLE.
- Semillas outer: [42, 123, 2026].

## 3. Naturaleza del target

`quiebre_stock_inminente` es un **proxy del estado actual**: agotado o últimas unidades equivale a 1. No es un quiebre futuro observado y los resultados no validan pronóstico temporal ni riesgo clínico.

## 4. Por qué 4 folds

Con 8 positivos, cuatro folds ubican exactamente dos positivos en cada outer-validation. Cinco folds dejarían folds con un solo positivo y un error movería el recall en 100 puntos. Las repeticiones con distintas semillas miden sensibilidad a la partición, pero no crean observaciones nuevas.

## 5. Validación anidada

Se usó outer `StratifiedKFold(4)` repetido y inner `StratifiedKFold(3)`. El threshold se eligió solo con probabilidades inner-OOF del outer-train. El outer-validation nunca participó en preprocesamiento, calibración ni selección.

## 6. Threshold no es calibración

El threshold convierte probabilidades en clases. La calibración intenta alinear probabilidad estimada y frecuencia observada. Se evaluó el modelo sin calibrar, sigmoid y, solo exploratoriamente, isotonic.

## 7. Sigmoid e isotonic

Sigmoid es la variante calibrada principal por ser paramétrica. Isotonic es exploratorio: 43 filas y 8 positivos son insuficientes para recomendar una función escalonada flexible como artefacto productivo.

## 8. Matriz de costos

Escenario principal: TN=0, TP=0, FP=1, FN=5; `costo = 5*FN + FP`. Es una **penalización técnica relativa para evaluación**, no un costo clínico, económico ni médico. También se reportan razones 2:1 y 10:1.

## 9. Resultados outer-CV

| Modelo | Calibración | Recall medio | Precision media | ROC-AUC | PR-AUC/AP | Brier | Log-loss | FP medio | Proporción alertada | Estado Recall >=90% |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Dummy | sin_calibrar | 0.000 | 0.000 | 0.500 | 0.186 | 0.186 | 5.149 | 0.00 | 0.000 | NO_ALCANZADO_ESTABLEMENTE |
| Dummy | sigmoid | 0.000 | 0.000 | 0.500 | 0.186 | 0.153 | 0.484 | 0.00 | 0.000 | NO_ALCANZADO_ESTABLEMENTE |
| Dummy | isotonic_exploratorio | 0.000 | 0.000 | 0.500 | 0.186 | 0.152 | 0.481 | 0.00 | 0.000 | NO_ALCANZADO_ESTABLEMENTE |
| RandomForest | sin_calibrar | 0.667 | 0.169 | 0.405 | 0.268 | 0.204 | 0.596 | 6.33 | 0.711 | NO_ALCANZADO_ESTABLEMENTE |
| RandomForest | sigmoid | 0.333 | 0.122 | 0.434 | 0.283 | 0.161 | 0.505 | 4.50 | 0.485 | NO_ALCANZADO_ESTABLEMENTE |
| RandomForest | isotonic_exploratorio | 0.750 | 0.164 | 0.465 | 0.236 | 0.169 | 0.521 | 7.17 | 0.809 | NO_ALCANZADO_ESTABLEMENTE |
| LogisticRegression | sin_calibrar | 0.625 | 0.155 | 0.494 | 0.324 | 0.237 | 0.718 | 6.00 | 0.677 | NO_ALCANZADO_ESTABLEMENTE |
| LogisticRegression | sigmoid | 0.375 | 0.191 | 0.458 | 0.319 | 0.157 | 0.497 | 3.00 | 0.352 | NO_ALCANZADO_ESTABLEMENTE |
| LogisticRegression | isotonic_exploratorio | 0.542 | 0.130 | 0.392 | 0.218 | 0.172 | 0.923 | 6.33 | 0.690 | NO_ALCANZADO_ESTABLEMENTE |

Estado de modelos opcionales:

- **XGBoost:** `NO_DISPONIBLE_ENTORNO` — ModuleNotFoundError: No module named 'xgboost'

## 10. Recall >=90%, falsos positivos y estabilidad

Con 8 positivos, Recall >=90% exige detectar 8/8 en el conjunto OOF correspondiente. La clasificación final exige alcanzarlo en todos los outer folds y no solo como promedio. Una política se marca degenerada cuando alcanza el objetivo superando el límite técnico configurable de proporción alertada (80%); este límite se acompaña con sensibilidad 60%, 70%, 80%, 90% y 100% y no se presenta como criterio clínico.

## 11. ROC-AUC, PR-AUC y calibración

ROC-AUC y Average Precision se calcularon exclusivamente sobre outer-validation. Brier y log-loss evalúan calidad probabilística. Con tan pocos positivos, diferencias pequeñas entre variantes no constituyen evidencia fuerte y las curvas de confiabilidad contienen bins con pocos casos.

## 12. Limitaciones

- 43 observaciones y 8 positivos.
- Un único corte temporal; no hay evento futuro.
- Dependencia potencial entre productos similares y farmacias.
- Alta sensibilidad a las particiones.
- Isotonic puede sobreajustar.
- Las repeticiones CV reutilizan las mismas filas.
- El límite de alertas es una configuración técnica para sensibilidad, no una verdad clínica.

## 13. Recomendación final

No existe evidencia suficiente para afirmar que Recall >= 90% sea estable y útil. El objetivo debe reportarse como no alcanzado establemente o, cuando corresponda, alcanzado únicamente mediante una política degenerada.

No se modificaron joblib, threshold productivo, predicciones productivas ni pipeline web.
