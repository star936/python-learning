# coding: utf-8


"""
邻接表实现:
    Graph: 保存了包含所有顶点的主表
    Vertex: 描绘了图表中顶点的信息,每一个vertex使用一个字典来记录顶点与顶点之间的连接关系和每条连接边的权重.
"""


class Vertex(object):
    def __init__(self, key):
        self.id = key
        self.connected_to = {}

    def add_neighbor(self, neighbor, weight=0):
        """添加从一个顶点到另一个顶点的连接"""
        self.connected_to[neighbor] = weight

    def get_connections(self):
        """返回以connected_to字典中的实例变量所表示的邻接表中的所有顶点"""
        return self.connected_to.keys()

    def get_id(self):
        return self.id

    def get_weight(self, neighbor):
        """返回顶点与顶点之间边的权重"""
        return self.connected_to[neighbor]

    def __str__(self):
        return str(self.id) + " connected to: " + str([x.id for x in self.connected_to])


class Graph(object):
    def __init__(self):
        self.vertices = {}
        self.num_vertex = 0

    def add_vertex(self, key):
        self.num_vertex = self.num_vertex + 1
        vertex = Vertex(key)
        self.vertices[key] = vertex
        return vertex

    def get_vertex(self, key):
        if key in self.vertices:
            return self.vertices[key]
        else:
            return None

    def __contains__(self, key):
        return key in self.vertices

    def add_edge(self, f, t, cost=0):
        if f not in self.vertices:
            nv = self.add_vertex(f)
        if t not in self.vertices:
            nv = self.add_vertex(t)
            self.vertices[f].add_neighbor(self.vertices[t], cost)

    def get_vertices(self):
        return self.vertices.keys()

    def __iter__(self):
        return iter(self.vertices.values())


