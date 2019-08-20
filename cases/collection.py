# coding: utf-8

from dataclasses import dataclass, field


# 去过普吉岛的人员数据
users_visited_phuket = [
    {"first_name": "Sirena", "last_name": "Gross", "phone_number": "650-568-0388", "date_visited": "2018-03-14"},
    {"first_name": "James", "last_name": "Ashcraft", "phone_number": "412-334-4380", "date_visited": "2014-09-16"},
]

# 去过新西兰的人员数据
users_visited_nz = [
    {"first_name": "Justin", "last_name": "Malcom", "phone_number": "267-282-1964", "date_visited": "2011-03-13"},
    {"first_name": "Albert", "last_name": "Potter", "phone_number": "702-249-3714", "date_visited": "2013-09-11"},
]


def find_potential_customers_v1():
    """找到去过普吉岛但是没去过新西兰的人，性能改进版"""
    # 首先，遍历所有新西兰访问记录，创建查找索引
    nz_records_idx = {
        (rec['first_name'], rec['last_name'], rec['phone_number'])
        for rec in users_visited_nz
    }

    for rec in users_visited_phuket:
        key = (rec['first_name'], rec['last_name'], rec['phone_number'])
        if key not in nz_records_idx:
            yield rec


class VisitRecord:
    """旅游记录"""
    def __init__(self, first_name, last_name, phone_number, date_visited):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.date_visited = date_visited

    def __hash__(self):
        return hash(
            (self.first_name, self.last_name, self.phone_number)
        )

    def __eq__(self, other):
        if isinstance(other, VisitRecord) and hash(other) == hash(self):
            return True
        return False

def find_potential_customers_v2():
    return set(VisitRecord(**r) for r in users_visited_phuket) - \
        set(VisitRecord(**r) for r in users_visited_nz)


# 以下方法需要Python3.7+版本才能使用
@dataclass(unsafe_hash=True)
class VisitRecordDC:
    first_name: str
    last_name: str
    phone_number: str
    # 跳过“访问时间”字段，不作为任何对比条件
    date_visited: str = field(hash=False, compare=False)


def find_potential_customers_v3():
    return set(VisitRecordDC(**r) for r in users_visited_phuket) - \
        set(VisitRecordDC(**r) for r in users_visited_nz)