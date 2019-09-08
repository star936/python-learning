# coding: utf-8


from pyspark import SparkContext, SparkConf


def create_spark_context():
    spark_conf = SparkConf().setAppName("WordCount")\
        .set("spark.ui.showConsoleProgress", "false")  # 设置不要显示spark执行进度
    sc = SparkContext(conf=spark_conf)

    print('master:{}'.format(sc.master))

    set_logger(sc)
    set_path(sc)

    return sc


def set_logger(sc):
    """设置不要显示太多信息"""
    logger = sc._jvm.org.apache.log4j
    logger.LogManager.getLogger('org').setLevel(logger.Level.ERROR)
    logger.LogManager.getLogger('akka').setLevel(logger.Level.ERROR)
    logger.LogManager.getRootLogger().setLevel(logger.Level.ERROR)


def set_path(sc):
    global Path
    if sc.master[:5] == 'local':
        Path = "file:/Users/dang/work/pywork/python-learning/data/"
    else:
        Path = "hdfs://localhost:9000/user/dang/data/"


if __name__ == '__main__':
    print('start')
    sc, path = create_spark_context()
    textFile = sc.textFile(path + "wordcount.txt")
    print('file has {} lines'.format(textFile.count()))

    countRDD = textFile.flatMap(lambda line: line.split(','))\
        .map(lambda word: (word, 1)).reduceByKey(lambda x, y: x+y)
    print('file has {} distinct words'.format(countRDD.count()))
    print(countRDD.collect())






