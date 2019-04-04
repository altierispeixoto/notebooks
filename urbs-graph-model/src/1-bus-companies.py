import findspark
findspark.init()

import pyspark
import random
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SQLContext

from database import UrbsNeo4JDatabase

conf = SparkConf().setAppName("App")
conf = (conf.setMaster('local[*]')
        .set('spark.executor.memory', '4G')
        .set('spark.driver.memory', '30G')
        .set('spark.driver.maxResultSize', '10G'))

sc = SparkContext.getOrCreate(conf=conf)
sqlContext = SQLContext(sc)





processed_path = '/home/altieris/datascience/data/curitibaurbs/processed/'

def load_trechos_itinerarios():
        trechosItinerarios = sqlContext.read.json(processed_path+'trechositinerarios/')
        trechosItinerarios.registerTempTable("trechos_itinerarios")

pontosLinha = sqlContext.read.json(processed_path+'pontoslinha/')
pontosLinha.registerTempTable("pontos_linha")


##### EMPRESAS ONIBUS

def create_empresas_onibus(trechosItinerarios):
        conn = UrbsNeo4JDatabase('bolt://172.17.0.2:7687', 'neo4j', 'neo4j2018')
        empresasOnibus = trechosItinerarios.select("COD_EMPRESA","NOME_EMPRESA").distinct()

        empresas_df = empresasOnibus.toPandas()

        [conn.create_bus_company(row['COD_EMPRESA'], row['NOME_EMPRESA']) for index, row in empresas_df.iterrows()]
        conn.close()

#### CATEGORIAS ONIBUS
def create_categorias_onibus(trechosItinerarios):
        conn = UrbsNeo4JDatabase('bolt://172.17.0.2:7687', 'neo4j', 'neo4j2018')
        categoriasOnibus = trechosItinerarios.select('COD_CATEGORIA','NOME_CATEGORIA').distinct()

        categorias_df = categoriasOnibus.toPandas()
        [conn.create_bus_category(row['COD_CATEGORIA'], row['NOME_CATEGORIA']) for index, row in categorias_df.iterrows()]
        conn.close()

def extract_address(x):
        return x.split('-')[0]

def extract_neighborhood(x):
        l = x.split('-')
        if len(l) > 1:
                return l[1]
        return l[0]

def create_pontos_onibus():
        conn = UrbsNeo4JDatabase('bolt://172.17.0.2:7687', 'neo4j', 'neo4j2018')
        pontos = sqlContext.sql("select nome,num,tipo,lat,lon from pontos_linha where sourcedate = '2019-03-14' ")

        pontos_df = pontos.toPandas()

        pontos_df['address'] = pontos_df['nome'].map(lambda x :extract_address(x))
        pontos_df['neighborhood'] = pontos_df['nome'].map(lambda x: extract_neighborhood(x))

        [conn.create_bus_stop(row['nome'], row['num'],row['tipo'],row['lat'],row['lon'],row['address'],row['neighborhood']) for index, row in pontos_df.iterrows()]
        conn.close()


conn = UrbsNeo4JDatabase('bolt://172.17.0.2:7687', 'neo4j', 'neo4j2018')
conn.delete_all()
conn.close()

# trechosItinerarios = load_trechos_itinerarios()
# create_empresas_onibus(trechosItinerarios)
# create_categorias_onibus(trechosItinerarios)
create_pontos_onibus()


