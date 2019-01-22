###
## 1 - Download data from  https://www.prf.gov.br/portal/dados-abertos/acidentes/acidentes
## 2 - Data Dictionary https://www1.prf.gov.br/arquivos/index.php/s/9JIz6yPXT71l9Gf#pdfviewer
##


import json
import os
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
import urllib.request
import sys, getopt
import random
import datetime
import geojson
from shapely.geometry import shape,Polygon,Point
from scipy.spatial import ConvexHull
from scipy.ndimage.interpolation import rotate
from bson import json_util

path = os.getcwd()+'/accidents'

print(path)

kms_per_radian = 6371.0088

# 100 metros
epsilon = 0.1 / kms_per_radian

def load_dataset(dataset_name,index_column_name,sep):
    try:
        dataframe = pd.read_csv(dataset_name, sep=sep, parse_dates=True, infer_datetime_format=True)
        return dataframe
    except Exception:
        print("Ocorreu um erro ao tentar carregar o arquivo.")


def dbscan_fit(coords_dataset, min_samples=3):
    model = DBSCAN(eps=epsilon, min_samples=min_samples, algorithm='ball_tree', metric='haversine', n_jobs=1).fit(np.radians(coords_dataset))
    num_clusters = len(set(model.labels_))
    print('Number of clusters: {:,}'.format(num_clusters))
    return pd.Series([coords[model.labels_ == n] for n in range(len(set(model.labels_)))])

def remove_duplicated_points(df):
    return  df.drop_duplicates(['latitude','longitude'])[['latitude','longitude']]

def sort_points(df):
    return df.sort_values(by=['latitude', 'longitude'], ascending=False)


def get_clustered_points(cluster_dataframe):
    t = pd.DataFrame([])
    matrix = cluster_dataframe.as_matrix(columns=['longitude', 'latitude'])
    for i in range(0,len(matrix)):
        t = t.append(df.loc[(df['longitude'] == matrix[i][0]) & (df['latitude'] == matrix[i][1])])
    return t

def default(o):
    if isinstance(o, np.int64): 
        return int(o)  
    raise TypeError


def minimum_bounding_rectangle(points):
    """
    Find the smallest bounding rectangle for a set of points.
    Returns a set of points representing the corners of the bounding box.

    :param points: an nx2 matrix of coordinates
    :rval: an nx2 matrix of coordinates
    """
 
    pi2 = np.pi/2.

    # get the convex hull for the points
    hull_points = points[ConvexHull(points).vertices]

    # calculate edge angles
    edges = np.zeros((len(hull_points)-1, 2))
    edges = hull_points[1:] - hull_points[:-1]

    angles = np.zeros((len(edges)))
    angles = np.arctan2(edges[:, 1], edges[:, 0])

    angles = np.abs(np.mod(angles, pi2))
    angles = np.unique(angles)

    # find rotation matrices
    # XXX both work
    rotations = np.vstack([
        np.cos(angles),
        np.cos(angles-pi2),
        np.cos(angles+pi2),
        np.cos(angles)]).T
    rotations = rotations.reshape((-1, 2, 2))

    # apply rotations to the hull
    rot_points = np.dot(rotations, hull_points.T)

    # find the bounding points
    min_x = np.nanmin(rot_points[:, 0], axis=1)
    max_x = np.nanmax(rot_points[:, 0], axis=1)
    min_y = np.nanmin(rot_points[:, 1], axis=1)
    max_y = np.nanmax(rot_points[:, 1], axis=1)

    # find the box with the best area
    areas = (max_x - min_x) * (max_y - min_y)
    best_idx = np.argmin(areas)

    # return the best box
    x1 = max_x[best_idx]
    x2 = min_x[best_idx]
    y1 = max_y[best_idx]
    y2 = min_y[best_idx]
    r = rotations[best_idx]

    rval = np.zeros((4, 2))
    rval[0] = np.dot([x1, y2], r)
    rval[1] = np.dot([x2, y2], r)
    rval[2] = np.dot([x2, y1], r)
    rval[3] = np.dot([x1, y1], r)

    lp = [ Point(p[1],p[0]) for p in rval ]
    polygon = Polygon([(p.x, p.y) for p in lp])

    return polygon.wkt


def generate_bouding_box(df):
    
    try:
        poly = Polygon([[p.longitude, p.latitude] for p in df.itertuples()])
        x = poly.buffer(0.0003,3)

        list_of_points = np.array([ [lat,lon] for lon,lat in x.exterior.coords])

        return minimum_bounding_rectangle(list_of_points)
    except:
        return ''


def generate_data(clusters):
    accidents_list = []
    for i in range(0,len(clusters)):
        dictionary = {}
        polygon = generate_bouding_box(clusters[i])

        if(polygon != ''):
            t = get_clustered_points(clusters[i])
            if (len(t) > 20):
                dictionary['acidentes'] = len(t)
                dictionary['municipios'] = [x.replace('  ', '') for x in t.municipio.unique()]
                dictionary['pessoas'] = t.pessoas.sum()
                dictionary['mortos'] = t.mortos.sum()
                dictionary['feridos-leves'] = t.feridos_leves.sum()
                dictionary['feridos-grave'] = t.feridos_graves.sum()
                dictionary['tipos-acidente'] = {k.replace("  ",""): v for k,v in t.tipo_acidente.value_counts().to_dict().items()}
                dictionary['fase-dia'] = {k.replace("  ",""): v for k,v in t.fase_dia.value_counts().to_dict().items()}
                dictionary['polygon'] = polygon
                accidents_list.append(dictionary)
    return accidents_list    


def save_data(accidents_list):
    print("prepare to write data to file...")
    with open(path+'/accidents.ndjson', 'w') as f:  
        for document in accidents_list:
            f.write(json_util.dumps(document,default=default,ensure_ascii=False)+'\n')
    

import time
from datetime import timedelta
start_time = time.monotonic()

print("starting...")
df = load_dataset(path+'/data/regioes/accidents_brasil_cleansed.csv','data_inversa',';')    
coords = remove_duplicated_points(df)
coords = sort_points(coords)

clusters = dbscan_fit(coords)

accidents = generate_data(clusters)
save_data(accidents)
print("finish")

end_time = time.monotonic()
print(timedelta(seconds=end_time - start_time))