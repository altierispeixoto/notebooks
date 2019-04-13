import findspark

findspark.init()
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SQLContext

from neo4jcrud  import UrbsNeo4JDatabase

class DataLoader:

    def __init__(self):
        self.conf = SparkConf().setAppName("App")
        self.conf = (self.conf.setMaster('local[*]')
                     .set('spark.executor.memory', '4G')
                     .set('spark.driver.memory', '30G')
                     .set('spark.driver.maxResultSize', '10G'))

        self.sc = SparkContext.getOrCreate(conf=self.conf)
        self.sqlContext = SQLContext(self.sc)

    def load_data(self, src):
        return self.sqlContext.read.parquet(src)


    def create_empresas_onibus(self,trechosItinerarios,conn):

        empresasOnibus = trechosItinerarios.select("COD_EMPRESA", "NOME_EMPRESA").distinct()
        empresas_df = empresasOnibus.toPandas()
        [conn.create_bus_company(row['COD_EMPRESA'], row['NOME_EMPRESA']) for index, row in empresas_df.iterrows()]

    #### CATEGORIAS ONIBUS
    def create_categorias_onibus(self,trechosItinerarios,conn):
        categoriasOnibus = trechosItinerarios.select('COD_CATEGORIA', 'NOME_CATEGORIA').distinct()

        categorias_df = categoriasOnibus.toPandas()
        [conn.create_bus_category(row['COD_CATEGORIA'], row['NOME_CATEGORIA']) for index, row in categorias_df.iterrows()]


    def create_bus_stops(self, pontos_linha):

        pontos = self.sqlContext.sql("select distinct nome,num,tipo,lat,lon from pontos_linha where sourcedate = '2019-03-14' ")

        pontos_df = pontos.toPandas()

        [conn.create_bus_stop(row['nome'], row['num'], row['tipo'], row['lat'], row['lon']) for index, row in pontos_df.iterrows()]



if __name__ == '__main__':
    NEO4J_URI = 'bolt://172.17.0.2:7687'
    NEO4J_USER = 'neo4j'
    NEO4J_PASSWORD = 'neo4j2018'

    conn = UrbsNeo4JDatabase(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
    dataloader = DataLoader()

    trechositinerarios_source_path = '/home/altieris/datascience/data/curitibaurbs/processed/trechositinerarios/'

    # trechositinerarios = dataloader.load_data(trechositinerarios_source_path)
    # dataloader.create_empresas_onibus(trechositinerarios, conn)
    # dataloader.create_categorias_onibus(trechositinerarios, conn)

    pontos_linha_source_path = '/home/altieris/datascience/data/curitibaurbs/processed/pontoslinha/'
    pontos_linha = dataloader.load_data(pontos_linha_source_path)

    pontos_linha.select('filename').show()



    conn.close()