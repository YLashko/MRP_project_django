from UI.GHP import GHP
from UI.MRP import MRP
import csv
from UI.html_layout import layout


class MRPTree:
    def __init__(self):
        self.ghp: GHP = None

    def get_item(self, item: list[int]) -> MRP:
        root = self.ghp
        n = 0
        while len(item) > 0:
            try:
                n = item.pop(0)
                root = root.get_children()[n]
            except IndexError as e:
                print(f"Can't get child {n} of {root.name}: {e}")
        return root

    def calculate_all(self):
        self.calculate_recursive(self.ghp)

    def calculate_recursive(self, root: GHP | MRP):
        root.setup_tables()
        root.compute_timestamps()
        root.setup_children()
        for child in root.get_children():
            self.calculate_recursive(child)

    def get_tree(self):
        return list(self.get_tree_recursive(self.ghp, []))

    def get_tree_recursive(self, root, tree_list):
        tree_list += [root]
        for child in root.get_children():
            self.get_tree_recursive(child, tree_list)
        return tree_list

    def set_ghp(self, ghp: GHP):
        self.ghp = ghp

    def add_mrp(self, tree_coords: list[int], mrp: MRP, prod_multiplier: int):
        self.get_item(tree_coords).add_child_MRP(mrp, prod_multiplier)


def r0(list_: list):
    return [i if i != 0 else "" for i in list_]


class Convert:

    @staticmethod
    def ghp_to_rows(ghp):
        return [
            [ghp.name] + ["" for n in range(ghp.timestamps)],
            ["Okres"] + [str(n + 1) for n in range(ghp.timestamps)],
            ["Przewidywany popyt"] + r0(ghp.demand_table),
            ["Produkcja"] + r0(ghp.production_table),
            ["Dostępne"] + ghp.in_stock_table
        ]

    @staticmethod
    def mrp_to_rows(mrp):
        return [
            [mrp.name] + ["" for n in range(mrp.timestamps)],
            ["Okres"] + [str(n + 1) for n in range(mrp.timestamps)],
            ["Całkowite zapotrzebowanie"] + r0(mrp.demand_table),
            ["Planowane przyjęcia"] + r0(mrp.intake_table),
            ["Przewidywane na stanie"] + mrp.in_stock_table,
            ["Zapotrzebowanie netto"] + [abs(el) for el in mrp.net_demand_table],
            ["Planowane zamówienia"] + r0(mrp.planned_orders_table),
            ["Planowane przyjęcie zamówień"] + r0(mrp.orders_intake_table)
        ]

    @staticmethod
    def json_to_tree(json_data: dict) -> MRPTree:

        def json_to_tree_recursive(element: MRP | GHP, json_data: list):
            for json_element in json_data:
                element.add_child_MRP(new_element := MRP(
                    name=json_element["name"],
                    prod_time=int(json_element["prod_time"]),
                    batch_size=int(json_element["batch_size"]),
                    in_stock=int(json_element["in_stock"]),
                    level=0,
                    intake_list=[float(i) if i != "" else 0 for i in json_element["intake_table"]]
                ), float(json_element["prod_multiplier"]))
                json_to_tree_recursive(new_element, json_element["children"])

        ghp = GHP(
            name=json_data["name"],
            prod_time=int(json_data["prod_time"]),
            level=0,
            in_stock=int(json_data["in_stock"]),
            demand_list=[float(i) if i != "" else 0 for i in json_data["demand_table"]],
            production_list=[float(i) if i != "" else 0 for i in json_data["prod_table"]],
        )
        json_to_tree_recursive(ghp, json_data["children"])
        tree = MRPTree()
        tree.set_ghp(ghp)
        return tree


class Save:
    @staticmethod
    def to_csv(tree: MRPTree, filename):
        csv_list = []
        for element in tree.get_tree():
            if isinstance(element, GHP):
                csv_list += Convert.ghp_to_rows(element)
            elif isinstance(element, MRP):
                csv_list += Convert.mrp_to_rows(element)
        with open(filename, "w", encoding="utf-8", newline='') as f:
            csv.writer(f).writerows(csv_list)

    @staticmethod
    def to_html_table(tree: MRPTree, filename=None, ret=False):
        table = "<table>"
        element_rows = []
        for element in tree.get_tree():
            max_rows = 0
            if isinstance(element, GHP):
                element_rows = Convert.ghp_to_rows(element)
            elif isinstance(element, MRP):
                element_rows = Convert.mrp_to_rows(element)
            for row in element_rows:
                max_rows = max(max_rows, len(row))
                table += "<tr>"
                for cell in row:
                    table += f"<td>{cell}</td>"
                table += "</tr>"
            table += "<tr>" + "<th>----</th>" * max_rows + "</tr>"
        table += "</table>"
        if ret:
            return layout(table)
        with open(filename, "w", encoding='utf-8') as file:
            file.write(layout(table))
