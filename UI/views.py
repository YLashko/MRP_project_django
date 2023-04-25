import json

from django.shortcuts import render
from django.http import HttpResponse

from UI.Tree import Convert, Save

from pprint import pprint


def main_page(request):
    return render(request, "index.html", {})


def saved(request):
    return render(request, "saved.html", {})


def calculate(request):
    data = json.loads(list(request.GET.dict().keys())[0])
    pprint(data)
    tree = Convert.json_to_tree(data)
    tree.calculate_all()
    table = Save.to_html_table(tree, ret=True)
    return HttpResponse(table)
