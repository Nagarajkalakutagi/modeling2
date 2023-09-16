from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
# Create your views here.
from rest.models import Users
from rest.serializer import AddUserSerializers
from rest_framework.status import *


class ResultView(viewsets.ViewSet):
    def create(self, request):
        try:
            data = request.data
            query = 'WITH'

            for qr in data['nodes']:
                if qr['type'] == 'INPUT':
                    tm_query = ''
                    dt = qr['transformObject']
                    key = qr['key']
                    table_name = dt['tableName']
                    all_fields = dt['fields']
                    fields_len = len(all_fields)
                    for i in range(fields_len):
                        fields = all_fields[i]

                        if i < fields_len - 1:
                            tm_query = f'{tm_query} {fields},'
                        else:
                            tm_query = f'{tm_query} {fields}'

                    query = f'{query} {key} as (SELECT {tm_query} FROM rest_{table_name}),'

                elif qr['type'] == 'FILTER':
                    pr_key = qr['key']
                    tfo = qr['transformObject']
                    field_name = tfo['variable_field_name']
                    join_operator = tfo['joinOperator']
                    query = f'{query} {pr_key} as (SELECT {tm_query} FROM {key} WHERE'
                    tfo_len = len(tfo['operations'])
                    for i in range(tfo_len):
                        operator = tfo['operations'][i]['operator']
                        value = tfo['operations'][i]['value']

                        if i < tfo_len - 1:
                            query = f'{query} {field_name} {operator} {value} {join_operator}'
                        else:
                            query = f'{query} {field_name} {operator} {value}'
                    query = f'{query}),'
                    key = pr_key

                elif qr['type'] == 'SORT':
                    pr_key = qr['key']
                    query = f'{query} {pr_key} as (SELECT {tm_query} FROM {key} ORDER BY'
                    tfo_len = len(qr['transformObject'])
                    for i in range(tfo_len):
                        dt = qr['transformObject'][i]
                        target = dt['target']
                        order = dt['order']
                        if i < tfo_len - 1:
                            query = f'{query} {target} {order},'
                        else:
                            query = f'{query} {target} {order}'

                    query = f'{query}),'
                    key = pr_key

                elif qr['type'] == 'LIKE_CLAUSE':
                    column = qr['transformObject']['column']
                    operator_value = qr['transformObject']['operator_value']
                    pr_key = qr['key']
                    query = f"{query} {pr_key} as (SELECT {tm_query} FROM {key} WHERE {column} LIKE '{operator_value}' ),"
                    key = pr_key

                elif qr['type'] == 'TEXT_TRANSFORMATION':
                    pr_key = qr['key']
                    tm_query2 = {}
                    for tfo in qr['transformObject']:
                        column = tfo['column']
                        transformation = tfo['transformation']
                        for fd in all_fields:
                            if fd == column:
                                tm_query2[column] = f'{transformation}({column}) as {column}'
                            else:
                                tm_query2[fd] = fd

                    fields_len = len(all_fields)
                    tm_query3 = ''
                    for i in range(fields_len):
                        fd = tm_query2[all_fields[i]]
                        if i < fields_len - 1:
                            tm_query3 = f'{tm_query3} {fd},'
                        else:
                            tm_query3 = f'{tm_query3} {fd}'

                    query = f'{query} {pr_key} as (SELECT {tm_query3} FROM {key}),'
                    key = pr_key
                elif qr['type'] == 'OUTPUT':
                    pr_key = qr['key']
                    limit = qr['transformObject']['limit']
                    offset = qr['transformObject']['offset']
                    query = f'{query} {pr_key} as (SELECT * FROM {key} limit {limit} offset {offset}) SELECT * FROM {pr_key}'
                else:
                    return Response({"msg": "Invalid column name"}, status=HTTP_400_BAD_REQUEST)

            obj = Users.objects.raw(query)
            ls = []
            for dt in obj:
                ls.append({'id': dt.id, 'name': dt.name, 'age': dt.age})
            ls.append({"query": query})

            return Response(ls, status=HTTP_200_OK)

        except Exception as msg:
            return Response({"msg": str(msg)}, status=HTTP_400_BAD_REQUEST)


class AddUser(viewsets.ModelViewSet):
    serializer_class = AddUserSerializers
    queryset = Users.objects.all()