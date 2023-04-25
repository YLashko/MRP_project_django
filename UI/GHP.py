from UI.MRP import MRP


class GHP:
    def __init__(self, name, prod_time: int = 1, level: int = 0, in_stock: int = 0,
                 timestamps: int = 1, demand_list: list[int] = None, production_list: list[int] = None,
                 children: list = None):
        self.name = name
        self.prod_time = prod_time
        self.level = level
        self.in_stock = in_stock
        self.timestamps = timestamps
        self.children: list[MRP] = []
        self.children_quan_multipliers = []
        self.net_demand_table = []
        self.production_table = []
        self.demand_table = []
        self.in_stock_table = []
        if demand_list and production_list:
            self.set_demand_table(demand_list)
            self.set_production_table(production_list)
        if children:
            for i in range(0, len(children), 2):
                self.add_child_MRP(children[i], children[i + 1])

    def setup_tables(self) -> None:
        self.net_demand_table = [0] * self.timestamps
        self.in_stock_table = [0] * self.timestamps
        self.in_stock_table[0] = self.in_stock

    def get_children(self):
        return self.children

    def add_child_MRP(self, mrp, multiplier: int):
        self.children.append(mrp)
        self.children_quan_multipliers.append(multiplier)

    def setup_children(self):
        for n, child in enumerate(self.children):
            child.set_demand_table(list(map(
                lambda x: x * self.children_quan_multipliers[n],
                self.order_table
            )))

    def add_demand(self, pos: int, n: int) -> None:
        try:
            self.demand_table[pos] = n
        except IndexError as e:
            print(f"An error occurred while adding demand for {self.name}: {e}")

    def add_production(self, pos: int, n: int) -> None:
        try:
            self.production_table[pos] = n
        except IndexError as e:
            print(f"An error occurred while adding production for {self.name}: {e}")

    def set_demand_table(self, demand_list: list[int]) -> None:
        self.demand_table = demand_list
        self.timestamps = max(self.timestamps, len(demand_list))

    def set_production_table(self, production_list: list[int]) -> None:
        self.production_table = production_list
        self.timestamps = max(self.timestamps, len(production_list))

    def compute_in_stock(self):
        for ts in range(1, self.timestamps):
            self.in_stock_table[ts] = self.in_stock_table[ts - 1] + self.production_table[ts] - \
                                                                    self.demand_table[ts]

    def compute_timestamps(self):
        self.compute_in_stock()

    @property
    def order_table(self):
        return [self.production_table[n] for n in range(self.prod_time, self.timestamps)]
