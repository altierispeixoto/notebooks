import findspark

findspark.init()
from pyspark.conf import SparkConf
from pyspark.context import SparkContext
from pyspark.sql import SQLContext
from pyspark.sql.functions import input_file_name
import gc


class ETLSpark:

    def __init__(self):
        self.conf = SparkConf().setAppName("App")
        self.conf = (self.conf.setMaster('local[*]')
                     .set('spark.executor.memory', '4G')
                     .set('spark.driver.memory', '30G')
                     .set('spark.driver.maxResultSize', '10G'))

        self.sc = SparkContext.getOrCreate(conf=self.conf)
        self.sqlContext = SQLContext(self.sc)

    def extract(self, src):
        return self.sqlContext.read.json(src).withColumn("filename", input_file_name())

    def transform(self, src_data, target_path, coalesce=1):
        src_data.coalesce(coalesce).write.mode('overwrite').format("parquet").save(target_path)
        del src_data
        gc.collect()
