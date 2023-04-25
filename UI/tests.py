from GHP import GHP
from MRP import MRP
from Tree import MRPTree, Save, Convert
import json


def test_zad1():
    stol = GHP(
        name="Stół",
        prod_time=1,
        in_stock=2
    )
    blaty = MRP(
        name="Blaty",
        prod_time=3,
        level=1,
        batch_size=40,
        in_stock=22
    )
    plyta = MRP(
        name="Plyta",
        prod_time=1,
        level=2,
        batch_size=50,
        in_stock=10
    )
    nogi = MRP(
        name="Nogi",
        prod_time=2,
        level=1,
        batch_size=120,
        in_stock=40
    )
    stol.set_demand_table([0, 0, 0, 0, 20, 0, 40, 0, 10, 0])
    stol.setup_tables()
    stol.set_production_table([0, 0, 0, 0, 28, 0, 30, 0, 0, 0])
    stol.compute_in_stock()
    stol.add_child_MRP(blaty, 1)
    stol.add_child_MRP(nogi, 4)
    blaty.add_child_MRP(plyta, 1)
    stol.setup_children()
    blaty.setup_tables()
    nogi.setup_tables()
    blaty.compute_timestamps()
    nogi.compute_timestamps()
    blaty.setup_children()
    plyta.setup_tables()
    plyta.compute_timestamps()
    print_mrp(blaty)
    print_mrp(nogi)
    print_mrp(plyta)


def test_proj():
    tree = MRPTree()
    tree.set_ghp(
        GHP(
            name="Napój",
            prod_time=1,
            in_stock=250,
            demand_list=[0, 0, 0, 0, 500, 0, 0, 0, 1500, 0],
            production_list=[0, 0, 0, 0, 750, 0, 0, 1500, 0, 0],
            children=[
                MRP(
                    name="Butelka",
                    prod_time=2,
                    level=1,
                    batch_size=500,
                    in_stock=150,
                    children=[
                        MRP(
                            name="Plastik (kg)",
                            prod_time=1,
                            level=2,
                            batch_size=100,
                            in_stock=50
                        ), 0.05
                    ]
                ), 1,
                MRP(
                    name="Nakrętka",
                    prod_time=1,
                    level=1,
                    batch_size=500,
                    in_stock=50
                ), 1,
                MRP(
                    name="Ciecz (l)",
                    prod_time=1,
                    level=1,
                    batch_size=1000,
                    in_stock=0,
                    children=[
                        MRP(
                            name="Cukier (kg)",
                            prod_time=1,
                            level=2,
                            batch_size=150,
                            in_stock=0
                        ), 0.1,
                        MRP(
                            name="Gaz (m3)",
                            prod_time=1,
                            level=2,
                            batch_size=300,
                            in_stock=1,
                        ), 0.25,
                        MRP(
                            name="Woda (l)",
                            prod_time=1,
                            level=2,
                            batch_size=1500,
                            in_stock=600
                        ), 1,
                        MRP(
                            name="Aromaty (kg)",
                            prod_time=2,
                            level=2,
                            batch_size=20,
                            in_stock=6
                        ), 0.02
                    ]
                ), 1
            ]
        )
    )
    tree.calculate_all()
    Save.to_csv(tree, "test.csv")
    Save.to_html_table(tree, "test.html")


def test_json():
    with open("../../../Desktop/MRP_project-master/test.json", "r", encoding="utf-8") as json_data:
        data = json.loads(json_data.read())
    tree = Convert.json_to_tree(data)
    tree.calculate_all()
    Save.to_csv(tree, "test_json.csv")
    Save.to_html_table(tree, "test_json.html")


def print_mrp(mrp):
    print(mrp.name)
    print(mrp.demand_table)
    print(mrp.in_stock_table)
    print(mrp.net_demand_table)
    print(mrp.planned_orders_table)
    print(mrp.orders_intake_table)
