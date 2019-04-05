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
    trechosItinerarios = sqlContext.read.json(processed_path + 'trechositinerarios/')
    trechosItinerarios.registerTempTable("trechos_itinerarios")


linhas = sqlContext.read.json(processed_path+'linhas/')
linhas.registerTempTable("linhas")

pontosLinha = sqlContext.read.json(processed_path+'pontoslinha/')
pontosLinha.registerTempTable("pontos_linha")

tabelaVeiculo = sqlContext.read.json(processed_path+'tabelaveiculo/')
tabelaVeiculo.registerTempTable("tabela_veiculo")

tabelaLinha = sqlContext.read.json(processed_path+'tabelalinha/')
tabelaLinha.registerTempTable("tabela_linha")

trechosItinerarios = sqlContext.read.json(processed_path+'trechositinerarios/')
trechosItinerarios.registerTempTable("trechos_itinerarios")

# position_events = sqlContext.read.json(processed_path+'veiculos/')
# position_events.registerTempTable("veiculos")


##### EMPRESAS ONIBUS

def create_empresas_onibus(trechosItinerarios):
    conn = UrbsNeo4JDatabase('bolt://172.17.0.2:7687', 'neo4j', 'neo4j2018')
    empresasOnibus = trechosItinerarios.select("COD_EMPRESA", "NOME_EMPRESA").distinct()

    empresas_df = empresasOnibus.toPandas()

    [conn.create_bus_company(row['COD_EMPRESA'], row['NOME_EMPRESA']) for index, row in empresas_df.iterrows()]
    conn.close()


#### CATEGORIAS ONIBUS
def create_categorias_onibus(trechosItinerarios):
    conn = UrbsNeo4JDatabase('bolt://172.17.0.2:7687', 'neo4j', 'neo4j2018')
    categoriasOnibus = trechosItinerarios.select('COD_CATEGORIA', 'NOME_CATEGORIA').distinct()

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


def create_bus_stops():
    conn = UrbsNeo4JDatabase('bolt://172.17.0.2:7687', 'neo4j', 'neo4j2018')
    pontos = sqlContext.sql("select distinct nome,num,tipo,lat,lon from pontos_linha where sourcedate = '2019-03-14' ")

    pontos_df = pontos.toPandas()

    pontos_df['address'] = pontos_df['nome'].map(lambda x: extract_address(x))
    pontos_df['neighborhood'] = pontos_df['nome'].map(lambda x: extract_neighborhood(x))

    [conn.create_bus_stop(row['nome'], row['num'], row['tipo'], row['lat'], row['lon'], row['address'],
                          row['neighborhood']) for index, row in pontos_df.iterrows()]
    conn.close()


def create_routes():
    conn = UrbsNeo4JDatabase('bolt://172.17.0.2:7687', 'neo4j', 'neo4j2018')

    query_view_rota_sequenciada = "CREATE OR REPLACE TEMPORARY VIEW rota_sequenciada AS  " \
                                  "select 	pseq.cod_linha,pseq.sentido_linha,pseq.seq_inicio,pseq.seq_fim,pseq.ponto_inicio,pseq.nome_ponto_inicio " \
                                  ",pseq.ponto_final,pseq.nome_ponto_final,li.CATEGORIA_SERVICO as categoria_servico,li.NOME as nome_linha,li.NOME_COR as nome_cor,li.SOMENTE_CARTAO as somente_cartao " \
                                  ",pseq.sourcedate " \
                                  "from (select " \
                                  "p1.COD as cod_linha " \
                                  ",p1.SENTIDO  as sentido_linha " \
                                  ",p1.SEQ      as seq_inicio " \
                                  ",p2.SEQ      as seq_fim " \
                                  ",p1.NUM      as ponto_inicio " \
                                  ",p1.NOME     as nome_ponto_inicio " \
                                  ",p2.NUM      as ponto_final " \
                                  ",p2.NOME     as nome_ponto_final " \
                                  ",p1.sourcedate " \
                                  "from pontos_linha P1 " \
                                  "inner join pontos_linha p2 on (p1.SEQ+1 = p2.SEQ and p1.COD = p2.COD and p1.SENTIDO = p2.SENTIDO and p1.sourcedate = p2.sourcedate) " \
                                  ") pseq " \
                                  "inner join linhas       li on (pseq.cod_linha = li.COD and pseq.sourcedate = li.sourcedate) " \
                                  "order by pseq.cod_linha,pseq.sentido_linha,pseq.seq_inicio,pseq.seq_fim "

    sqlContext.sql(query_view_rota_sequenciada)

    query_rota_sequenciada = "select cod_linha,sentido_linha,ponto_inicio,nome_ponto_inicio,ponto_final,nome_ponto_final,categoria_servico,nome_linha,nome_cor,somente_cartao " \
                             "from rota_sequenciada where sourcedate ='2019-03-14' and ponto_inicio != ponto_final"

    rota_sequenciada = sqlContext.sql(query_rota_sequenciada)
    rota_sequenciada_df = rota_sequenciada.toPandas()

    [conn.create_bus_lines(row['ponto_inicio'], row['ponto_final'], row['cod_linha'], row['sentido_linha'], row['categoria_servico'], row['nome_linha'], row['nome_cor'],
                           row['somente_cartao']) for index, row in rota_sequenciada_df.iterrows()]

    conn.close()



conn = UrbsNeo4JDatabase('bolt://172.17.0.2:7687', 'neo4j', 'neo4j2018')
conn.delete_all()
conn.close()

# trechosItinerarios = load_trechos_itinerarios()
# create_empresas_onibus(trechosItinerarios)
# create_categorias_onibus(trechosItinerarios)
create_bus_stops()
create_routes()



