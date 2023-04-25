class MRP:
    def __init__(self, name, prod_time: int = 1, level: int = 0, batch_size: int = 0, in_stock: int = 0,
                 timestamps: int = 1, backprop_ordering: bool = True, children: list = None, intake_list: list = None):
        self.name = name
        self.prod_time = prod_time
        self.level = level
        self.batch_size = batch_size
        self.in_stock = in_stock
        self.timestamps = timestamps
        self.backprop_ordering = backprop_ordering  # does nothing, TODO
        self.demand_table = []
        self.children: list[MRP] = []
        self.children_quan_multipliers = []
        self.orders_intake_table = []
        self.planned_orders_table = []
        self.net_demand_table = []
        self.intake_table = []
        self.in_stock_table = []
        if children:
            for i in range(0, len(children), 2):
                self.add_child_MRP(children[i], children[i + 1])
        if intake_list:
            self.intake_table = intake_list

    def setup_tables(self) -> None:
        self.in_stock_table = [0] * self.timestamps
        if len(self.intake_table) == 0:
            self.intake_table = [0] * self.timestamps
        self.net_demand_table = [0] * self.timestamps
        self.planned_orders_table = [0] * self.timestamps
        self.orders_intake_table = [0] * self.timestamps
        self.in_stock_table[0] = self.in_stock

    def compute_timestamps(self) -> None:
        for ts in range(self.timestamps):
            # compute current in_stock amount
            self.net_demand_table[ts] = min(self.in_stock_table[ts] - self.demand_table[ts] +
                                            self.intake_table[ts], 0)
            self.in_stock_table[ts] -= self.demand_table[ts] - self.intake_table[ts]

            # order more if necessary
            if self.net_demand_table[ts] < 0:
                self.order_backprop(ts, self.net_demand_table[ts])

            # set in_stock amount for the next timestamp
            if ts < self.timestamps - 1:
                self.in_stock_table[ts + 1] = self.in_stock_table[ts]

    def order_backprop(self, ts, net_demand):
        diff = 0
        # current iteration orders
        backprop_buffer = []
        # backprop until total ordered is bigger than net demand
        for n in range(ts, -2, -1):
            # if reached the beginning or ordered enough
            if diff >= -net_demand or (n - self.prod_time) <= -1:
                # only happens when it's not possible to produce enough in time
                if len(backprop_buffer) == 0:
                    return
                # add ordered materials to in_stock
                orders = 0
                for index in range(backprop_buffer[-1], backprop_buffer[0] + 1):
                    if index in backprop_buffer:
                        orders += 1
                    self.in_stock_table[index] += self.batch_size * orders
                break
            # if there is already an order on this timestamp, skip
            if self.orders_intake_table[n] != 0:
                continue
            self.planned_orders_table[n - self.prod_time] = self.batch_size
            self.orders_intake_table[n] = self.batch_size
            diff += self.batch_size
            backprop_buffer.append(n)

    def setup_children(self):
        for n, child in enumerate(self.children):
            child.set_demand_table(list(map(
                lambda x: x * self.children_quan_multipliers[n],
                self.planned_orders_table
            )))

    def get_children(self):
        return self.children

    def add_child_MRP(self, mrp, multiplier: float | int):
        self.children.append(mrp)
        self.children_quan_multipliers.append(multiplier)

    def add_demand(self, pos: int, n: int) -> None:
        try:
            self.demand_table[pos] = n
        except IndexError as e:
            print(f"An error occurred while adding demand for {self.name}: {e}")

    def add_intake(self, pos: int, n: int) -> None:
        try:
            self.intake_table[pos] = n
        except IndexError as e:
            print(f"An error occurred while adding intake for {self.name}: {e}")

    def set_demand_table(self, demand_list: list[int]) -> None:
        self.demand_table = demand_list
        self.timestamps = max(self.timestamps, len(demand_list))
