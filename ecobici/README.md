# ecobici-challenge

El objetivo del proyecto es predecir la demanda de ecobicis para cada uno de los cuadrantes de la ciudad. Se interpreta que se busca predecir la demanda agregada por cuadrante, y no individualmente por estación.

Se cuenta con información provista del historial de viajes del año 2022. Además, como parte del proyecto, se incluyó información de clima y feriados, que afectan fuertemente la demanada de bicis. 

Para ejecutar el algoritmo, es necesario correr los siguientes archivos:

(Aclaración - Por temas de espacio no se sube a github el csv trips_2022, pero la ubicación esperada es en la carpeta data)

Las versiones de cada librería necesarias se encuentran en el archivo requirements.txt (pip install -r requirements.txt)

1) Pre-processing\
Archivo: preprocessing.py\
Objetivo: Leer el dataset de trips y generar nuevas features.\
Cómo correr: python preprocessing.py\
Resumen: A partir del dataset de trips, y de los datasets incorporados de clima y feriados se implementan los siguientes pasos:
- Asignar un cuadrante a cada estación
- Agrupar data a nivel cuadrante y día que es el nivel de agregación para predecir
- Sumar nuevas varibales de clima como temperaturas y precipitaciones por día
- Incorporar feriados a traves de la librería holidays
- Calcular promedios móviles para la cantidad de viajes
- Identificar outliers por día de la semana y cuadrante e imputar con la media de ese día y cuadrante
- Se guarda el nuevo dataset en trips_preprocessed

2) Entrenamiento modelo\
Archivo: fit.py\
Objetivo: Entrenar 2 modelos para predicir la cantidad de viajes por día y cuadrante en la ciudad de buenos aires.\
Resumen: Se define entrenar un modelo XGBoost ya que tiene buena performance al considerar variables exógenas, y un modelo de series de tiempo Auto-Arima en el cual también se incluyen variables exógenas, e incluye técnicas automatizadas para seleccionar hiper-parámetros.
Consideraciones:
- Para train se usa de enero a octubre, y test noviembre y diciembre.
- En el caso de XGBoost se entrena 1 solo modelo con cuadrante como feature. En el caso de las series de tiempo, se entrena una distinta para cada cuadrante
- Se definen RMSE y MAPE como métricas de evaluación
- Las métricas de evaluación se visualizan en la terminal cuando se corre el archivo
- Los modelos entrenados se guardan en archivos .pkl en la carpeta models

Evaluación de la corrida

XGBoost\
Test - Root Mean Squared Error:       389.7823644860491\
Test - Mean Absolute Percetage Error: 0.1488598513865096\

XGBoost - Tuned Random Search\
Test - Root Mean Squared Error:       391.18908589822973\
Test - Mean Absolute Percetage Error: 0.152156800545546\

Auto-Arima \
Test - Root Mean Squared Error:       731.3884182517955\
Test - Mean Absolute Percetage Error: 0.39134692902666895\

Comentarios acerca de los modelos:\
- La comparación entre XGBoost y Series de Tiempo no es 100% justa ya que para entrenar XGBoost se usaron features como # de viajes promedio de la última semana, por lo cual el modelo en test tenía visibilidad de la historia de la semana anterior. En el caso del modelo de series de tiempo (auto-arima) se entrenó la serie hasta octubre y se predijo Noviembre y Diciembre, por lo cual el modelo no tenía visibilidad de la información más reciente. Para que sea comparable, habría que reentrenar las series de tiempo semanalmente. Efectivamente la performance de las series de tiempo fue muy inferior.
- El modelo con los hiper-parámetros encontrados con RandomSearch no tuvo mejor performance que el modelo original con los hiperpareametros base. Sería necesario seguir iterando o visualizar en detalle algunos de los parámetros más relevantes para ver como cambia la performance con cada valor.
- Sería útil contar con información más allá de 1 año para entender mejor los cambios estacionales, y poder utilizar información de todo el año para entrenar. 

Con esta información, el modelo seleccionado sería XGBoost, con oportunidad de seguir buscando una mejor optimización de hiper-parámetros.


Además, se incluyen 2 notebooks con visualizaciones y comentarios del proyecto. Estas son exploration.ipynb donde se hace un primer análisis exploratorio, y evaluation.ipynb donde se visualizan y comparan los resultados de las distintas corridas.

En la carpeta utils se encuentran algunas funciones que se utilizan para preprocesar o visualizar los datos.